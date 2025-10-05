# PsychoPy AI Coder Assistant

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PsychoPy Version](https://img.shields.io/badge/psychopy-2023.1.0+-green.svg)](https://www.psychopy.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An AI-powered extension for PsychoPy Coder that analyzes Python scripts and provides intelligent suggestions for optimization, best practices, and Builder component mapping.

## 🎯 Overview

The PsychoPy AI Coder Assistant helps researchers and developers write more efficient, maintainable PsychoPy experiments by:

- **Analyzing code intent** and suggesting equivalent Builder components
- **Detecting performance bottlenecks** and providing optimization recommendations  
- **Identifying best practice violations** and suggesting improvements
- **Maintaining privacy** by detecting and redacting sensitive information

## ✨ Key Features

### 🧠 Intent Interpretation & Builder Mapping
- Analyzes experimental logic and suggests Builder component equivalents
- Identifies trial loops that could be TrialHandler components
- Recognizes stimulus presentation patterns and recommends appropriate components
- Maps complex experimental designs to Builder workflows

### ⚡ Performance Optimization
- Detects stimulus creation inside loops (major performance issue)
- Suggests vectorized operations using NumPy
- Identifies inefficient timing methods (`time.sleep()` vs `core.wait()`)
- Recommends stimulus and resource pre-loading strategies

### 📋 Best Practices
- Flags magic numbers and suggests named constants
- Identifies missing resource cleanup (`win.close()`, `core.quit()`)
- Recommends proper error handling and code organization
- Suggests frame-based vs. time-based timing approaches

### 🔒 Privacy & Security
- Automatically detects and redacts sensitive information (API keys, URLs, paths)
- Shows privacy warnings before sending code to external services
- Configurable privacy settings and analysis features
- Secure HTTPS communication with AI providers

## 🚀 Quick Start

### Installation

```bash
# 最小（LLM解析・ローカルパターンのみ）
pip install psychopy-ai-coder-assistant

# PsychoPy Coder プラグインとしてフル利用
pip install "psychopy-ai-coder-assistant[psychopy]"
```

### Standalone PsychoPy へのローカルソース導入（未公開開発版）

まだ PyPI に公開していない場合、Standalone PsychoPy が内包する Python を使って直接インストールします。

1. PsychoPy Standalone を一度起動し、Coder の Shell で内部 Python パスを確認:
    ```python
    import sys; print(sys.executable)
    ```
    例: `/opt/PsychoPy/python`

2. そのパスを環境変数に設定し、リポジトリをクローンしてインストール:
    ```bash
    export PY_APP=/opt/PsychoPy/python   # 上で確認したパスに置き換え
    git clone https://github.com/nekoare/psychopy-ai-coder-assistant.git
    cd psychopy-ai-coder-assistant
        # PsychoPy 依存を含める場合
        "$PY_APP" -m pip install -e .[psychopy]
    ```

3. 再度 Standalone PsychoPy を起動し、Tools メニューに AI Assistant が表示されるか確認。

4. API キーを設定（後述）。

補助スクリプト: `scripts/install_standalone.sh` も参照してください。

### Setup

1. **Open PsychoPy Coder**
2. **Configure API**: Go to `Tools → AI Assistant Settings`
3. **Add API Key**: Enter your API key for OpenAI, Anthropic, or Google
4. **Customize Features**: Enable/disable specific analysis types

### Usage

1. **Open any Python script** in PsychoPy Coder
2. **Analyze code**: Click the AI Assistant toolbar button or use `Ctrl+Shift+A`
3. **Review suggestions**: Browse categorized recommendations in the side panel
4. **Apply improvements**: Click suggestions to see detailed explanations and improved code

## 🔧 Supported AI Providers

| Provider | Models | API Key Format |
|----------|--------|----------------|
| **OpenAI** | GPT-4, GPT-3.5 | `sk-...` |
| **Anthropic** | Claude 3 | `sk-ant-...` |
| **Google** | Gemini Pro | Various formats |

## 📊 Example Analysis

**Before (Inefficient Code):**
```python
import psychopy.visual as visual
import time

win = visual.Window()
for trial in range(100):
    # ❌ Creating stimulus every trial (slow!)
    text = visual.TextStim(win, text=f"Trial {trial}")
    text.draw()
    win.flip()
    # ❌ Imprecise timing
    time.sleep(1.0)
```

**After (AI-Optimized Code):**
```python
import psychopy.visual as visual
import psychopy.core as core

# ✅ Constants for maintainability
N_TRIALS = 100
TRIAL_DURATION = 1.0

win = visual.Window()
# ✅ Create stimulus once
text = visual.TextStim(win, text="")

try:
    for trial in range(N_TRIALS):
        # ✅ Update text property only
        text.setText(f"Trial {trial}")
        text.draw()
        win.flip()
        # ✅ Precise timing
        core.wait(TRIAL_DURATION)
finally:
    # ✅ Proper cleanup
    win.close()
    core.quit()
```

**AI Suggestions Generated:**
- 🏗️ **Builder Mapping**: "Consider using TrialHandler component for trial management"
- ⚡ **Performance**: "Move TextStim creation outside loop (5x speed improvement)"
- 📋 **Best Practice**: "Define N_TRIALS constant and add proper cleanup"

## 🛡️ Privacy & Security

### Automatic Data Protection
- **Sensitive Content Detection**: API keys, passwords, file paths automatically redacted
- **Privacy Risk Assessment**: Code analyzed for privacy implications before sending
- **User Consent**: Clear warnings about external data transmission

### Security Features
- **HTTPS Encryption**: All API communications encrypted
- **No Data Storage**: Plugin doesn't store code or analysis results
- **Configurable Privacy**: Fine-grained control over what gets analyzed

## 📁 Project Structure

```
psychopy-ai-coder-assistant/
├── src/psychopy_ai_coder_assistant/
│   ├── __init__.py              # Plugin entry point
│   ├── plugin.py                # Main plugin integration
│   ├── analyzer.py              # Code analysis engine
│   ├── llm_client.py           # Multi-provider LLM interface
│   ├── prompts.py              # Prompt engineering templates
│   ├── patterns.py             # Local pattern detection
│   ├── security.py             # Privacy and security features
│   ├── config.py               # Configuration management
│   └── ui.py                   # wxPython UI components
├── tests/                      # Comprehensive test suite
├── examples/                   # Usage examples
└── scripts/                    # Development tools
```

## 🧪 Development

### Running Tests
```bash
python scripts/run_tests.py
```

### Installing for Development
```bash
git clone https://github.com/nekoare/psychopy-ai-coder-assistant.git
cd psychopy-ai-coder-assistant
pip install -e .
```

### Publishing to Your GitHub (初めて公開する場合の例)
ローカルで作成したこのプロジェクトを GitHub に公開し、他マシンでクローン→Standalone インストールする基本手順。

1. GitHub で空のリポジトリを作成（例: `nekoare/psychopy-ai-coder-assistant`）。
2. ローカルで（まだ `.git` が無い場合）:
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin git@github.com:nekoare/psychopy-ai-coder-assistant.git
    git push -u origin main
    ```
3. バージョンタグ（任意）:
    ```bash
    git tag v0.1.0
    git push origin v0.1.0
    ```
4. 他マシン（Standalone 用）でクローン→内部 Python でインストール:
    ```bash
    export PY_APP=/opt/PsychoPy/python   # 例
    git clone https://github.com/nekoare/psychopy-ai-coder-assistant.git
    cd psychopy-ai-coder-assistant
    "$PY_APP" -m pip install -e .[psychopy]
    ```

PyPI 公開前でもこの手順で利用可能です。`-e` を外せば固定インストールになります。

## 🧩 PsychoPy プラグインとしての利用方法（要点）

1. PsychoPy を起動（Coder 画面）
2. 本パッケージをインストール（pip または Standalone 内部 Python）
3. 再起動後、メニュー / Tools に "AI Assistant" が表示される
4. 分析したいスクリプトを開き、ショートカット `Ctrl+Shift+A`（設定により異なる想定）で解析
5. サイドパネルにカテゴリ別 (Performance / Best Practices / Privacy / Builder Mapping) の提案が出る

問題なく表示されない場合:
- インストール先 Python が PsychoPy 実行時と一致しているか確認
- `python -c "import importlib.metadata as md;print([e.name for e in md.entry_points(group='psychopy.plugins')])"` で `ai_coder_assistant` が含まれるかを確認

## ❓ PyPI とは何か / なぜ使うか

PyPI (Python Package Index) は Python パッケージの公式公開リポジトリです。これに公開することで:
- `pip install psychopy-ai-coder-assistant` だけで簡単インストール
- 依存関係解決（PsychoPy / wxPython など）を自動化
- バージョン管理（0.1.0 → 0.1.1 ...）が統一
公開不要なプライベート配布であれば GitHub からのクローン + `pip install -e .` でも利用可能です。

## 🗂 補助ドキュメント

- `INSTALLATION.md` 詳細インストール
- `RELEASE_CHECKLIST.md` リリース手順
- `CHANGELOG.md` 変更履歴
- `CONTRIBUTING.md` 開発貢献ガイド


## 📚 Documentation

- **[Installation Guide](INSTALLATION.md)** - Detailed setup instructions
- **[API Documentation](docs/api.md)** - Developer reference
- **[Privacy Policy](docs/privacy.md)** - Data handling practices
- **[Contributing](CONTRIBUTING.md)** - Development guidelines

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on:
- Setting up the development environment
- Running tests and code quality checks
- Submitting pull requests
- Reporting issues

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **PsychoPy Team** for the excellent framework and plugin architecture
- **AI Provider Teams** (OpenAI, Anthropic, Google) for powerful language models
- **wxPython Project** for the GUI framework
- **Psychology Research Community** for feedback and use cases

## 📞 Support

- **🐛 Bug Reports**: [GitHub Issues](https://github.com/nekoare/psychopy-ai-coder-assistant/issues)
- **💡 Feature Requests**: [GitHub Discussions](https://github.com/nekoare/psychopy-ai-coder-assistant/discussions)  
- **❓ Questions**: PsychoPy Forum with `ai-assistant` tag
- **📧 Email**: support@psychopy-ai-assistant.com

---

**Made with ❤️ for the PsychoPy community**