"""
Tests for pattern detection functionality
"""

import unittest
from src.psychopy_ai_coder_assistant.patterns import PsychoPyPatternDetector


class TestPsychoPyPatternDetector(unittest.TestCase):
    """Test cases for PsychoPy pattern detection."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.detector = PsychoPyPatternDetector()
        
    def test_detect_stimulus_in_loop(self):
        """Test detection of stimulus creation inside loops."""
        code = """
import psychopy.visual as visual
win = visual.Window()
for i in range(10):
    text = visual.TextStim(win, text="Hello")
    text.draw()
"""
        
        patterns = self.detector.detect_patterns(code)
        
        # Should detect TextStim creation in loop
        stim_patterns = [p for p in patterns if 'Stimulus creation in loop' in p['title']]
        self.assertGreater(len(stim_patterns), 0)
        self.assertEqual(stim_patterns[0]['category'], 'performance')
        
    def test_detect_trial_loops(self):
        """Test detection of trial loops."""
        code = """
import psychopy.visual as visual
import psychopy.event as event
win = visual.Window()
for trial in range(20):
    text = visual.TextStim(win, text="Press space")
    text.draw()
    win.flip()
    keys = event.waitKeys(['space'])
"""
        
        patterns = self.detector.detect_patterns(code)
        
        # Should detect trial loop pattern
        trial_patterns = [p for p in patterns if p['category'] == 'builder_mapping']
        self.assertGreater(len(trial_patterns), 0)
        
    def test_detect_magic_numbers(self):
        """Test detection of magic numbers."""
        code = """
if response.keys == 'space':
    print("Space pressed")
if color == 'red':
    print("Red stimulus")
"""
        
        patterns = self.detector.detect_patterns(code)
        
        # Should detect magic strings
        magic_patterns = [p for p in patterns if 'Magic' in p['title']]
        self.assertGreater(len(magic_patterns), 0)
        
    def test_detect_timing_issues(self):
        """Test detection of inefficient timing."""
        code = """
import time
for i in range(10):
    print(f"Trial {i}")
    time.sleep(1.0)
"""
        
        patterns = self.detector.detect_patterns(code)
        
        # Should detect time.sleep usage
        timing_patterns = [p for p in patterns if 'time.sleep' in p['title']]
        self.assertGreater(len(timing_patterns), 0)
        self.assertEqual(timing_patterns[0]['category'], 'performance')
        
    def test_detect_missing_cleanup(self):
        """Test detection of missing cleanup calls."""
        code = """
import psychopy.visual as visual
win = visual.Window()
# Do experiment stuff
# Missing win.close() and core.quit()
"""
        
        patterns = self.detector.detect_patterns(code)
        
        # Should detect missing cleanup
        cleanup_patterns = [p for p in patterns if 'cleanup' in p['title'] or 'close' in p['title']]
        self.assertGreater(len(cleanup_patterns), 0)
        
    def test_detect_resource_loading_in_loop(self):
        """Test detection of resource loading inside loops."""
        code = """
import psychopy.sound as sound
for trial in range(10):
    snd = sound.Sound('beep.wav')
    snd.play()
"""
        
        patterns = self.detector.detect_patterns(code)
        
        # Should detect sound loading in loop
        resource_patterns = [p for p in patterns if 'Sound loading' in p['title']]
        self.assertGreater(len(resource_patterns), 0)
        self.assertEqual(resource_patterns[0]['category'], 'performance')
        
    def test_no_patterns_in_good_code(self):
        """Test that well-written code produces fewer patterns."""
        code = """
import psychopy.visual as visual
import psychopy.core as core

# Constants
RESPONSE_KEY = 'space'
STIMULUS_COLOR = 'red'

# Setup
win = visual.Window()
text = visual.TextStim(win, color=STIMULUS_COLOR)

# Experiment loop
for trial in range(10):
    text.setText(f"Trial {trial}")
    text.draw()
    win.flip()
    core.wait(1.0)

# Cleanup
win.close()
core.quit()
"""
        
        patterns = self.detector.detect_patterns(code)
        
        # Good code should have fewer or no problematic patterns
        performance_issues = [p for p in patterns if p['category'] == 'performance']
        # May still detect the trial loop for Builder mapping, but fewer performance issues
        self.assertLess(len(performance_issues), 3)
        
    def test_invalid_syntax_handling(self):
        """Test handling of code with syntax errors."""
        code = """
import psychopy.visual
for i in range(10
    print(i)  # Syntax error
"""
        
        # Should not crash on syntax errors
        patterns = self.detector.detect_patterns(code)
        self.assertIsInstance(patterns, list)


if __name__ == '__main__':
    unittest.main()