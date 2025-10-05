"""
Integration tests for the AI Coder Assistant
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from psychopy_ai_coder_assistant.plugin import AICoderAssistantPlugin
from psychopy_ai_coder_assistant.config import ConfigManager


class TestPluginIntegration(unittest.TestCase):
    """Integration tests for the main plugin."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock PsychoPy components
        self.mock_coder_frame = Mock()
        self.mock_coder_frame.menuBar = Mock()
        self.mock_coder_frame.toolbar = Mock()
        self.mock_coder_frame.mainSizer = Mock()
        self.mock_coder_frame.currentDoc = Mock()
        
        # Mock menu methods
        self.mock_coder_frame.menuBar.GetMenuCount.return_value = 0
        self.mock_coder_frame.menuBar.Append = Mock()
        
        # Mock toolbar methods
        self.mock_coder_frame.toolbar.AddSeparator = Mock()
        self.mock_coder_frame.toolbar.AddTool = Mock()
        self.mock_coder_frame.toolbar.Realize = Mock()
        
        # Mock document methods
        self.mock_coder_frame.currentDoc.GetText.return_value = "print('hello world')"
        
    @patch('psychopy_ai_coder_assistant.plugin.wx')
    def test_plugin_registration(self, mock_wx):
        """Test plugin registration with Coder frame."""
        # Mock wx components
        mock_wx.NewIdRef.return_value = 12345
        mock_wx.Menu.return_value = Mock()
        
        plugin = AICoderAssistantPlugin(self.mock_coder_frame)
        plugin.register()
        
        # Verify menu was modified
        self.assertTrue(self.mock_coder_frame.menuBar.Append.called)
        
        # Verify toolbar was modified
        self.assertTrue(self.mock_coder_frame.toolbar.AddTool.called)
        self.assertTrue(self.mock_coder_frame.toolbar.Realize.called)
        
    @patch('psychopy_ai_coder_assistant.plugin.wx')
    @patch('psychopy_ai_coder_assistant.plugin.AIAssistantPanel')
    def test_plugin_menu_actions(self, mock_panel, mock_wx):
        """Test plugin menu action handling."""
        # Setup mocks
        mock_wx.NewIdRef.return_value = 12345
        mock_wx.Menu.return_value = Mock()
        mock_wx.MessageBox = Mock()
        
        plugin = AICoderAssistantPlugin(self.mock_coder_frame)
        plugin.config_manager.is_configured = Mock(return_value=True)
        plugin.config_manager.get = Mock(return_value=False)  # Don't show privacy warning
        
        # Mock the assistant panel
        mock_panel_instance = Mock()
        mock_panel.return_value = mock_panel_instance
        
        plugin.register()
        
        # Test AI review action
        mock_event = Mock()
        plugin.on_ai_review(mock_event)
        
        # Should analyze code
        mock_panel_instance.analyze_code.assert_called_once()
        
    @patch('psychopy_ai_coder_assistant.plugin.wx')
    def test_plugin_unconfigured_api(self, mock_wx):
        """Test plugin behavior when API is not configured."""
        mock_wx.NewIdRef.return_value = 12345
        mock_wx.MessageBox = Mock()
        
        plugin = AICoderAssistantPlugin(self.mock_coder_frame)
        plugin.config_manager.is_configured = Mock(return_value=False)
        plugin.register()
        
        # Test AI review action when not configured
        mock_event = Mock()
        plugin.on_ai_review(mock_event)
        
        # Should show configuration message
        mock_wx.MessageBox.assert_called_once()
        
    @patch('psychopy_ai_coder_assistant.plugin.wx')
    def test_plugin_privacy_warning(self, mock_wx):
        """Test privacy warning display."""
        mock_wx.NewIdRef.return_value = 12345
        mock_wx.MessageBox = Mock(return_value=mock_wx.YES)
        mock_wx.YES = 'YES'
        
        plugin = AICoderAssistantPlugin(self.mock_coder_frame)
        plugin.config_manager.is_configured = Mock(return_value=True)
        plugin.config_manager.get = Mock(return_value=True)  # Show privacy warning
        plugin.config_manager.set = Mock()
        
        # Mock the assistant panel
        with patch('psychopy_ai_coder_assistant.plugin.AIAssistantPanel') as mock_panel:
            mock_panel_instance = Mock()
            mock_panel.return_value = mock_panel_instance
            
            plugin.register()
            
            # Test AI review action
            mock_event = Mock()
            plugin.on_ai_review(mock_event)
            
            # Should show privacy warning
            privacy_calls = [call for call in mock_wx.MessageBox.call_args_list 
                           if 'Privacy Warning' in str(call)]
            self.assertGreater(len(privacy_calls), 0)
            
            # Should set privacy warning acknowledged
            plugin.config_manager.set.assert_called_with('show_privacy_warning', False)


