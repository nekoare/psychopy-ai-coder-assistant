"""
Example usage of the PsychoPy AI Coder Assistant

This example demonstrates how to use the AI assistant to analyze PsychoPy code
and get suggestions for improvements.
"""

# Example PsychoPy code that could benefit from AI analysis
psychopy_example_code = """
import psychopy.visual as visual
import psychopy.core as core
import psychopy.event as event
import time
import random

# Create window
win = visual.Window(size=(800, 600), fullscr=False)

# Experiment parameters
n_trials = 50
stimulus_duration = 2.0
response_key = 'space'

# Trial loop
for trial in range(n_trials):
    # Create stimuli for each trial (inefficient!)
    text_stim = visual.TextStim(win, text=f"Trial {trial + 1}")
    
    # Show stimulus
    text_stim.draw()
    win.flip()
    
    # Wait for response (inefficient timing!)
    time.sleep(stimulus_duration)
    
    # Collect response
    keys = event.getKeys([response_key])
    if keys:
        print(f"Response on trial {trial + 1}")
    
    # Random delay (should use constants!)
    delay = random.uniform(0.5, 1.5)
    time.sleep(delay)

# Missing cleanup!
"""

# Expected AI suggestions for this code:
expected_suggestions = {
    "builder_mapping": [
        "The trial loop (range(50)) could be implemented as a TrialHandler component",
        "Text stimulus presentation could use a TextStim component in Builder",
        "Response collection could use a Keyboard component"
    ],
    
    "performance_optimizations": [
        "Create TextStim outside the loop, update text inside",
        "Replace time.sleep() with core.wait() for better timing",
        "Pre-generate random delays to avoid computation during trials"
    ],
    
    "best_practices": [
        "Define constants for magic numbers (n_trials=50, response_key='space')",
        "Add proper window cleanup (win.close(), core.quit())",
        "Separate experiment configuration from execution logic"
    ]
}

# Improved version of the code based on AI suggestions
improved_code = """
import psychopy.visual as visual
import psychopy.core as core
import psychopy.event as event
import random

# Experiment constants
N_TRIALS = 50
STIMULUS_DURATION = 2.0
RESPONSE_KEY = 'space'
MIN_DELAY = 0.5
MAX_DELAY = 1.5

# Setup
win = visual.Window(size=(800, 600), fullscr=False)

# Create stimulus once (performance improvement)
text_stim = visual.TextStim(win, text="")

# Pre-generate delays (performance improvement)
trial_delays = [random.uniform(MIN_DELAY, MAX_DELAY) for _ in range(N_TRIALS)]

try:
    # Trial loop
    for trial in range(N_TRIALS):
        # Update stimulus text
        text_stim.setText(f"Trial {trial + 1}")
        
        # Show stimulus
        text_stim.draw()
        win.flip()
        
        # Wait for response (better timing)
        core.wait(STIMULUS_DURATION)
        
        # Collect response
        keys = event.getKeys([RESPONSE_KEY])
        if keys:
            print(f"Response on trial {trial + 1}")
        
        # Inter-trial delay
        core.wait(trial_delays[trial])

finally:
    # Proper cleanup (best practice)
    win.close()
    core.quit()
"""

if __name__ == "__main__":
    print("PsychoPy AI Coder Assistant Example")
    print("=" * 40)
    print("\nOriginal code issues:")
    print("- Stimulus created in loop (performance)")
    print("- Uses time.sleep() instead of core.wait() (timing)")
    print("- Magic numbers not defined as constants (maintainability)")
    print("- Missing proper cleanup (best practice)")
    print("- Could be simplified with Builder components")
    
    print("\nImproved code addresses:")
    print("- ✅ Stimulus created once, text updated in loop")
    print("- ✅ Uses core.wait() for precise timing")
    print("- ✅ Constants defined for configuration")
    print("- ✅ Proper try/finally cleanup")
    print("- ✅ Better separation of setup and execution")
    
    print(f"\nOriginal code length: {len(psychopy_example_code.split())} lines")
    print(f"Improved code length: {len(improved_code.split())} lines")
    print("Both achieve the same experimental goals with better performance and maintainability!")