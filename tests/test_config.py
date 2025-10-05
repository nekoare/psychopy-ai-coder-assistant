"""
Tests for configuration management
"""

import unittest
import tempfile
import os
from pathlib import Path
from src.psychopy_ai_coder_assistant.config import ConfigManager


class TestConfigManager(unittest.TestCase):
    """Test cases for configuration management."""
    
    def setUp(self):
        """Set up test fixtures with temporary config directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_manager = ConfigManager()
        # Override config directory for testing
        self.config_manager.config_dir = Path(self.temp_dir) / 'ai_assistant'
        self.config_manager.config_file = self.config_manager.config_dir / 'config.json'
        self.config_manager.config_dir.mkdir(parents=True, exist_ok=True)
        
    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_default_config(self):
        """Test default configuration values."""
        config = self.config_manager._get_default_config()
        
        self.assertEqual(config['api_provider'], 'openai')
        self.assertIn('api_keys', config)
        self.assertIn('analysis_features', config)
        self.assertTrue(config['show_privacy_warning'])
        
    def test_get_set_config_values(self):
        """Test getting and setting configuration values."""
        # Test simple value
        self.config_manager.set('api_provider', 'anthropic')
        self.assertEqual(self.config_manager.get('api_provider'), 'anthropic')
        
        # Test nested value
        self.config_manager.set('analysis_features.builder_mapping', False)
        self.assertFalse(self.config_manager.get('analysis_features.builder_mapping'))
        
        # Test default value
        self.assertEqual(self.config_manager.get('nonexistent_key', 'default'), 'default')
        
    def test_api_key_management(self):
        """Test API key storage and retrieval."""
        # Set API key
        self.config_manager.set_api_key('openai', 'sk-test-key-123')
        
        # Retrieve API key
        retrieved_key = self.config_manager.get_api_key('openai')
        self.assertEqual(retrieved_key, 'sk-test-key-123')
        
        # Test non-existent key
        self.assertIsNone(self.config_manager.get_api_key('nonexistent'))
        
    def test_configuration_persistence(self):
        """Test that configuration persists across instances."""
        # Set some values
        self.config_manager.set('api_provider', 'google')
        self.config_manager.set_api_key('google', 'test-key')
        
        # Create new instance with same config file
        new_config_manager = ConfigManager()
        new_config_manager.config_dir = self.config_manager.config_dir
        new_config_manager.config_file = self.config_manager.config_file
        new_config_manager._config = new_config_manager._load_config()
        
        # Values should persist
        self.assertEqual(new_config_manager.get('api_provider'), 'google')
        self.assertEqual(new_config_manager.get_api_key('google'), 'test-key')
        
    def test_is_configured(self):
        """Test configuration validation."""
        # Initially not configured
        self.assertFalse(self.config_manager.is_configured())
        
        # Set provider and key
        self.config_manager.set('api_provider', 'openai')
        self.config_manager.set_api_key('openai', 'sk-valid-key-123')
        
        # Should now be configured
        self.assertTrue(self.config_manager.is_configured())
        
        # Empty key should not be considered configured
        self.config_manager.set_api_key('openai', '   ')
        self.assertFalse(self.config_manager.is_configured())
        
    def test_enabled_features(self):
        """Test enabled features management."""
        features = self.config_manager.get_enabled_features()
        
        # Should have default features
        self.assertIn('builder_mapping', features)
        self.assertIn('performance_optimization', features)
        self.assertIn('best_practices', features)
        
        # Modify feature
        self.config_manager.set('analysis_features.builder_mapping', False)
        updated_features = self.config_manager.get_enabled_features()
        self.assertFalse(updated_features['builder_mapping'])
        
    def test_reset_to_defaults(self):
        """Test resetting configuration to defaults."""
        # Modify some values
        self.config_manager.set('api_provider', 'custom')
        self.config_manager.set_api_key('custom', 'custom-key')
        
        # Reset to defaults
        self.config_manager.reset_to_defaults()
        
        # Should be back to defaults
        self.assertEqual(self.config_manager.get('api_provider'), 'openai')
        self.assertIsNone(self.config_manager.get_api_key('custom'))
        
    def test_malformed_config_file(self):
        """Test handling of malformed configuration files."""
        # Write malformed JSON to config file
        with open(self.config_manager.config_file, 'w') as f:
            f.write('{"invalid": json}')
            
        # Should fall back to defaults
        config = self.config_manager._load_config()
        self.assertEqual(config['api_provider'], 'openai')
        
    def test_config_file_creation(self):
        """Test automatic config file creation."""
        # Remove config file if it exists
        if self.config_manager.config_file.exists():
            self.config_manager.config_file.unlink()
            
        # Set a value (should trigger save)
        self.config_manager.set('test_key', 'test_value')
        
        # Config file should be created
        self.assertTrue(self.config_manager.config_file.exists())
        
        # Content should be valid JSON
        with open(self.config_manager.config_file, 'r') as f:
            import json
            config_data = json.load(f)
            self.assertEqual(config_data['test_key'], 'test_value')


if __name__ == '__main__':
    unittest.main()