# Windows 向け 単体 EXE 化ガイド

本プロジェクトを Python 環境無しで実行できる `ai-coder-assistant.exe` にパッケージする手順です。

## 1. 前提環境 (Windows)
```
Python 3.11 (推奨) 64bit
pip install --upgrade pip
git clone https://github.com/nekoare/psychopy-ai-coder-assistant.git
cd psychopy-ai-coder-assistant
```

最小依存のみで十分な場合:
```
pip install .
```
LLM を使う場合 (任意):
```
pip install .[llm_extras]
```

## 2. PyInstaller インストール
```
pip install pyinstaller
```

## 3. 単一ファイル EXE ビルド (パターン検出のみ)
```
pyinstaller -F -n ai-coder-assistant \
  --exclude-module psychopy \
  --exclude-module wx \
  --exclude-module wxPython \
  --exclude-module google.generativeai \
  --exclude-module tiktoken \
  src/psychopy_ai_coder_assistant/cli.py
```

生成物: `dist/ai-coder-assistant.exe`

## 4. LLM を含めたい場合
OpenAI だけ含める例 (ファイルサイズ抑制):
```
pyinstaller -F -n ai-coder-assistant-openai \
  --hidden-import=openai \
  --exclude-module psychopy --exclude-module wx --exclude-module google.generativeai --exclude-module tiktoken \
  src/psychopy_ai_coder_assistant/cli.py
```

Google / Anthropic も必要なら `--hidden-import anthopic` / `--hidden-import google.generativeai` を追加。サイズ増大に注意。

## 5. 実行例
```
dist\ai-coder-assistant.exe path\to\script.py --json > suggestions.json
```

LLM を利用したい場合 (OpenAI):
```
set OPENAI_API_KEY=sk-xxxxx
dist\ai-coder-assistant-openai.exe experiment.py
```

## 6. 出力形式
- デフォルト: テキスト (優先度順)
- JSON: `--json` フラグ利用

## 7. 失敗しやすいポイント
| 症状 | 原因 | 対処 |
|------|------|------|
| exe 起動が遅い | ワンファイル展開待ち | 待つ (初回のみ) |
| ModuleNotFoundError | hidden-import 不足 | エラーモジュールを hidden-import 追加 |
| サイズが大きい | 使わない LLM / GUI を含んでいる | exclude-module 追加 |

## 8. セキュリティ / API キー
API キーは exe に埋め込まず、環境変数 or 引数 `--api-key` で渡す。漏洩リスク低減のため `--api-key` では履歴に残る可能性があるので極力環境変数を推奨。

## 9. 自動化 (PowerShell スクリプト)
`scripts/build_windows_exe.ps1` を参照: 最小 / OpenAI 版をまとめて出力。

---
より高度な最適化 (UPX 圧縮, Nuitka, PyOxidizer) は将来検討可能です。
