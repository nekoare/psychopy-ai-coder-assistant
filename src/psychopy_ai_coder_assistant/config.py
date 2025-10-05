"""
Configuration management for AI Coder Assistant
"""

import os
import json
from typing import Any, Dict, Optional
from pathlib import Path


class ConfigManager:
    """Manages configuration settings for the AI Assistant."""
    
    def __init__(self):
        self.config_dir = Path.home() / '.psychopy' / 'ai_assistant'
        self.config_file = self.config_dir / 'config.json'
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self._config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self._get_default_config()
        
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'api_provider': 'openai',  # openai, anthropic, google
            'api_keys': {},
            'show_privacy_warning': True,
            'analysis_features': {
                'builder_mapping': True,
                'performance_optimization': True,
                'best_practices': True
            },
            'ui_preferences': {
                'panel_width': 300,
                'auto_analyze': False
            }
        }
        
    def save(self) -> None:
        """Save configuration to file."""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config, f, indent=2)
        except IOError as e:
            print(f"Failed to save config: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self._config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
                
        return value
        
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        keys = key.split('.')
        config = self._config
        
        # Navigate to the parent dict
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
            
        # Set the value
        config[keys[-1]] = value
        self.save()
        
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for specified provider."""
        return self.get(f'api_keys.{provider}')
        
    def set_api_key(self, provider: str, api_key: str) -> None:
        """Set API key for specified provider."""
        self.set(f'api_keys.{provider}', api_key)
        
    def is_configured(self) -> bool:
        """Check if API is properly configured."""
        provider = self.get('api_provider')
        api_key = self.get_api_key(provider)
        return provider and api_key and len(api_key.strip()) > 0
        
    def get_active_provider(self) -> str:
        """Get the currently active API provider."""
        return self.get('api_provider', 'openai')
        
    def get_enabled_features(self) -> Dict[str, bool]:
        """Get enabled analysis features."""
        return self.get('analysis_features', {})
        
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults."""
        self._config = self._get_default_config()
        self.save()