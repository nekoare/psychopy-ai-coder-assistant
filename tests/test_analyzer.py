"""
Tests for code analyzer functionality
"""

import unittest
from unittest.mock import Mock, patch
from src.psychopy_ai_coder_assistant.analyzer import CodeAnalyzer, AnalysisResult, CodeSuggestion
from src.psychopy_ai_coder_assistant.config import ConfigManager


class TestCodeAnalyzer(unittest.TestCase):
    """Test cases for CodeAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config_manager = Mock(spec=ConfigManager)
        self.config_manager.get_enabled_features.return_value = {
            'builder_mapping': True,
            'performance_optimization': True,
            'best_practices': True
        }
        self.analyzer = CodeAnalyzer(self.config_manager)
        
    def test_analyze_valid_code(self):
        """Test analyzing valid PsychoPy code."""
        code = """
import psychopy.visual as visual
import psychopy.core as core

win = visual.Window()
for i in range(10):
    text = visual.TextStim(win, text=f"Trial {i}")
    text.draw()
    win.flip()
win.close()
"""
        
        # Mock LLM response
        mock_llm_result = {
            'summary': 'Simple trial loop with text stimuli',
            'builder_mapping': [{
                'original_code': 'for i in range(10):',
                'builder_equivalent': 'TrialHandler with nReps=10',
                'explanation': 'This loop could be implemented as a TrialHandler'
            }],
            'performance_optimizations': [{
                'issue': 'TextStim created in loop',
                'original_code': 'text = visual.TextStim(win, text=f"Trial {i}")',
                'improved_code': 'text = visual.TextStim(win); text.setText(f"Trial {i}")',
                'explanation': 'Create stimulus outside loop, update inside'
            }],
            'best_practices': []
        }
        
        with patch.object(self.analyzer, '_get_llm_analysis', return_value=mock_llm_result):
            result = self.analyzer.analyze_code(code)
            
        self.assertTrue(result.success)
        self.assertIsInstance(result.suggestions, list)
        self.assertGreater(len(result.suggestions), 0)
        
    def test_analyze_invalid_syntax(self):
        """Test analyzing code with syntax errors."""
        code = """
import psychopy.visual as visual
for i in range(10
    print(i)  # Missing closing parenthesis
"""
        
        result = self.analyzer.analyze_code(code)
        
        self.assertFalse(result.success)
        self.assertIn('Syntax error', result.error_message)
        
    def test_suggestion_prioritization(self):
        """Test that suggestions are properly prioritized."""
        suggestions = [
            CodeSuggestion('performance', 'Low priority', '', '', '', [], 1),
            CodeSuggestion('performance', 'High priority', '', '', '', [], 5),
            CodeSuggestion('best_practices', 'Medium priority', '', '', '', [], 3),
        ]
        
        filtered = self.analyzer._filter_and_prioritize(suggestions)
        
        # Should be sorted by priority (descending)
        self.assertEqual(filtered[0].priority, 5)
        self.assertEqual(filtered[1].priority, 3)
        self.assertEqual(filtered[2].priority, 1)
        
    def test_duplicate_filtering(self):
        """Test that duplicate suggestions are filtered out."""
        suggestions = [
            CodeSuggestion('performance', 'Title 1', '', 'same_code', '', [], 1),
            CodeSuggestion('performance', 'Title 2', '', 'same_code', '', [], 2),
            CodeSuggestion('best_practices', 'Title 3', '', 'different_code', '', [], 1),
        ]
        
        filtered = self.analyzer._filter_and_prioritize(suggestions)
        
        # Should remove duplicate based on category + original_code
        self.assertEqual(len(filtered), 2)
        
    @patch('threading.Thread')
    def test_async_analysis(self, mock_thread):
        """Test asynchronous code analysis."""
        code = "print('hello')"
        callback = Mock()
        
        self.analyzer.analyze_code_async(code, callback)
        
        # Verify thread was created and started
        mock_thread.assert_called_once()
        mock_thread.return_value.start.assert_called_once()


class TestAnalysisResult(unittest.TestCase):
    """Test cases for AnalysisResult dataclass."""
    
    def test_successful_result(self):
        """Test creating a successful analysis result."""
        suggestions = [
            CodeSuggestion('performance', 'Test', 'Description', 'old', 'new', [], 3)
        ]
        
        result = AnalysisResult(
            summary="Test analysis",
            suggestions=suggestions,
            success=True,
            analysis_time=1.5
        )
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.suggestions), 1)
        self.assertEqual(result.analysis_time, 1.5)
        self.assertIsNone(result.error_message)
        
    def test_failed_result(self):
        """Test creating a failed analysis result."""
        result = AnalysisResult(
            summary="Analysis failed",
            suggestions=[],
            success=False,
            error_message="API error"
        )
        
        self.assertFalse(result.success)
        self.assertEqual(len(result.suggestions), 0)
        self.assertEqual(result.error_message, "API error")


if __name__ == '__main__':
    unittest.main()