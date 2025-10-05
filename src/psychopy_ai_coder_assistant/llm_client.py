"""
LLM API client with support for multiple providers
"""

import json
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
import requests

try:
    import openai
except ImportError:
    openai = None

try:
    import anthropic
except ImportError:
    anthropic = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    def analyze_code(self, code: str, prompt: str) -> Dict[str, Any]:
        """Analyze code with the given prompt."""
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is available."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4"):
        self.api_key = api_key
        self.model = model
        if openai:
            openai.api_key = api_key
            
    def is_available(self) -> bool:
        return openai is not None and self.api_key
        
    def analyze_code(self, code: str, prompt: str) -> Dict[str, Any]:
        if not self.is_available():
            raise RuntimeError("OpenAI provider not available")
            
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": code}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            # Try to parse as JSON, fallback to text response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"analysis": content, "suggestions": []}
                
        except Exception as e:
            raise RuntimeError(f"OpenAI API error: {str(e)}")


class AnthropicProvider(LLMProvider):
    """Anthropic Claude provider."""
    
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model
        if anthropic:
            self.client = anthropic.Anthropic(api_key=api_key)
            
    def is_available(self) -> bool:
        return anthropic is not None and self.api_key
        
    def analyze_code(self, code: str, prompt: str) -> Dict[str, Any]:
        if not self.is_available():
            raise RuntimeError("Anthropic provider not available")
            
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {"role": "user", "content": f"{prompt}\n\nCode to analyze:\n{code}"}
                ]
            )
            
            content = response.content[0].text
            
            # Try to parse as JSON, fallback to text response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"analysis": content, "suggestions": []}
                
        except Exception as e:
            raise RuntimeError(f"Anthropic API error: {str(e)}")


class GoogleProvider(LLMProvider):
    """Google Gemini provider."""
    
    def __init__(self, api_key: str, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model = model
        if genai:
            genai.configure(api_key=api_key)
            self.model_obj = genai.GenerativeModel(model)
            
    def is_available(self) -> bool:
        return genai is not None and self.api_key
        
    def analyze_code(self, code: str, prompt: str) -> Dict[str, Any]:
        if not self.is_available():
            raise RuntimeError("Google provider not available")
            
        try:
            full_prompt = f"{prompt}\n\nCode to analyze:\n{code}"
            response = self.model_obj.generate_content(full_prompt)
            
            content = response.text
            
            # Try to parse as JSON, fallback to text response
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                return {"analysis": content, "suggestions": []}
                
        except Exception as e:
            raise RuntimeError(f"Google API error: {str(e)}")


class LLMClient:
    """Main LLM client that manages multiple providers."""
    
    def __init__(self, config_manager):
        self.config_manager = config_manager
        self.providers: Dict[str, LLMProvider] = {}
        self._initialize_providers()
        
    def _initialize_providers(self) -> None:
        """Initialize available providers."""
        # OpenAI
        openai_key = self.config_manager.get_api_key('openai')
        if openai_key:
            self.providers['openai'] = OpenAIProvider(openai_key)
            
        # Anthropic
        anthropic_key = self.config_manager.get_api_key('anthropic')
        if anthropic_key:
            self.providers['anthropic'] = AnthropicProvider(anthropic_key)
            
        # Google
        google_key = self.config_manager.get_api_key('google')
        if google_key:
            self.providers['google'] = GoogleProvider(google_key)
            
    def get_active_provider(self) -> Optional[LLMProvider]:
        """Get the currently active provider."""
        provider_name = self.config_manager.get_active_provider()
        return self.providers.get(provider_name)
        
    def is_configured(self) -> bool:
        """Check if any provider is configured and available."""
        provider = self.get_active_provider()
        return provider is not None and provider.is_available()
        
    def analyze_code(self, code: str, prompt: str) -> Dict[str, Any]:
        """Analyze code using the active provider."""
        provider = self.get_active_provider()
        
        if not provider:
            raise RuntimeError("No LLM provider configured")
            
        if not provider.is_available():
            raise RuntimeError("Selected LLM provider is not available")
            
        return provider.analyze_code(code, prompt)
        
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names."""
        return [name for name, provider in self.providers.items() 
                if provider.is_available()]
        
    def refresh_providers(self) -> None:
        """Refresh provider configurations."""
        self.providers.clear()
        self._initialize_providers()