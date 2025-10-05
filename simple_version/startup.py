# coding: utf-8
# ファイル名: startup.py
# 配置場所: ~/.psychopy3/startup.py
# PsychoPy AI Coder Assistant - 起動スクリプト

import wx
import sys
import os
import threading
import time

# ai_coder_assistant.py が同じディレクトリにあることを前提とする
sys.path.append(os.path.dirname(__file__))
try:
    import ai_coder_assistant
except ImportError as e:
    print(f"AI Coder Assistantのインポートに失敗しました: {e}")
    ai_coder_assistant = None

def show_welcome_dialog(config_manager):
    """初回セットアップダイアログ"""
    message = (
        "🤖 PsychoPy AI Coder Assistant へようこそ！\n\n"
        "この拡張機能は、あなたのPsychoPyコードを分析し、以下の改善提案を行います：\n\n"
        "🏗️ Builderコンポーネントへのマッピング提案\n"
        "⚡ 性能最適化の推奨事項\n"
        "📋 ベストプラクティスの改善案\n\n"
        "【重要な注意事項】\n"
        "• コードはGoogle Gemini AIサービスに送信されます\n"
        "• 機密情報や個人情報を含むコードの分析は避けてください\n" 
        "• Gemini APIキーの取得が必要です（月15回まで無料）\n"
        "• 送信前に自動的に機密情報の検出・除去を行います\n\n"
        "今すぐ設定を開始しますか？"
    )
    
    dlg = wx.MessageDialog(
        None, 
        message, 
        "AI Coder Assistant - セットアップ", 
        wx.YES_NO | wx.ICON_INFORMATION
    )
    
    result = dlg.ShowModal()
    dlg.Destroy()
    
    if result == wx.ID_YES:
        config_manager.set("consent_given", True)
        # 設定ダイアログを開く
        wx.CallAfter(ai_coder_assistant.show_settings, None)
        return True
    else:
        config_manager.set("consent_given", False)
        return False

def add_menu_to_coder(coder_frame, config_manager):
    """Coderのメニューに項目を追加する"""
    try:
        menu_bar = coder_frame.GetMenuBar()
        if not menu_bar:
            return
        
        # ツールメニューを探す（日本語・英語両方に対応）
        tools_menu = None
        tools_menu_pos = -1
        
        for i in range(menu_bar.GetMenuCount()):
            menu_label = menu_bar.GetMenuLabel(i)
            if any(keyword in menu_label.lower() for keyword in ['tool', 'ツール']):
                tools_menu = menu_bar.GetMenu(i)
                tools_menu_pos = i
                break
        
        if not tools_menu:
            # ツールメニューが存在しない場合は作成
            tools_menu = wx.Menu()
            menu_bar.Insert(menu_bar.GetMenuCount() - 1, tools_menu, "ツール(&T)")
        
        # セパレーターを追加（既存項目がある場合）
        if tools_menu.GetMenuItemCount() > 0:
            tools_menu.AppendSeparator()
        
        # AI分析メニュー項目
        menu_id_analyze = wx.NewIdRef()
        analyze_item = tools_menu.Append(
            menu_id_analyze, 
            "AIコード分析(&A)\tCtrl+Shift+A", 
            "現在のスクリプトをAIで分析し、改善提案を取得します"
        )
        
        # 設定メニュー項目
        menu_id_settings = wx.NewIdRef()
        settings_item = tools_menu.Append(
            menu_id_settings,
            "AI Assistant 設定(&S)",
            "AIアシスタントの設定を変更します"
        )
        
        # ヘルプメニュー項目
        menu_id_help = wx.NewIdRef()
        help_item = tools_menu.Append(
            menu_id_help,
            "AI Assistant ヘルプ(&H)",
            "AIアシスタントの使い方を表示します"
        )
        
        # イベントバインド
        coder_frame.Bind(wx.EVT_MENU, ai_coder_assistant.analyze_with_ai, id=menu_id_analyze)
        coder_frame.Bind(wx.EVT_MENU, ai_coder_assistant.show_settings, id=menu_id_settings)
        coder_frame.Bind(wx.EVT_MENU, lambda e: show_help_dialog(coder_frame), id=menu_id_help)
        
        # キーボードショートカットの設定
        accel_table = wx.AcceleratorTable([
            (wx.ACCEL_CTRL | wx.ACCEL_SHIFT, ord('A'), menu_id_analyze)
        ])
        coder_frame.SetAcceleratorTable(accel_table)
        
        # ツールバーにボタンを追加
        add_toolbar_button(coder_frame, menu_id_analyze)
        
        print("AI Coder Assistant: メニューとツールバーに項目を追加しました")
        
    except Exception as e:
        print(f"AI Coder Assistant: メニュー追加エラー - {e}")

