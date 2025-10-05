# PsychoPy AI Coder Assistant - Gemini版

シンプルで使いやすいGoogle Gemini専用のPsychoPy AI Coderアシスタントです。

## 🚀 特徴

### なぜGeminiのみ？
- **🎯 シンプル**: 1つのAIプロバイダーのみで設定が簡単
- **💰 無料**: 月15回まで完全無料で利用可能
- **🌟 高品質**: Google Geminiの優れた分析能力
- **⚡ 高速**: レスポンスが早く、ストレス無し
- **🔒 安全**: プライバシー保護機能を内蔵

## 📁 ファイル構成

```
simple_version/
├── ai_coder_assistant.py     # メインロジック（Gemini専用）
├── startup.py                # PsychoPy起動時処理
├── README_GEMINI_ONLY.md     # この説明書
└── test_sample.py            # 動作確認用サンプル
```

## 🔧 インストール手順

### 1. ファイルの配置

```bash
# PsychoPy設定フォルダに移動
cd ~/.psychopy3

# ファイルをコピー
cp /path/to/ai_coder_assistant.py ~/.psychopy3/
cp /path/to/startup.py ~/.psychopy3/
```

### 2. 依存関係のインストール

```bash
pip install requests
```

### 3. Gemini APIキーの取得

1. https://aistudio.google.com/app/apikey にアクセス
2. Googleアカウントでログイン
3. 「Create API Key」をクリック
4. 生成されたAPIキーをコピー
5. **重要**: 月15回まで無料で利用可能

## 🎯 使用方法

### 1. 初回セットアップ
1. PsychoPyを起動
2. ウェルカムダイアログで「はい」をクリック
3. 設定ダイアログでGemini APIキーを入力
4. 分析機能を選択して保存

### 2. コード分析
1. PsychoPy Coderでスクリプトを開く
2. **メニュー**: `ツール → AIコード分析`
3. **ショートカット**: `Ctrl+Shift+A`
4. **ツールバー**: AIアシスタントボタンをクリック

### 3. 結果の確認
- **Builderタブ**: 手書きコードのBuilderコンポーネント化提案
- **性能タブ**: ループ最適化、タイミング改善など
- **品質タブ**: ベストプラクティス、コード品質向上

## 🔒 プライバシー・セキュリティ機能

### 自動検出・除去される情報
- **APIキー**: `api_key = "sk-..."`
- **データベースURL**: `postgresql://user:pass@host/db`
- **ファイルパス**: `/home/user/secret.txt`
- **メールアドレス**: `researcher@university.edu`
- **その他機密情報**: トークン、パスワードなど

### セキュリティ対策
- HTTPS通信のみ使用
- 送信前のプライバシーリスク評価
- ユーザー同意確認
- 機密情報の自動マスキング

## 🧪 コード例

### 分析前（非効率なコード）
```python
import psychopy.visual as visual
import time

win = visual.Window()
for trial in range(100):
    # ❌ 毎回刺激を作成（遅い）
    text = visual.TextStim(win, text=f"Trial {trial}")
    text.draw()
    win.flip()
    # ❌ 不正確なタイミング
    time.sleep(1.0)
```

### AI提案結果
- **🏗️ Builder**: "TrialHandlerコンポーネントでnReps=100として実装"
- **⚡ 性能**: "TextStimをループ外で作成し、setTextで更新"
- **📋 品質**: "time.sleep()をcore.wait()に変更、定数を定義"

### 改善後のコード
```python
import psychopy.visual as visual
import psychopy.core as core

# ✅ 定数定義
N_TRIALS = 100
TRIAL_DURATION = 1.0

win = visual.Window()
# ✅ 刺激を一度だけ作成
text = visual.TextStim(win, text="")

try:
    for trial in range(N_TRIALS):
        # ✅ テキストのみ更新
        text.setText(f"Trial {trial}")
        text.draw()
        win.flip()
        # ✅ 正確なタイミング
        core.wait(TRIAL_DURATION)
finally:
    # ✅ 適切なクリーンアップ
    win.close()
    core.quit()
```

## ⚙️ 設定オプション

