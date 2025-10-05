"""UI components for PsychoPy Coder integration.

このモジュールはオプション依存 (wxPython / PsychoPy GUI) に依存します。
CI や最小インストール環境では wx が存在しないため、インポートに失敗
してもプレースホルダを提供してテストを継続できるようにします。
"""

from typing import List
from .analyzer import CodeAnalyzer, AnalysisResult, CodeSuggestion
from .config import ConfigManager

try:  # pragma: no cover - 通常 GUI 環境
    import wx  # type: ignore
except Exception:  # pragma: no cover - ヘッドレス/CI
    wx = None  # type: ignore


if wx is None:  # フォールバック軽量クラス定義
    class AIAssistantPanel:  # type: ignore
        def __init__(self, parent, code_analyzer: CodeAnalyzer):  # noqa: D401
            self.code_analyzer = code_analyzer
        def analyze_code(self, code: str):
            # 非GUI環境では何もしない
            pass
    class AISettingsDialog:  # type: ignore
        def __init__(self, parent, config_manager: ConfigManager):
            self.config_manager = config_manager
        def ShowModal(self):
            return 0
        def Destroy(self):
            pass
else:  # 本来の GUI 実装
    class AIAssistantPanel(wx.Panel):  # pragma: no cover - GUI 部分
        """Side panel for displaying AI analysis results."""
        def __init__(self, parent, code_analyzer: CodeAnalyzer):
            super().__init__(parent)
            self.code_analyzer = code_analyzer
            self.current_suggestions: List[CodeSuggestion] = []
            self._create_ui()
            self._bind_events()
        def _create_ui(self):
            main_sizer = wx.BoxSizer(wx.VERTICAL)
            title = wx.StaticText(self, label="AI Code Assistant")
            title_font = title.GetFont(); title_font.PointSize += 2; title_font = title_font.Bold(); title.SetFont(title_font)
            main_sizer.Add(title, 0, wx.ALL | wx.CENTER, 5)
            self.status_text = wx.StaticText(self, label="Ready")
            main_sizer.Add(self.status_text, 0, wx.ALL | wx.EXPAND, 5)
            self.progress = wx.Gauge(self, range=100); self.progress.Hide(); main_sizer.Add(self.progress, 0, wx.ALL | wx.EXPAND, 5)
            filter_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.filter_all = wx.ToggleButton(self, label="All")
            self.filter_builder = wx.ToggleButton(self, label="Builder")
            self.filter_performance = wx.ToggleButton(self, label="Performance")
            self.filter_practices = wx.ToggleButton(self, label="Practices")
            self.filter_all.SetValue(True)
            for btn in [self.filter_all, self.filter_builder, self.filter_performance, self.filter_practices]:
                filter_sizer.Add(btn, 1, wx.ALL, 2)
            main_sizer.Add(filter_sizer, 0, wx.ALL | wx.EXPAND, 5)
            self.suggestions_list = SuggestionsList(self)
            main_sizer.Add(self.suggestions_list, 1, wx.ALL | wx.EXPAND, 5)
            button_sizer = wx.BoxSizer(wx.HORIZONTAL)
            self.apply_btn = wx.Button(self, label="Apply Selected")
            self.refresh_btn = wx.Button(self, label="Refresh")
            self.apply_btn.Enable(False)
            button_sizer.Add(self.apply_btn, 1, wx.ALL, 2)
            button_sizer.Add(self.refresh_btn, 1, wx.ALL, 2)
            main_sizer.Add(button_sizer, 0, wx.ALL | wx.EXPAND, 5)
            self.SetSizer(main_sizer)
        def _bind_events(self):
            self.filter_all.Bind(wx.EVT_TOGGLEBUTTON, self._on_filter_change)
            self.filter_builder.Bind(wx.EVT_TOGGLEBUTTON, self._on_filter_change)
            self.filter_performance.Bind(wx.EVT_TOGGLEBUTTON, self._on_filter_change)
            self.filter_practices.Bind(wx.EVT_TOGGLEBUTTON, self._on_filter_change)
            self.apply_btn.Bind(wx.EVT_BUTTON, self._on_apply_selected)
            self.refresh_btn.Bind(wx.EVT_BUTTON, self._on_refresh)
        def analyze_code(self, code: str):
            self.status_text.SetLabel("Analyzing code..."); self.progress.Show(); self.progress.Pulse(); self.Layout()
            self.code_analyzer.analyze_code_async(code, self._on_analysis_complete)
        def _on_analysis_complete(self, result: AnalysisResult):
            wx.CallAfter(self._update_results, result)
        def _update_results(self, result: AnalysisResult):
            self.progress.Hide()
            if result.success:
                self.status_text.SetLabel(f"Analysis complete ({result.analysis_time:.1f}s)")
                self.current_suggestions = result.suggestions
                self._update_suggestions_display(); self.apply_btn.Enable(len(result.suggestions) > 0)
            else:
                self.status_text.SetLabel(f"Analysis failed: {result.error_message}")
                self.current_suggestions = []; self.suggestions_list.clear(); self.apply_btn.Enable(False)
            self.Layout()
        def _update_suggestions_display(self):
            filtered_suggestions = self._get_filtered_suggestions(); self.suggestions_list.update_suggestions(filtered_suggestions)
        def _get_filtered_suggestions(self) -> List[CodeSuggestion]:
            if self.filter_all.GetValue():
                return self.current_suggestions
            filtered: List[CodeSuggestion] = []
            if self.filter_builder.GetValue():
                filtered.extend([s for s in self.current_suggestions if s.category == 'builder_mapping'])
            if self.filter_performance.GetValue():
                filtered.extend([s for s in self.current_suggestions if s.category == 'performance'])
            if self.filter_practices.GetValue():
                filtered.extend([s for s in self.current_suggestions if s.category == 'best_practices'])
            return filtered
        def _on_filter_change(self, _event):
            if not any([self.filter_all.GetValue(), self.filter_builder.GetValue(), self.filter_performance.GetValue(), self.filter_practices.GetValue()]):
                self.filter_all.SetValue(True)
            self._update_suggestions_display()
        def _on_apply_selected(self, _event):
            selected = self.suggestions_list.get_selected_suggestions()
            if selected:
                wx.MessageBox(f"Would apply {len(selected)} suggestions.\n(Implementation pending)", "Apply Suggestions", wx.OK | wx.ICON_INFORMATION)
        def _on_refresh(self, _event):
            parent_frame = self.GetTopLevelParent()
            if hasattr(parent_frame, 'currentDoc') and parent_frame.currentDoc:
                code = parent_frame.currentDoc.GetText(); self.analyze_code(code)

    class SuggestionsList(wx.ListCtrl):  # pragma: no cover
        def __init__(self, parent):
            super().__init__(parent, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
            self.suggestions: List[CodeSuggestion] = []
            self.AppendColumn("Priority", width=60)
            self.AppendColumn("Category", width=80)
            self.AppendColumn("Title", width=200)
            self.Bind(wx.EVT_LIST_ITEM_SELECTED, self._on_item_selected)
        def update_suggestions(self, suggestions: List[CodeSuggestion]):
            self.suggestions = suggestions; self.DeleteAllItems()
            for i, suggestion in enumerate(suggestions):
                index = self.InsertItem(i, str(suggestion.priority))
                self.SetItem(index, 1, suggestion.category.replace('_', ' ').title())
                self.SetItem(index, 2, suggestion.title)
                if suggestion.priority >= 4:
                    self.SetItemTextColour(index, wx.Colour(255, 0, 0))
                elif suggestion.priority >= 3:
                    self.SetItemTextColour(index, wx.Colour(255, 165, 0))
        def clear(self):
            self.suggestions = []; self.DeleteAllItems()
        def get_selected_suggestions(self) -> List[CodeSuggestion]:
            selected: List[CodeSuggestion] = []; item = self.GetFirstSelected()
            while item != -1:
                if item < len(self.suggestions):
                    selected.append(self.suggestions[item])
                item = self.GetNextSelected(item)
            return selected
        def _on_item_selected(self, event):
            index = event.GetIndex()
            if 0 <= index < len(self.suggestions):
                suggestion = self.suggestions[index]; self._show_suggestion_details(suggestion)
        def _show_suggestion_details(self, suggestion: CodeSuggestion):
            dialog = SuggestionDetailDialog(self, suggestion); dialog.ShowModal(); dialog.Destroy()

    class SuggestionDetailDialog(wx.Dialog):  # pragma: no cover
        def __init__(self, parent, suggestion: CodeSuggestion):
            super().__init__(parent, title=suggestion.title, size=(600, 400))
            self.suggestion = suggestion; self._create_ui()
        def _create_ui(self):
            main_sizer = wx.BoxSizer(wx.VERTICAL)
            desc_text = wx.StaticText(self, label=self.suggestion.description); desc_text.Wrap(550); main_sizer.Add(desc_text, 0, wx.ALL | wx.EXPAND, 10)
            if self.suggestion.original_code:
                main_sizer.Add(wx.StaticText(self, label="Original Code:"), 0, wx.ALL, 5)
                original_text = wx.TextCtrl(self, value=self.suggestion.original_code, style=wx.TE_MULTILINE | wx.TE_READONLY)
                original_text.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)); main_sizer.Add(original_text, 1, wx.ALL | wx.EXPAND, 5)
            if self.suggestion.improved_code:
                main_sizer.Add(wx.StaticText(self, label="Suggested Improvement:"), 0, wx.ALL, 5)
                improved_text = wx.TextCtrl(self, value=self.suggestion.improved_code, style=wx.TE_MULTILINE | wx.TE_READONLY)
                improved_text.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL)); main_sizer.Add(improved_text, 1, wx.ALL | wx.EXPAND, 5)
            button_sizer = wx.BoxSizer(wx.HORIZONTAL)
            apply_btn = wx.Button(self, wx.ID_APPLY, "Apply"); close_btn = wx.Button(self, wx.ID_CLOSE, "Close")
            button_sizer.Add(apply_btn, 0, wx.ALL, 5); button_sizer.Add(close_btn, 0, wx.ALL, 5)
            main_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 5)
            apply_btn.Bind(wx.EVT_BUTTON, self._on_apply); close_btn.Bind(wx.EVT_BUTTON, self._on_close)
            self.SetSizer(main_sizer)
        def _on_apply(self, _event):
            wx.MessageBox("Apply functionality not yet implemented", "Info", wx.OK | wx.ICON_INFORMATION)
        def _on_close(self, _event):
            self.EndModal(wx.ID_CLOSE)

    class AISettingsDialog(wx.Dialog):  # pragma: no cover
        def __init__(self, parent, config_manager: ConfigManager):
            super().__init__(parent, title="AI Assistant Settings", size=(500, 400))
            self.config_manager = config_manager; self._create_ui(); self._load_settings()
        def _create_ui(self):
            main_sizer = wx.BoxSizer(wx.VERTICAL)
            provider_box = wx.StaticBoxSizer(wx.VERTICAL, self, "API Provider")
            self.provider_choice = wx.Choice(self, choices=["OpenAI", "Anthropic", "Google"])
            provider_box.Add(wx.StaticText(self, label="Provider:"), 0, wx.ALL, 5); provider_box.Add(self.provider_choice, 0, wx.ALL | wx.EXPAND, 5)
            main_sizer.Add(provider_box, 0, wx.ALL | wx.EXPAND, 10)
            keys_box = wx.StaticBoxSizer(wx.VERTICAL, self, "API Keys")
            keys_box.Add(wx.StaticText(self, label="OpenAI API Key:"), 0, wx.ALL, 2); self.openai_key = wx.TextCtrl(self, style=wx.TE_PASSWORD); keys_box.Add(self.openai_key, 0, wx.ALL | wx.EXPAND, 2)
            keys_box.Add(wx.StaticText(self, label="Anthropic API Key:"), 0, wx.ALL, 2); self.anthropic_key = wx.TextCtrl(self, style=wx.TE_PASSWORD); keys_box.Add(self.anthropic_key, 0, wx.ALL | wx.EXPAND, 2)
            keys_box.Add(wx.StaticText(self, label="Google API Key:"), 0, wx.ALL, 2); self.google_key = wx.TextCtrl(self, style=wx.TE_PASSWORD); keys_box.Add(self.google_key, 0, wx.ALL | wx.EXPAND, 2)
            main_sizer.Add(keys_box, 0, wx.ALL | wx.EXPAND, 10)
            features_box = wx.StaticBoxSizer(wx.VERTICAL, self, "Analysis Features")
            self.builder_mapping_cb = wx.CheckBox(self, label="Builder Component Mapping")
            self.performance_cb = wx.CheckBox(self, label="Performance Optimization")
            self.best_practices_cb = wx.CheckBox(self, label="Best Practices")
            for cb in [self.builder_mapping_cb, self.performance_cb, self.best_practices_cb]:
                features_box.Add(cb, 0, wx.ALL, 5)
            main_sizer.Add(features_box, 0, wx.ALL | wx.EXPAND, 10)
            button_sizer = wx.BoxSizer(wx.HORIZONTAL)
            save_btn = wx.Button(self, wx.ID_OK, "Save"); cancel_btn = wx.Button(self, wx.ID_CANCEL, "Cancel")
            button_sizer.Add(save_btn, 0, wx.ALL, 5); button_sizer.Add(cancel_btn, 0, wx.ALL, 5)
            main_sizer.Add(button_sizer, 0, wx.ALL | wx.CENTER, 10)
            save_btn.Bind(wx.EVT_BUTTON, self._on_save); cancel_btn.Bind(wx.EVT_BUTTON, self._on_cancel)
            self.SetSizer(main_sizer)
        def _load_settings(self):
            provider = self.config_manager.get('api_provider', 'openai'); provider_map = {'openai': 0, 'anthropic': 1, 'google': 2}; self.provider_choice.SetSelection(provider_map.get(provider, 0))
            if self.config_manager.get_api_key('openai'): self.openai_key.SetValue('*' * 20)
            if self.config_manager.get_api_key('anthropic'): self.anthropic_key.SetValue('*' * 20)
            if self.config_manager.get_api_key('google'): self.google_key.SetValue('*' * 20)
            features = self.config_manager.get('analysis_features', {})
            self.builder_mapping_cb.SetValue(features.get('builder_mapping', True))
            self.performance_cb.SetValue(features.get('performance_optimization', True))
            self.best_practices_cb.SetValue(features.get('best_practices', True))
        def _on_save(self, _event):
            provider_map = {0: 'openai', 1: 'anthropic', 2: 'google'}; provider = provider_map[self.provider_choice.GetSelection()]; self.config_manager.set('api_provider', provider)
            openai_key = self.openai_key.GetValue();
            if openai_key and not openai_key.startswith('*'): self.config_manager.set_api_key('openai', openai_key)
            anthropic_key = self.anthropic_key.GetValue();
            if anthropic_key and not anthropic_key.startswith('*'): self.config_manager.set_api_key('anthropic', anthropic_key)
            google_key = self.google_key.GetValue();
            if google_key and not google_key.startswith('*'): self.config_manager.set_api_key('google', google_key)
            features = {'builder_mapping': self.builder_mapping_cb.GetValue(), 'performance_optimization': self.performance_cb.GetValue(), 'best_practices': self.best_practices_cb.GetValue()}
            self.config_manager.set('analysis_features', features); self.EndModal(wx.ID_OK)
        def _on_cancel(self, _event):
            self.EndModal(wx.ID_CANCEL)