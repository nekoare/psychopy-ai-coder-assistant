"""
PsychoPy AI Coder Assistant Plugin

An AI-powered extension for PsychoPy Coder that provides intelligent code analysis,
optimization suggestions, and Builder component mapping recommendations.
"""

__version__ = "0.1.0"
__author__ = "AI Assistant Developer"

from .plugin import AICoderAssistantPlugin

def loadPlugin():
    """Entry point for PsychoPy plugin loading."""
    from psychopy import app
    
    # Get the Coder frame if it exists
    coder_frame = None
    if hasattr(app, 'coder') and app.coder:
        coder_frame = app.coder
    
    # Initialize the plugin
    plugin = AICoderAssistantPlugin(coder_frame)
    plugin.register()
    
    return plugin

# Metadata for PsychoPy plugin system
plugin_info = {
    'name': 'AI Coder Assistant',
    'version': __version__,
    'description': 'AI-powered code analysis and optimization assistant',
    'author': __author__,
    'psychopy_min_version': '2023.1.0'
}