### 分析機能
```python
"builder_mapping"          # Builderコンポーネントマッピング
"performance_optimization" # 性能最適化提案
"best_practices"          # ベストプラクティス提案
```

### Geminiの特徴
- **速度**: 🚀🚀🚀 高速レスポンス（通常2-5秒）
- **品質**: 🌟🌟🌟 高品質な分析結果
- **コスト**: 💰 月15回まで無料
- **制限**: 1回の分析で約1000行のコードまで

## 🛠️ トラブルシューティング

### 1. メニューに項目が表示されない
```bash
# PsychoPyを完全に再起動
# ファイルパスを確認
ls ~/.psychopy3/ai_coder_assistant.py
ls ~/.psychopy3/startup.py
```

### 2. API エラーが発生する
- **APIキー確認**: 正しいキーが入力されているか
- **無料枠確認**: 月15回の制限に達していないか
- **ネットワーク**: インターネット接続を確認

### 3. 分析が遅い・失敗する
- **コードサイズ**: 1000行以下に分割して分析
- **機密情報**: APIキー等が含まれていないか確認
- **構文エラー**: Pythonの構文エラーがないか確認

### 4. プライバシーエラー
```bash
# コードから機密情報を手動で削除
# 一時的な変数名に置き換える
api_key = "your_api_key"  →  api_key = "YOUR_KEY_HERE"
```

## 🎛️ カスタマイズ

### プロンプトの調整
`build_psychopy_prompt()` 関数内のプロンプトテキストを編集して、分析の観点をカスタマイズできます。

```python
def build_psychopy_prompt():
    return """あなたはPsychoPy専門家です。
    
    特に以下の点に注目してください：
    - [あなたの専門分野]の実験に特化した提案
    - [特定の研究手法]に関する最適化
    """
```

### 機密情報パターンの追加
`CodeSanitizer` クラスの `sensitive_patterns` リストに新しいパターンを追加できます。

```python
self.sensitive_patterns = [
    # 既存パターン...
    (r'password\s*=\s*["\'][^"\']+["\']', 'PASSWORD'),
    (r'secret_key\s*=\s*["\'][^"\']+["\']', 'SECRET_KEY'),
]
```

## 📊 Geminiの利用状況管理

### 使用回数の確認
1. https://aistudio.google.com/ にアクセス
2. アカウント情報で使用量を確認
3. 月の途中でリセットされます

### 効率的な利用方法
- **小さなコード**: 関数単位で分析
- **重要な部分**: メインロジックを優先
- **事前チェック**: 構文エラーを修正してから分析

## 💡 ベストプラクティス

### 分析のコツ
1. **準備**: エラーのないコードで分析
2. **焦点**: 改善したい部分を明確にする
3. **段階的**: 提案を一つずつ適用
4. **検証**: 改善後も動作確認を行う

### 無料枠の節約
- **統合**: 複数の小さな関数をまとめて分析
- **計画**: 月の利用計画を立てる
- **効率**: 最も重要なコードを優先

## 🔄 他バージョンとの比較

| 機能 | Gemini版 | 多プロバイダー版 |
|------|----------|-----------------|
| **複雑さ** | シンプル | 高機能 |
| **設定** | APIキーのみ | 複数選択 |
| **コスト** | 月15回無料 | プロバイダー依存 |
| **品質** | 高品質 | プロバイダー依存 |
| **保守性** | 簡単 | 複雑 |

## 📝 ライセンス

MIT License - 自由に使用・改変・配布可能

## 🤝 貢献

改善提案やバグ報告は GitHub Issues までお寄せください。

### よくある質問

**Q: 15回の制限はいつリセットされますか？**
A: 毎月1日にリセットされます。

**Q: 15回を超えて使いたい場合は？**
A: Google Cloud Platformで有料プランに移行できます。

**Q: 企業での利用は可能ですか？**
A: はい、Geminiの利用規約に従って商用利用可能です。

**Q: コードが外部に保存されますか？**
A: Googleのプライバシーポリシーに従い、学習には使用されません。

---

**💡 シンプルで高品質なAI分析を、今すぐ始めましょう！**