def add_toolbar_button(coder_frame, menu_id):
    """ツールバーにAIボタンを追加"""
    try:
        toolbar = getattr(coder_frame, 'toolbar', None)
        if not toolbar:
            return
            
        # セパレーターを追加
        toolbar.AddSeparator()
        
        # AIアシスタントボタンを追加
        ai_tool = toolbar.AddTool(
            menu_id,
            "AI分析",
            wx.ArtProvider.GetBitmap(wx.ART_TIP, wx.ART_TOOLBAR, (16, 16)),
            shortHelp="AIコード分析",
            longHelp="現在のコードをAIで分析します"
        )
        
        toolbar.Realize()
        
    except Exception as e:
        print(f"AI Coder Assistant: ツールバー追加エラー - {e}")

def show_help_dialog(parent):
    """ヘルプダイアログを表示"""
    help_text = """🤖 PsychoPy AI Coder Assistant ヘルプ

【基本的な使い方】
1. PsychoPy Coderでスクリプトを開く
2. メニューから「ツール → AIコード分析」を選択
   または Ctrl+Shift+A を押す
3. 分析結果を確認し、提案された改善を検討する

【分析内容】
🏗️ Builderマッピング: 手書きコードをBuilderコンポーネントで実現する方法
⚡ 性能最適化: ループ内での刺激作成など、性能に影響する問題の検出
📋 ベストプラクティス: PsychoPyの推奨する書き方への改善提案

【AIプロバイダー】
• Google Gemini (無料枠: 月15回まで)

【プライバシーとセキュリティ】
• コード送信前に機密情報を自動検出・除去
• APIキー、パスワード、ファイルパスなどを自動マスク
• ユーザーの同意なしにはコードを送信しません

【設定方法】
1. メニューから「ツール → AI Assistant 設定」を選択
2. Gemini APIキーを入力
3. 分析機能を選択して保存

【APIキーの取得方法】
• Gemini: https://aistudio.google.com/app/apikey (月15回まで無料)

【トラブルシューティング】
• メニューに項目が表示されない → PsychoPyを再起動
• 分析が失敗する → APIキーと残クレジットを確認
• 応答が遅い → より軽量なモデル（Gemini Flash）を試す

質問やバグ報告は GitHub Issues までお寄せください。
"""
    
    dlg = wx.lib.scrolledpanel.ScrolledPanel(parent, size=(600, 500))
    sizer = wx.BoxSizer(wx.VERTICAL)
    
    text_ctrl = wx.TextCtrl(
        dlg, 
        value=help_text,
        style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP,
        size=(580, 450)
    )
    text_ctrl.SetFont(wx.Font(9, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    
    sizer.Add(text_ctrl, 1, wx.ALL | wx.EXPAND, 10)
    
    btn = wx.Button(dlg, wx.ID_OK, "閉じる")
    sizer.Add(btn, 0, wx.ALL | wx.CENTER, 10)
    
    dlg.SetSizer(sizer)
    dlg.SetupScrolling()
    
    frame = wx.Frame(parent, title="AI Assistant ヘルプ", size=(620, 520))
    frame.SetIcon(wx.ArtProvider.GetIcon(wx.ART_HELP, wx.ART_FRAME_ICON))
    
    panel = wx.Panel(frame)
    frame_sizer = wx.BoxSizer(wx.VERTICAL)
    
    help_text_ctrl = wx.TextCtrl(
        panel,
        value=help_text,
        style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_WORDWRAP
    )
    help_text_ctrl.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
    
    close_btn = wx.Button(panel, wx.ID_CLOSE, "閉じる")
    close_btn.Bind(wx.EVT_BUTTON, lambda e: frame.Close())
    
    frame_sizer.Add(help_text_ctrl, 1, wx.ALL | wx.EXPAND, 10)
    frame_sizer.Add(close_btn, 0, wx.ALL | wx.CENTER, 10)
    
    panel.SetSizer(frame_sizer)
    frame.Show()

def wait_for_coder_ready(config_manager):
    """Coderが起動するまで待機してからメニューを追加"""
    def check_coder():
        max_attempts = 30  # 最大30秒待機
        attempt = 0
        
        while attempt < max_attempts:
            try:
                # すべてのトップレベルウィンドウをチェック
                for window in wx.GetTopLevelWindows():
                    if "CoderFrame" in str(type(window)) and window.IsShown():
                        # Coderフレームが見つかった
                        wx.CallAfter(add_menu_to_coder, window, config_manager)
                        return
                        
                time.sleep(1)
                attempt += 1
                
            except Exception as e:
                print(f"AI Coder Assistant: Coder検出エラー - {e}")
                break
                
        print("AI Coder Assistant: Coderフレームの検出に失敗しました")
    
    # バックグラウンドスレッドで実行
    threading.Thread(target=check_coder, daemon=True).start()

def on_app_ready():
    """PsychoPyアプリケーション準備完了時の処理"""
    if ai_coder_assistant is None:
        return
    
    try:
        config_manager = ai_coder_assistant.ConfigManager()
        
        # 初回起動時のセットアップ
        if not config_manager.get("consent_given"):
            # 少し遅延してからダイアログを表示（UIが完全に準備されるまで待つ）
            wx.CallLater(2000, show_welcome_dialog, config_manager)
        
        # Coderの起動を待ってメニューを追加
        wait_for_coder_ready(config_manager)
        
        print("AI Coder Assistant: 正常に初期化されました")
        
    except Exception as e:
        print(f"AI Coder Assistant: 初期化エラー - {e}")

def on_coder_window_create(event):
    """Coderウィンドウ作成時のイベントハンドラー"""
    try:
        window = event.GetWindow()
        if window and "CoderFrame" in str(type(window)):
            if ai_coder_assistant:
                config_manager = ai_coder_assistant.ConfigManager()
                if config_manager.get("consent_given"):
                    # 少し遅延してからメニューを追加（ウィンドウが完全に初期化されるまで待つ）
                    wx.CallLater(500, add_menu_to_coder, window, config_manager)
        
        # イベントを継続
        event.Skip()
        
    except Exception as e:
        print(f"AI Coder Assistant: ウィンドウ作成イベントエラー - {e}")
        if hasattr(event, 'Skip'):
            event.Skip()

# --- メイン初期化処理 ---
try:
    # wxPythonアプリケーションが利用可能か確認
    if wx.GetApp():
        # 即座に初期化を試行
        wx.CallAfter(on_app_ready)
        
        # ウィンドウ作成イベントもバインド（フォールバック）
        app = wx.GetApp()
        if app:
            app.Bind(wx.EVT_ACTIVATE_APP, lambda e: (on_app_ready(), e.Skip()))
        
        print("AI Coder Assistant: 起動スクリプトが読み込まれました")
    else:
        print("AI Coder Assistant: wxアプリケーションが見つかりません")
        
except Exception as e:
    print(f"AI Coder Assistant: 起動スクリプトエラー - {e}")

# PsychoPy特有の起動完了イベントを待つ（存在する場合）
try:
    import psychopy.app
    if hasattr(psychopy.app, 'startApp'):
        original_startApp = psychopy.app.startApp
        def wrapped_startApp(*args, **kwargs):
            result = original_startApp(*args, **kwargs)
            wx.CallLater(1000, on_app_ready)
            return result
        psychopy.app.startApp = wrapped_startApp
except:
    pass  # PsychoPyのバージョンによっては存在しない可能性