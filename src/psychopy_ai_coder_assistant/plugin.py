"""
Main plugin class for PsychoPy AI Coder Assistant
"""

import wx
from typing import Optional, Dict, Any
from psychopy import app
from psychopy.app.coder import CoderFrame

from .ui import AIAssistantPanel, AISettingsDialog
from .analyzer import CodeAnalyzer
from .config import ConfigManager


class AICoderAssistantPlugin:
    """Main plugin class that integrates AI assistant into PsychoPy Coder."""
    
    def __init__(self, coder_frame: Optional[CoderFrame] = None):
        self.coder_frame = coder_frame
        self.config_manager = ConfigManager()
        self.code_analyzer = CodeAnalyzer(self.config_manager)
        self.assistant_panel: Optional[AIAssistantPanel] = None
        self.menu_id = wx.NewIdRef()
        self.toolbar_id = wx.NewIdRef()
        self.settings_id = wx.NewIdRef()
        
    def register(self) -> None:
        """Register the plugin with PsychoPy Coder."""
        if not self.coder_frame:
            return
            
        self._add_menu_items()
        self._add_toolbar_button()
        self._create_assistant_panel()
        
    def _add_menu_items(self) -> None:
        """Add AI Assistant menu items to Coder."""
        if not self.coder_frame or not hasattr(self.coder_frame, 'menuBar'):
            return
            
        # Create Tools menu if it doesn't exist
        tools_menu = None
        menubar = self.coder_frame.menuBar
        
        for i in range(menubar.GetMenuCount()):
            menu_label = menubar.GetMenuLabel(i)
            if 'Tools' in menu_label or 'ツール' in menu_label:  # Support Japanese
                tools_menu = menubar.GetMenu(i)
                break
                
        if not tools_menu:
            tools_menu = wx.Menu()
            menubar.Append(tools_menu, _('Tools'))
            
        # Add AI Assistant menu items
        tools_menu.AppendSeparator()
        tools_menu.Append(self.menu_id, _('AI Code Review\tCtrl+Shift+A'), 
                         _('Analyze current code with AI assistant'))
        tools_menu.Append(self.settings_id, _('AI Assistant Settings'), 
                         _('Configure AI assistant settings'))
        
        # Bind events
        self.coder_frame.Bind(wx.EVT_MENU, self.on_ai_review, id=self.menu_id)
        self.coder_frame.Bind(wx.EVT_MENU, self.on_settings, id=self.settings_id)
        
    def _add_toolbar_button(self) -> None:
        """Add AI Assistant button to toolbar."""
        if not self.coder_frame or not hasattr(self.coder_frame, 'toolbar'):
            return
            
        toolbar = self.coder_frame.toolbar
        
        # Add separator and AI button
        toolbar.AddSeparator()
        toolbar.AddTool(self.toolbar_id, 'AI Review', 
                       wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_TOOLBAR),
                       'Analyze code with AI assistant')
        
        # Bind event
        self.coder_frame.Bind(wx.EVT_TOOL, self.on_ai_review, id=self.toolbar_id)
        toolbar.Realize()
        
    def _create_assistant_panel(self) -> None:
        """Create the AI assistant side panel."""
        if not self.coder_frame:
            return
            
        # Create panel in the right side of the coder frame
        parent = self.coder_frame
        self.assistant_panel = AIAssistantPanel(parent, self.code_analyzer)
        
        # Add to sizer if available
        if hasattr(self.coder_frame, 'mainSizer'):
            self.coder_frame.mainSizer.Add(self.assistant_panel, 0, wx.EXPAND | wx.ALL, 5)
            self.coder_frame.Layout()
            
    def on_ai_review(self, event: wx.Event) -> None:
        """Handle AI code review request."""
        if not self.coder_frame or not self.assistant_panel:
            return
            
        # Check if API is configured
        if not self.config_manager.is_configured():
            wx.MessageBox(
                _('Please configure your AI API settings first.\nGo to Tools → AI Assistant Settings'),
                _('Configuration Required'),
                wx.OK | wx.ICON_INFORMATION
            )
            self.on_settings(event)
            return
            
        # Show privacy warning if first time
        if self.config_manager.get('show_privacy_warning', True):
            result = wx.MessageBox(
                _('This feature sends your code to external AI services for analysis.\n'
                  'Please ensure your code contains no sensitive information.\n\n'
                  'Do you want to continue?'),
                _('Privacy Warning'),
                wx.YES_NO | wx.ICON_WARNING
            )
            
            if result != wx.YES:
                return
                
            self.config_manager.set('show_privacy_warning', False)
            
        # Get current code
        current_editor = self.coder_frame.currentDoc
        if not current_editor:
            wx.MessageBox(_('No active editor found'), _('Error'), wx.OK | wx.ICON_ERROR)
            return
            
        code = current_editor.GetText()
        if not code.strip():
            wx.MessageBox(_('No code to analyze'), _('Error'), wx.OK | wx.ICON_ERROR)
            return
            
        # Analyze code asynchronously
        self.assistant_panel.analyze_code(code)
        
    def on_settings(self, event: wx.Event) -> None:
        """Handle settings dialog request."""
        dialog = AISettingsDialog(self.coder_frame, self.config_manager)
        dialog.ShowModal()
        dialog.Destroy()


def _(text: str) -> str:
    """Placeholder for internationalization."""
    return text