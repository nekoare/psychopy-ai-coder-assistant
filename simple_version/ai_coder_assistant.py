# coding: utf-8
# ファイル名: ai_coder_assistant.py
# PsychoPy AI Coder Assistant - 簡易版メインスクリプト

import wx
import requests
import json
import threading
import os
import re
import hashlib
import time

# --- 設定管理 ---
PSYCHOPY_USER_DIR = os.path.join(os.path.expanduser('~'), '.psychopy3')
if not os.path.exists(PSYCHOPY_USER_DIR):
    os.makedirs(PSYCHOPY_USER_DIR)
CONFIG_FILE = os.path.join(PSYCHOPY_USER_DIR, 'ai_assistant_config.json')

class ConfigManager:
    """設定の読み書きを管理するクラス"""
    def __init__(self):
        self.config = self.load()

    def load(self):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "consent_given": False,
                "privacy_consent": False,
                "api_provider": "gemini",  # gemini only
                "api_keys": {
                    "gemini": ""
                },
                "analysis_features": {
                    "builder_mapping": True,
                    "performance_optimization": True,
                    "best_practices": True
                },
                "endpoints": {
                    "gemini": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent"
                },
                "models": {
                    "gemini": "gemini-1.5-flash-latest"
                }
            }

    def save(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def get(self, key, default=None):
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value

    def set(self, key, value):
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self.save()

    def is_configured(self):
        provider = self.get('api_provider')
        api_key = self.get(f'api_keys.{provider}')
        return provider and api_key and len(api_key.strip()) > 0

# --- プライバシー・セキュリティ ---
class CodeSanitizer:
    """コードから機密情報を検出・除去するクラス"""
    
    def __init__(self):
        self.sensitive_patterns = [
            (r'api[_-]?key\s*=\s*["\'][^"\']{20,}["\']', 'API_KEY'),
            (r'token\s*=\s*["\'][^"\']{20,}["\']', 'TOKEN'),
            (r'secret\s*=\s*["\'][^"\']{10,}["\']', 'SECRET'),
            (r'mysql://[^"\s]+', 'DATABASE_URL'),
            (r'postgresql://[^"\s]+', 'DATABASE_URL'),
            (r'/home/[^/\s]+/[^\s]*', 'USER_PATH'),
            (r'C:\\Users\\[^\\]+\\[^\s]*', 'USER_PATH'),
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL'),
        ]
    
    def sanitize_code(self, code):
        """機密情報を検出して置換する"""
        sanitized = code
        detected_issues = []
        
        for pattern, issue_type in self.sensitive_patterns:
            matches = list(re.finditer(pattern, sanitized, re.IGNORECASE))
            for match in matches:
                original = match.group()
                hash_value = hashlib.md5(original.encode()).hexdigest()[:8]
                replacement = f'<{issue_type}_{hash_value}>'
                sanitized = sanitized.replace(original, replacement)
                detected_issues.append(issue_type)
        
        return sanitized, detected_issues
    
    def assess_privacy_risk(self, detected_issues):
        """プライバシーリスクを評価"""
        high_risk = ['API_KEY', 'TOKEN', 'SECRET', 'DATABASE_URL']
        return any(issue in high_risk for issue in detected_issues)

# --- AI連携（多プロバイダー対応） ---
def build_psychopy_prompt():
    """PsychoPy専用のコンテキストプロンプト"""
    return """あなたはPsychoPyのエキスパートです。

PsychoPyの基本概念:
- Builder: TrialHandler、TextStim、ImageStim等のコンポーネント
- Coder: Pythonスクリプトによる実験作成
- Window: メイン表示画面
- Clock: 正確なタイミング制御
- Event: キーボード・マウス入力

性能最適化の重要ポイント:
- 刺激はループ外で作成し、ループ内でプロパティ更新
- time.sleep()ではなくcore.wait()を使用
- NumPy配列によるベクトル化演算
- 画像・音声ファイルの事前読み込み

ベストプラクティス:
- マジックナンバーを定数として定義
- 適切なリソースクリーンアップ (win.close(), core.quit())
- フレームベースタイミングの活用

以下のJSON形式で分析結果を返してください:
{
    "summary": "コードの概要",
    "builder_mapping": [
        {
            "original_code": "元のコード",
            "builder_equivalent": "対応するBuilderコンポーネント",
            "explanation": "マッピングの説明"
        }
    ],
    "performance_optimizations": [
        {
            "issue": "性能問題の説明", 
            "original_code": "問題のあるコード",
            "improved_code": "改善されたコード",
            "explanation": "なぜ改善されるか"
        }
    ],
    "best_practices": [
        {
            "issue": "ベストプラクティス違反",
            "original_code": "問題のあるコード", 
            "improved_code": "改善されたコード",
            "explanation": "改善理由"
        }
    ]
}"""

def build_llm_request(code, model):
    """Gemini用リクエストを構築"""
    context = build_psychopy_prompt()
    
    return {
        "contents": [{
            "parts": [
                {"text": context},
                {"text": f"以下のPsychoPyコードを分析してください:\n\n```python\n{code}\n```"}
            ]
        }],
        "generationConfig": {
            "response_mime_type": "application/json"
        }
    }

def call_llm_api(code, config):
    """Gemini API呼び出し"""
    api_key = config.get("api_keys.gemini")
    endpoint = config.get("endpoints.gemini")
    
    if not api_key or not endpoint:
        return {"error": "Gemini APIキーが設定されていません。"}
    
    # コードのサニタイズ
    sanitizer = CodeSanitizer()
    sanitized_code, detected_issues = sanitizer.sanitize_code(code)
    
    # 高リスクの場合は警告
    if sanitizer.assess_privacy_risk(detected_issues):
        return {"error": "機密情報が検出されました。APIキーやパスワードなどを削除してから再実行してください。"}
    
    # リクエスト構築
    model = config.get("models.gemini")
    request_data = build_llm_request(sanitized_code, model)
    
    # ヘッダー設定
    headers = {"Content-Type": "application/json"}
    
    # URL設定（APIキーをクエリパラメータに追加）
    url = f"{endpoint}?key={api_key}"
    
    try:
        response = requests.post(url, headers=headers, json=request_data, timeout=90)
        response.raise_for_status()
        
        # Geminiレスポンス処理
        result = response.json()['candidates'][0]['content']['parts'][0]['text']
        return json.loads(result)
            
    except requests.exceptions.RequestException as e:
        return {"error": f"API接続エラー: {str(e)}"}
    except (KeyError, IndexError, json.JSONDecodeError) as e:
        return {"error": f"レスポンス解析エラー: {str(e)}"}

# --- UI表示 ---
class SuggestionDialog(wx.Dialog):
    """分析結果を表示するダイアログ"""
    
    def __init__(self, parent, analysis_result):
        super().__init__(parent, title="AIコード分析結果", size=(800, 600))
        self.analysis_result = analysis_result
        self.create_ui()
        
    def create_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # タブ付きインターフェース
        notebook = wx.Notebook(self)
        
        if "error" in self.analysis_result:
            # エラー表示
            error_panel = wx.Panel(notebook)
            error_sizer = wx.BoxSizer(wx.VERTICAL)
            error_text = wx.StaticText(error_panel, label=f"エラー: {self.analysis_result['error']}")
            error_sizer.Add(error_text, 1, wx.ALL | wx.EXPAND, 10)
            error_panel.SetSizer(error_sizer)
            notebook.AddPage(error_panel, "エラー")
        else:
            # 正常な分析結果表示
            if self.analysis_result.get("builder_mapping"):
                builder_panel = self.create_suggestion_panel(notebook, "builder_mapping", "Builderマッピング")
                notebook.AddPage(builder_panel, "Builder")
                
            if self.analysis_result.get("performance_optimizations"):
                perf_panel = self.create_suggestion_panel(notebook, "performance_optimizations", "性能最適化")
                notebook.AddPage(perf_panel, "性能")
                
            if self.analysis_result.get("best_practices"):
                best_panel = self.create_suggestion_panel(notebook, "best_practices", "ベストプラクティス")
                notebook.AddPage(best_panel, "品質")
        
        main_sizer.Add(notebook, 1, wx.ALL | wx.EXPAND, 5)
        
        # 閉じるボタン
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        close_btn = wx.Button(self, wx.ID_CLOSE, "閉じる")
        btn_sizer.Add(close_btn, 0, wx.ALL, 5)
        main_sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 5)
        
        close_btn.Bind(wx.EVT_BUTTON, lambda e: self.Close())
        
        self.SetSizer(main_sizer)
        
    def create_suggestion_panel(self, parent, key, title):
        """提案パネルを作成"""
        panel = wx.Panel(parent)
        sizer = wx.BoxSizer(wx.VERTICAL)
        
        suggestions = self.analysis_result[key]
        
        for i, suggestion in enumerate(suggestions):
            # 提案ごとのボックス
            box = wx.StaticBox(panel, label=f"{title} #{i+1}")
            box_sizer = wx.StaticBoxSizer(box, wx.VERTICAL)
            
            # 説明
            if 'explanation' in suggestion:
                desc = wx.StaticText(panel, label=suggestion['explanation'])
                desc.Wrap(750)
                box_sizer.Add(desc, 0, wx.ALL | wx.EXPAND, 5)
            
            # 元のコード
            if 'original_code' in suggestion:
                box_sizer.Add(wx.StaticText(panel, label="元のコード:"), 0, wx.ALL, 2)
                original = wx.TextCtrl(panel, value=suggestion['original_code'], 
                                     style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 60))
                original.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                box_sizer.Add(original, 0, wx.ALL | wx.EXPAND, 2)
            
            # 改善されたコード
            if 'improved_code' in suggestion:
                box_sizer.Add(wx.StaticText(panel, label="改善案:"), 0, wx.ALL, 2)
                improved = wx.TextCtrl(panel, value=suggestion['improved_code'], 
                                     style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 60))
                improved.SetFont(wx.Font(9, wx.FONTFAMILY_TELETYPE, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
                box_sizer.Add(improved, 0, wx.ALL | wx.EXPAND, 2)
            elif 'builder_equivalent' in suggestion:
                box_sizer.Add(wx.StaticText(panel, label="Builderでの実装:"), 0, wx.ALL, 2)
                builder = wx.TextCtrl(panel, value=suggestion['builder_equivalent'], 
                                    style=wx.TE_MULTILINE | wx.TE_READONLY, size=(-1, 40))
                box_sizer.Add(builder, 0, wx.ALL | wx.EXPAND, 2)
            
            sizer.Add(box_sizer, 0, wx.ALL | wx.EXPAND, 5)
        
        panel.SetSizer(sizer)
        return panel

# --- 設定ダイアログ ---
class SettingsDialog(wx.Dialog):
    """設定ダイアログ"""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent, title="AI Assistant 設定", size=(500, 400))
        self.config_manager = config_manager
        self.create_ui()
        self.load_settings()
        
    def create_ui(self):
        main_sizer = wx.BoxSizer(wx.VERTICAL)
        
        # AIプロバイダー（Geminiのみ）
        provider_box = wx.StaticBoxSizer(wx.VERTICAL, self, "AIプロバイダー")
        gemini_label = wx.StaticText(self, label="Google Gemini (無料枠: 月15回まで)")
        font = gemini_label.GetFont()
        font.PointSize += 1
        font = font.Bold()
        gemini_label.SetFont(font)
        provider_box.Add(gemini_label, 0, wx.ALL, 5)
        main_sizer.Add(provider_box, 0, wx.ALL | wx.EXPAND, 10)
        
        # APIキー設定
        key_box = wx.StaticBoxSizer(wx.VERTICAL, self, "APIキー設定")
        
        key_box.Add(wx.StaticText(self, label="Gemini API Key:"), 0, wx.ALL, 5)
        self.gemini_key = wx.TextCtrl(self, style=wx.TE_PASSWORD)
        key_box.Add(self.gemini_key, 0, wx.ALL | wx.EXPAND, 5)
        
        # APIキー取得のヘルプ
        help_text = wx.StaticText(self, label="APIキー取得: https://aistudio.google.com/app/apikey")
        help_text.SetForegroundColour(wx.Colour(0, 0, 255))  # 青色
        key_box.Add(help_text, 0, wx.ALL, 5)
        
        main_sizer.Add(key_box, 0, wx.ALL | wx.EXPAND, 10)
        
        # 分析機能設定
        features_box = wx.StaticBoxSizer(wx.VERTICAL, self, "分析機能")
        self.builder_cb = wx.CheckBox(self, label="Builderコンポーネントマッピング")
        self.performance_cb = wx.CheckBox(self, label="性能最適化")
        self.practices_cb = wx.CheckBox(self, label="ベストプラクティス")
        
        features_box.Add(self.builder_cb, 0, wx.ALL, 5)
        features_box.Add(self.performance_cb, 0, wx.ALL, 5) 
        features_box.Add(self.practices_cb, 0, wx.ALL, 5)
        main_sizer.Add(features_box, 0, wx.ALL | wx.EXPAND, 10)
        
        # ボタン
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
        save_btn = wx.Button(self, wx.ID_OK, "保存")
        cancel_btn = wx.Button(self, wx.ID_CANCEL, "キャンセル")
        btn_sizer.Add(save_btn, 0, wx.ALL, 5)
        btn_sizer.Add(cancel_btn, 0, wx.ALL, 5)
        main_sizer.Add(btn_sizer, 0, wx.ALL | wx.CENTER, 10)
        
        save_btn.Bind(wx.EVT_BUTTON, self.on_save)
        cancel_btn.Bind(wx.EVT_BUTTON, lambda e: self.EndModal(wx.ID_CANCEL))
        
        self.SetSizer(main_sizer)
        
    def load_settings(self):
        """設定をUIに読み込み"""
        # APIキー（セキュリティのため実際の値は表示しない）
        key = self.config_manager.get('api_keys.gemini')
        if key:
            self.gemini_key.SetValue('*' * 20)
        
        # 機能設定
        self.builder_cb.SetValue(self.config_manager.get('analysis_features.builder_mapping', True))
        self.performance_cb.SetValue(self.config_manager.get('analysis_features.performance_optimization', True))
        self.practices_cb.SetValue(self.config_manager.get('analysis_features.best_practices', True))
        
    def on_save(self, event):
        """設定を保存"""
        # プロバイダー（Gemini固定）
        self.config_manager.set('api_provider', 'gemini')
        
        # APIキー（変更された場合のみ保存）
        key = self.gemini_key.GetValue()
        if key and not key.startswith('*'):
            self.config_manager.set('api_keys.gemini', key)
        
        # 機能設定
        self.config_manager.set('analysis_features.builder_mapping', self.builder_cb.GetValue())
        self.config_manager.set('analysis_features.performance_optimization', self.performance_cb.GetValue())
        self.config_manager.set('analysis_features.best_practices', self.practices_cb.GetValue())
        
        self.EndModal(wx.ID_OK)

# --- メイン処理 ---
def analyze_with_ai(event):
    """AIコード分析のメイン関数"""
    config_manager = ConfigManager()
    
    # 設定チェック
    if not config_manager.is_configured():
        wx.MessageBox("APIキーが設定されていません。メニューから設定してください。", "設定エラー", wx.OK | wx.ICON_ERROR)
        show_settings(None)
        return
    
    # プライバシー同意チェック
    if not config_manager.get("privacy_consent"):
        result = wx.MessageBox(
            "この機能はコードを外部AIサービスに送信して分析します。\n"
            "機密情報が含まれていないことを確認してください。\n\n"
            "続行しますか？",
            "プライバシー確認",
            wx.YES_NO | wx.ICON_WARNING
        )
        if result != wx.YES:
            return
        config_manager.set("privacy_consent", True)
    
    # 現在のコードを取得
    try:
        app = wx.GetApp()
        coder_frame = None
        
        for window in wx.GetTopLevelWindows():
            if "CoderFrame" in str(type(window)):
                coder_frame = window
                break
        
        if not coder_frame:
            wx.MessageBox("Coderウィンドウが見つかりません。", "エラー", wx.OK | wx.ICON_ERROR)
            return
            
        editor = coder_frame.currentDoc
        if not editor:
            wx.MessageBox("アクティブなエディターが見つかりません。", "エラー", wx.OK | wx.ICON_ERROR)
            return
            
        script_text = editor.GetText()
        if not script_text.strip():
            wx.MessageBox("分析するコードがありません。", "エラー", wx.OK | wx.ICON_ERROR)
            return
            
    except Exception as e:
        wx.MessageBox(f"コード取得エラー: {str(e)}", "エラー", wx.OK | wx.ICON_ERROR)
        return
    
    # プログレスダイアログを表示して分析開始
    progress = wx.ProgressDialog(
        "AI分析中",
        "コードを分析しています...",
        maximum=100,
        parent=coder_frame,
        style=wx.PD_APP_MODAL | wx.PD_AUTO_HIDE
    )
    progress.Pulse()
    
    def background_analysis():
        """バックグラウンドでAI分析を実行"""
        try:
            result = call_llm_api(script_text, config_manager)
            wx.CallAfter(show_analysis_result, coder_frame, result, progress)
        except Exception as e:
            wx.CallAfter(show_analysis_result, coder_frame, {"error": str(e)}, progress)
    
    threading.Thread(target=background_analysis, daemon=True).start()

def show_analysis_result(parent, result, progress):
    """分析結果を表示"""
    progress.Destroy()
    dialog = SuggestionDialog(parent, result)
    dialog.ShowModal()
    dialog.Destroy()

def show_settings(event):
    """設定ダイアログを表示"""
    config_manager = ConfigManager()
    dialog = SettingsDialog(None, config_manager)
    dialog.ShowModal()
    dialog.Destroy()