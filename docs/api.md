# API 概要 (暫定)

現在ライブラリが提供する主な公開コンポーネント:

## CodeAnalyzer
`CodeAnalyzer(config_manager)` はコード文字列を解析し、
 - パターン検出 (Builder へのマッピング候補 / パフォーマンス / ベストプラクティス)
 - (APIキー設定済) LLM での高度なレビュー

戻り値: `AnalysisResult` オブジェクト

### 典型的な使用例
```python
from psychopy_ai_coder_assistant.analyzer import CodeAnalyzer
from psychopy_ai_coder_assistant.config import ConfigManager

config = ConfigManager()
analyzer = CodeAnalyzer(config)
result = analyzer.analyze_code(code_str)
for s in result.suggestions:
    print(s.category, s.title, s.explanation)
```

## ConfigManager
設定ファイル (~/.psychopy/ai_assistant/config.json) を読み取り、APIキーや有効機能を管理。

主なメソッド:
- `get_api_key(provider)`
- `get_active_provider()`
- `get_enabled_features()`
- `is_configured()`

## プラグインエントリ
エントリポイント: `psychopy.plugins` グループ内 `ai_coder_assistant`。
PsychoPy Coder 起動時、利用可能プラグインとして表示されます。

---
今後: 詳細なAPI仕様、データクラス構造、例外ポリシーを追加予定。
