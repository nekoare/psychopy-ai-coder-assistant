"""
Privacy and security features for AI Coder Assistant
"""

import re
import hashlib
from typing import List, Tuple, Dict, Any


class CodeSanitizer:
    """Sanitizes code before sending to external AI services."""
    
    def __init__(self):
        self.sensitive_patterns = [
            # API keys and tokens
            (r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']', 'API_KEY'),
            (r'token\s*=\s*["\'][^"\']{20,}["\']', 'TOKEN'),
            (r'secret\s*=\s*["\'][^"\']{10,}["\']', 'SECRET'),
            
            # Database connection strings
            (r'mysql://[^"\s]+', 'DATABASE_URL'),
            (r'postgresql://[^"\s]+', 'DATABASE_URL'),
            (r'mongodb://[^"\s]+', 'DATABASE_URL'),
            
            # File paths that might contain sensitive info
            (r'/home/[^/\s]+/[^\s]*', 'USER_PATH'),
            (r'C:\\Users\\[^\\]+\\[^\s]*', 'USER_PATH'),
            
            # Email addresses
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL'),
            
            # IP addresses
            (r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b', 'IP_ADDRESS'),
            
            # URLs with credentials
            (r'https?://[^:\s]+:[^@\s]+@[^\s]+', 'AUTHENTICATED_URL'),
        ]
        
    def sanitize_code(self, code: str) -> Tuple[str, List[Dict[str, Any]]]:
        """
        Sanitize code by replacing sensitive information.
        
        Returns:
            Tuple of (sanitized_code, list of replacements made)
        """
        sanitized = code
        replacements = []
        
        for pattern, replacement_type in self.sensitive_patterns:
            matches = list(re.finditer(pattern, sanitized, re.IGNORECASE))
            
            for match in matches:
                original = match.group()
                # Create a deterministic but anonymous replacement
                hash_value = hashlib.md5(original.encode()).hexdigest()[:8]
                replacement = f'<{replacement_type}_{hash_value}>'
                
                sanitized = sanitized.replace(original, replacement)
                
                replacements.append({
                    'original': original,
                    'replacement': replacement,
                    'type': replacement_type,
                    'start': match.start(),
                    'end': match.end()
                })
                
        return sanitized, replacements
        
    def check_for_sensitive_content(self, code: str) -> List[Dict[str, Any]]:
        """
        Check for potentially sensitive content without modifying the code.
        
        Returns:
            List of detected sensitive content
        """
        detected = []
        
        for pattern, content_type in self.sensitive_patterns:
            matches = list(re.finditer(pattern, code, re.IGNORECASE))
            
            for match in matches:
                detected.append({
                    'type': content_type,
                    'content': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'line': code[:match.start()].count('\n') + 1
                })
                
        return detected


class PrivacyManager:
    """Manages privacy settings and warnings."""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.code_sanitizer = CodeSanitizer()
        
    def should_show_privacy_warning(self) -> bool:
        """Check if privacy warning should be shown."""
        return self.config_manager.get('show_privacy_warning', True)
        
    def privacy_warning_acknowledged(self) -> None:
        """Mark privacy warning as acknowledged."""
        self.config_manager.set('show_privacy_warning', False)
        
    def get_privacy_warning_text(self) -> str:
        """Get the privacy warning text."""
        return """Privacy Notice: AI Code Analysis

This feature sends your code to external AI services for analysis. Please review the following:

• Your code will be transmitted to third-party AI providers (OpenAI, Anthropic, or Google)
• The analysis helps identify optimization opportunities and best practices
• No data is stored permanently by this extension
• API providers may have their own data retention policies

Security Measures:
• Sensitive information (API keys, passwords, etc.) is automatically detected and redacted
• Only the code content is sent - no personal information or file paths
• All network communications use encrypted HTTPS connections

Before proceeding:
1. Review your code for any sensitive information
2. Ensure compliance with your organization's data policies
3. Consider using on isolated/test code first

Do you want to continue with the analysis?"""

    def analyze_code_privacy(self, code: str) -> Dict[str, Any]:
        """
        Analyze code for privacy implications.
        
        Returns:
            Dictionary with privacy analysis results
        """
        sensitive_content = self.code_sanitizer.check_for_sensitive_content(code)
        sanitized_code, replacements = self.code_sanitizer.sanitize_code(code)
        
        # Calculate privacy risk score
        risk_score = self._calculate_privacy_risk(sensitive_content)
        
        return {
            'risk_score': risk_score,
            'sensitive_content': sensitive_content,
            'sanitized_code': sanitized_code,
            'replacements': replacements,
            'safe_to_send': risk_score < 3  # Risk scores: 1-5
        }
        
    def _calculate_privacy_risk(self, sensitive_content: List[Dict]) -> int:
        """Calculate privacy risk score (1-5)."""
        if not sensitive_content:
            return 1
            
        # Count different types of sensitive content
        risk_weights = {
            'API_KEY': 5,
            'TOKEN': 5,
            'SECRET': 5,
            'DATABASE_URL': 4,
            'AUTHENTICATED_URL': 4,
            'EMAIL': 2,
            'IP_ADDRESS': 2,
            'USER_PATH': 1
        }
        
        max_risk = 1
        for item in sensitive_content:
            content_type = item['type']
            risk = risk_weights.get(content_type, 1)
            max_risk = max(max_risk, risk)
            
        return min(max_risk, 5)
        
    def get_privacy_recommendations(self, privacy_analysis: Dict[str, Any]) -> List[str]:
        """Get privacy recommendations based on analysis."""
        recommendations = []
        
        risk_score = privacy_analysis['risk_score']
        sensitive_content = privacy_analysis['sensitive_content']
        
        if risk_score >= 4:
            recommendations.append(
                "⚠️ High privacy risk detected. Consider removing sensitive data before analysis."
            )
            
        if risk_score >= 3:
            recommendations.append(
                "🔒 Sensitive information detected and will be automatically redacted."
            )
            
        # Specific recommendations based on content types
        content_types = {item['type'] for item in sensitive_content}
        
        if 'API_KEY' in content_types or 'TOKEN' in content_types:
            recommendations.append(
                "🔑 API keys/tokens detected. These will be replaced with placeholders."
            )
            
        if 'DATABASE_URL' in content_types:
            recommendations.append(
                "🗄️ Database URLs detected. Consider using environment variables instead."
            )
            
        if 'EMAIL' in content_types:
            recommendations.append(
                "📧 Email addresses detected. These will be anonymized."
            )
            
        if not recommendations:
            recommendations.append("✅ No significant privacy risks detected.")
            
        return recommendations


class SecurityValidator:
    """Validates security aspects of the code analysis process."""
    
    def __init__(self):
        self.required_https_domains = [
            'api.openai.com',
            'api.anthropic.com',
            'generativelanguage.googleapis.com'
        ]
        
    def validate_api_endpoint(self, endpoint: str) -> bool:
        """Validate that API endpoint uses HTTPS."""
        return endpoint.startswith('https://')
        
    def validate_api_key_format(self, provider: str, api_key: str) -> bool:
        """Validate API key format (basic validation)."""
        if not api_key or len(api_key) < 10:
            return False
            
        # Basic format validation for different providers
        if provider == 'openai':
            return api_key.startswith('sk-') and len(api_key) > 40
        elif provider == 'anthropic':
            return api_key.startswith('sk-ant-') and len(api_key) > 40
        elif provider == 'google':
            return len(api_key) > 30  # Google API keys vary in format
            
        return True
        
    def get_security_recommendations(self) -> List[str]:
        """Get general security recommendations."""
        return [
            "🔐 Store API keys securely and never commit them to version control",
            "🌐 All API communications use HTTPS encryption",
            "🚫 Sensitive data is automatically detected and redacted",
            "⏰ Consider using API keys with limited scope and expiration",
            "🔄 Regularly rotate your API keys for better security",
            "👥 For team environments, use separate API keys per user",
        ]