class TestEndToEndWorkflow(unittest.TestCase):
    """End-to-end workflow tests."""
    
    @patch('psychopy_ai_coder_assistant.llm_client.openai')
    def test_full_analysis_workflow(self, mock_openai):
        """Test complete analysis workflow from code to suggestions."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = '''
        {
            "summary": "Simple PsychoPy script with performance issues",
            "builder_mapping": [{
                "original_code": "for i in range(10):",
                "builder_equivalent": "TrialHandler with nReps=10",
                "explanation": "This loop could be a TrialHandler"
            }],
            "performance_optimizations": [{
                "issue": "Stimulus creation in loop",
                "original_code": "text = visual.TextStim(win, text=str(i))",
                "improved_code": "text = visual.TextStim(win); text.setText(str(i))",
                "explanation": "Create stimulus outside loop"
            }],
            "best_practices": []
        }
        '''
        mock_openai.ChatCompletion.create.return_value = mock_response
        mock_openai.api_key = "test-key"
        
        # Test code with known patterns
        test_code = """
import psychopy.visual as visual
win = visual.Window()
for i in range(10):
    text = visual.TextStim(win, text=str(i))
    text.draw()
    win.flip()
"""
        
        # Create analyzer with mocked config
        from psychopy_ai_coder_assistant.analyzer import CodeAnalyzer
        from psychopy_ai_coder_assistant.config import ConfigManager
        
        config_manager = Mock(spec=ConfigManager)
        config_manager.get_enabled_features.return_value = {
            'builder_mapping': True,
            'performance_optimization': True,
            'best_practices': True
        }
        config_manager.get_active_provider.return_value = 'openai'
        config_manager.get_api_key.return_value = 'sk-test-key'
        
        analyzer = CodeAnalyzer(config_manager)
        
        # Analyze the code
        result = analyzer.analyze_code(test_code)
        
        # Verify results
        self.assertTrue(result.success)
        self.assertGreater(len(result.suggestions), 0)
        
        # Check for expected suggestion types
        categories = {s.category for s in result.suggestions}
        self.assertIn('performance', categories)
        
    def test_pattern_detection_only(self):
        """Test analysis with pattern detection only (no LLM)."""
        from psychopy_ai_coder_assistant.analyzer import CodeAnalyzer
        from psychopy_ai_coder_assistant.config import ConfigManager
        
        # Create analyzer with unconfigured LLM
        config_manager = Mock(spec=ConfigManager)
        config_manager.get_enabled_features.return_value = {
            'builder_mapping': True,
            'performance_optimization': True,
            'best_practices': True
        }
        config_manager.get_active_provider.return_value = 'openai'
        config_manager.get_api_key.return_value = None  # No API key
        
        analyzer = CodeAnalyzer(config_manager)
        
        # Test code with detectable patterns
        test_code = """
import psychopy.visual as visual
import time
win = visual.Window()
for i in range(10):
    text = visual.TextStim(win, text="Hello")
    text.draw()
    win.flip()
    time.sleep(1.0)
"""
        
        result = analyzer.analyze_code(test_code)
        
        # Should succeed with local patterns only
        self.assertTrue(result.success)
        self.assertGreater(len(result.suggestions), 0)
        
        # Should detect stimulus in loop and timing issues
        performance_suggestions = [s for s in result.suggestions if s.category == 'performance']
        self.assertGreater(len(performance_suggestions), 0)


if __name__ == '__main__':
    unittest.main()