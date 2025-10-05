"""
Prompt engineering templates for PsychoPy code analysis
"""

from typing import Dict, Any, List


class PromptTemplates:
    """Container for prompt templates used in code analysis."""
    
    @staticmethod
    def get_base_context() -> str:
        """Get base context about PsychoPy for all prompts."""
        return """You are an expert in PsychoPy, a Python library for creating psychology experiments.

PsychoPy has two main interfaces:
1. Builder: Visual interface with components like TrialHandler, TextStim, ImageStim, etc.
2. Coder: Python scripting interface for more complex experiments

Key PsychoPy concepts:
- Stimuli: Visual, auditory, or other sensory components (TextStim, ImageStim, SoundStim)
- TrialHandler: Manages trial sequences and data collection
- Clock: For precise timing (core.Clock, core.CountdownTimer)
- Window: The main display surface
- Event handling: Keyboard, mouse input (event.getKeys, mouse.Mouse)
- Data collection: ExperimentHandler, TrialHandler for saving results

Common performance patterns:
- Create stimuli OUTSIDE loops, update properties INSIDE loops
- Use numpy arrays for vectorized operations
- Pre-load images/sounds before trials start
- Use frame-based timing for animations

Best practices:
- Define constants for magic numbers (keys, colors, positions)
- Separate stimulus creation from trial logic
- Use appropriate timing methods (frames vs. seconds)
- Proper resource cleanup (win.close(), core.quit())"""

    @staticmethod
    def get_analysis_prompt() -> str:
        """Get the main code analysis prompt."""
        base_context = PromptTemplates.get_base_context()
        
        return f"""{base_context}

Analyze the provided PsychoPy code and provide suggestions in the following JSON format:

{{
    "summary": "Brief description of what the code does",
    "builder_mapping": [
        {{
            "original_code": "specific code snippet",
            "description": "what this code does",
            "builder_equivalent": "suggested Builder component(s)",
            "explanation": "why this mapping makes sense"
        }}
    ],
    "performance_optimizations": [
        {{
            "issue": "description of performance issue",
            "original_code": "problematic code snippet",
            "improved_code": "optimized version",
            "explanation": "why this is better"
        }}
    ],
    "best_practices": [
        {{
            "issue": "description of best practice violation",
            "original_code": "problematic code snippet",
            "improved_code": "improved version",
            "explanation": "why this follows best practices"
        }}
    ],
    "general_suggestions": [
        "Additional suggestions that don't fit other categories"
    ]
}}

Focus on:
1. Identifying experiment structures that could be simplified with Builder components
2. Finding performance bottlenecks (especially in loops)
3. Suggesting PsychoPy-specific best practices
4. Recommending proper resource management

Be specific in your suggestions and provide concrete code examples."""

    @staticmethod
    def get_builder_mapping_prompt() -> str:
        """Get prompt specifically for Builder component mapping."""
        base_context = PromptTemplates.get_base_context()
        
        return f"""{base_context}

Focus specifically on identifying code patterns that could be implemented more easily using PsychoPy Builder components.

Look for:
1. Trial loops → TrialHandler component
2. Stimulus presentation sequences → Component sequences
3. Response collection → Keyboard/Mouse components
4. Data saving → Data output components
5. Condition handling → Loop components with condition files

Common patterns to identify:
- `for trial in range(n):` → TrialHandler with nReps=n
- `visual.TextStim(...)` created in loops → TextStim component
- `event.waitKeys()` → Keyboard component
- Manual CSV writing → automatic data collection
- Condition randomization → randomized loop

Provide specific Builder component recommendations with explanations."""

    @staticmethod
    def get_performance_prompt() -> str:
        """Get prompt specifically for performance optimization."""
        base_context = PromptTemplates.get_base_context()
        
        return f"""{base_context}

Focus specifically on performance optimization opportunities.

Look for:
1. Stimulus creation inside loops (should be outside)
2. Inefficient loops that could use numpy vectorization
3. Resource loading during trials (should be pre-loaded)
4. Unnecessary object creation/destruction
5. Inefficient timing methods

Common anti-patterns:
- `visual.TextStim(...)` inside trial loops
- Python loops for coordinate calculations
- Loading images/sounds during trials
- Creating new objects every frame
- Using time.sleep() instead of frame-based timing

Provide specific optimized code examples with performance explanations."""

    @staticmethod
    def get_best_practices_prompt() -> str:
        """Get prompt specifically for best practices."""
        base_context = PromptTemplates.get_base_context()
        
        return f"""{base_context}

Focus specifically on PsychoPy best practices and coding standards.

Look for:
1. Magic numbers that should be constants
2. Hardcoded values that should be configurable
3. Missing error handling
4. Improper resource cleanup
5. Poor code organization
6. Inconsistent naming conventions

Best practice areas:
- Define constants for keys, colors, positions, timing
- Use descriptive variable names
- Separate configuration from logic
- Proper exception handling
- Resource cleanup (win.close(), core.quit())
- Consistent code formatting
- Appropriate comments and documentation

Provide specific improved code examples following PsychoPy conventions."""


class PromptBuilder:
    """Builds customized prompts based on enabled features."""
    
    def __init__(self, enabled_features: Dict[str, bool]):
        self.enabled_features = enabled_features
        
    def build_analysis_prompt(self) -> str:
        """Build a customized analysis prompt based on enabled features."""
        if all(self.enabled_features.values()):
            # All features enabled, use comprehensive prompt
            return PromptTemplates.get_analysis_prompt()
            
        # Build focused prompt based on enabled features
        sections = []
        base_context = PromptTemplates.get_base_context()
        sections.append(base_context)
        
        if self.enabled_features.get('builder_mapping', False):
            sections.append("\nFocus on Builder component mapping:")
            sections.append(PromptTemplates.get_builder_mapping_prompt().split(base_context)[1])
            
        if self.enabled_features.get('performance_optimization', False):
            sections.append("\nFocus on performance optimization:")
            sections.append(PromptTemplates.get_performance_prompt().split(base_context)[1])
            
        if self.enabled_features.get('best_practices', False):
            sections.append("\nFocus on best practices:")
            sections.append(PromptTemplates.get_best_practices_prompt().split(base_context)[1])
            
        return "\n".join(sections)
        
    def get_focused_prompt(self, focus_area: str) -> str:
        """Get a prompt focused on a specific area."""
        prompt_map = {
            'builder_mapping': PromptTemplates.get_builder_mapping_prompt,
            'performance_optimization': PromptTemplates.get_performance_prompt,
            'best_practices': PromptTemplates.get_best_practices_prompt
        }
        
        if focus_area in prompt_map:
            return prompt_map[focus_area]()
        else:
            return PromptTemplates.get_analysis_prompt()