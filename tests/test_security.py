"""
Tests for security and privacy functionality
"""

import unittest
from src.psychopy_ai_coder_assistant.security import CodeSanitizer, PrivacyManager, SecurityValidator
from src.psychopy_ai_coder_assistant.config import ConfigManager
from unittest.mock import Mock


class TestCodeSanitizer(unittest.TestCase):
    """Test cases for code sanitization."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.sanitizer = CodeSanitizer()
        
    def test_sanitize_api_keys(self):
        """Test sanitization of API keys."""
        code = """
api_key = "sk-1234567890abcdefghij1234567890abcdefghij"
openai.api_key = "sk-another-long-api-key-here"
"""
        
        sanitized, replacements = self.sanitizer.sanitize_code(code)
        
        self.assertNotIn("sk-1234567890", sanitized)
        self.assertNotIn("sk-another-long", sanitized)
        self.assertEqual(len(replacements), 2)
        self.assertEqual(replacements[0]['type'], 'API_KEY')
        
    def test_sanitize_database_urls(self):
        """Test sanitization of database URLs."""
        code = """
db_url = "postgresql://user:pass@localhost:5432/db"
mongo_url = "mongodb://user:pass@cluster.mongodb.net/database"
"""
        
        sanitized, replacements = self.sanitizer.sanitize_code(code)
        
        self.assertNotIn("postgresql://", sanitized)
        self.assertNotIn("mongodb://", sanitized)
        self.assertGreater(len(replacements), 0)
        
    def test_sanitize_file_paths(self):
        """Test sanitization of user file paths."""
        code = """
file_path = "/home/username/Documents/secret.txt"
win_path = "C:\\Users\\username\\data\\sensitive.csv"
"""
        
        sanitized, replacements = self.sanitizer.sanitize_code(code)
        
        self.assertNotIn("/home/username", sanitized)
        self.assertNotIn("C:\\Users\\username", sanitized)
        
    def test_sanitize_emails(self):
        """Test sanitization of email addresses."""
        code = """
contact = "researcher@university.edu"
email_list = ["user1@domain.com", "user2@domain.org"]
"""
        
        sanitized, replacements = self.sanitizer.sanitize_code(code)
        
        self.assertNotIn("researcher@university.edu", sanitized)
        self.assertNotIn("user1@domain.com", sanitized)
        
    def test_check_sensitive_content(self):
        """Test detection without modification."""
        code = """
api_key = "sk-1234567890abcdefghij"
email = "test@example.com"
"""
        
        detected = self.sanitizer.check_for_sensitive_content(code)
        
        self.assertGreater(len(detected), 0)
        api_detections = [d for d in detected if d['type'] == 'API_KEY']
        email_detections = [d for d in detected if d['type'] == 'EMAIL']
        
        self.assertEqual(len(api_detections), 1)
        self.assertEqual(len(email_detections), 1)
        
    def test_no_false_positives(self):
        """Test that normal code doesn't trigger false positives."""
        code = """
import psychopy.visual as visual
win = visual.Window()
text = visual.TextStim(win, text="Hello World")
text.draw()
win.flip()
"""
        
        sanitized, replacements = self.sanitizer.sanitize_code(code)
        
        self.assertEqual(len(replacements), 0)
        self.assertEqual(code, sanitized)


class TestPrivacyManager(unittest.TestCase):
    """Test cases for privacy management."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = Mock(spec=ConfigManager)
        self.privacy_manager = PrivacyManager(self.config_manager)
        
    def test_privacy_warning_settings(self):
        """Test privacy warning settings management."""
        # Test should show warning initially
        self.config_manager.get.return_value = True
        self.assertTrue(self.privacy_manager.should_show_privacy_warning())
        
        # Test acknowledging warning
        self.privacy_manager.privacy_warning_acknowledged()
        self.config_manager.set.assert_called_with('show_privacy_warning', False)
        
    def test_privacy_analysis_safe_code(self):
        """Test privacy analysis of safe code."""
        code = """
import psychopy.visual as visual
win = visual.Window()
text = visual.TextStim(win, text="Safe code")
"""
        
        analysis = self.privacy_manager.analyze_code_privacy(code)
        
        self.assertEqual(analysis['risk_score'], 1)
        self.assertTrue(analysis['safe_to_send'])
        self.assertEqual(len(analysis['sensitive_content']), 0)
        
    def test_privacy_analysis_risky_code(self):
        """Test privacy analysis of risky code."""
        code = """
api_key = "sk-1234567890abcdefghij1234567890abcdefghij"
db_url = "postgresql://user:pass@localhost/db"
"""
        
        analysis = self.privacy_manager.analyze_code_privacy(code)
        
        self.assertGreater(analysis['risk_score'], 3)
        self.assertFalse(analysis['safe_to_send'])
        self.assertGreater(len(analysis['sensitive_content']), 0)
        
    def test_privacy_recommendations(self):
        """Test privacy recommendations generation."""
        analysis = {
            'risk_score': 4,
            'sensitive_content': [
                {'type': 'API_KEY', 'content': 'sk-test'},
                {'type': 'EMAIL', 'content': 'test@example.com'}
            ]
        }
        
        recommendations = self.privacy_manager.get_privacy_recommendations(analysis)
        
        self.assertGreater(len(recommendations), 0)
        # Should include high risk warning
        high_risk_warnings = [r for r in recommendations if 'High privacy risk' in r]
        self.assertGreater(len(high_risk_warnings), 0)


class TestSecurityValidator(unittest.TestCase):
    """Test cases for security validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = SecurityValidator()
        
    def test_validate_https_endpoints(self):
        """Test HTTPS endpoint validation."""
        self.assertTrue(self.validator.validate_api_endpoint("https://api.openai.com"))
        self.assertFalse(self.validator.validate_api_endpoint("http://api.openai.com"))
        
    def test_validate_api_key_formats(self):
        """Test API key format validation."""
        # OpenAI keys
        self.assertTrue(self.validator.validate_api_key_format("openai", "sk-1234567890abcdefghij1234567890abcdefghij"))
        self.assertFalse(self.validator.validate_api_key_format("openai", "invalid-key"))
        
        # Anthropic keys
        self.assertTrue(self.validator.validate_api_key_format("anthropic", "sk-ant-1234567890abcdefghij1234567890abcdefghij"))
        self.assertFalse(self.validator.validate_api_key_format("anthropic", "sk-wrong-prefix"))
        
        # Google keys (more flexible format)
        self.assertTrue(self.validator.validate_api_key_format("google", "AIzaSyD1234567890abcdefghij1234567890"))
        self.assertFalse(self.validator.validate_api_key_format("google", "short"))
        
    def test_security_recommendations(self):
        """Test security recommendations."""
        recommendations = self.validator.get_security_recommendations()
        
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)
        
        # Should include key security points
        api_key_rec = any("API keys" in rec for rec in recommendations)
        https_rec = any("HTTPS" in rec for rec in recommendations)
        
        self.assertTrue(api_key_rec)
        self.assertTrue(https_rec)


if __name__ == '__main__':
    unittest.main()