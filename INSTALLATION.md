# Installation Guide

## Prerequisites

- Python 3.8 or higher
- PsychoPy 2023.1.0 or higher
- An API key from one of the supported providers:
  - OpenAI (GPT-4/3.5)
  - Anthropic (Claude)
  - Google (Gemini)

## Installation Methods

### Method 1: Install from PyPI (Recommended)

```bash
pip install psychopy-ai-coder-assistant
```

### Method 2: Install from Source

1. Clone the repository:
```bash
git clone https://github.com/nekoare/psychopy-ai-coder-assistant.git
cd psychopy-ai-coder-assistant
```

2. Install in development mode:
```bash
pip install -e .
```

#### Standalone PsychoPy (内部 Python) で開発版を使う場合

PsychoPy Standalone は自身の Python を同梱しているため、その Python 実行ファイルを直接使ってインストールしてください。

1. Standalone PsychoPy を起動し Coder Shell で:
  ```python
  import sys; print(sys.executable)
  ```
  例: `/opt/PsychoPy/python`

2. そのパスを使ってインストール:
  ```bash
  export PY_APP=/opt/PsychoPy/python    # 上記で得たパス
  git clone https://github.com/nekoare/psychopy-ai-coder-assistant.git
  cd psychopy-ai-coder-assistant
  "$PY_APP" -m pip install -e .
  ```

3. Standalone PsychoPy を再起動 → Tools メニューに AI Assistant があれば成功。

4. 不要になったらアンインストール:
  ```bash
  "$PY_APP" -m pip uninstall psychopy-ai-coder-assistant
  ```

5. 開発変更を即反映したくない場合（固定インストール）:
  ```bash
  "$PY_APP" -m pip install .
  ```

### Method 3: Install Dependencies Only

If you want to install just the dependencies:

```bash
pip install psychopy>=2023.1.0 requests>=2.25.0 wxpython>=4.1.0
pip install openai>=1.0.0  # For OpenAI support
pip install anthropic>=0.7.0  # For Anthropic support
pip install google-generativeai>=0.3.0  # For Google support
```

## Configuration

### 1. API Key Setup

After installation, you'll need to configure your API keys:

1. Open PsychoPy
2. Go to the Coder interface
3. From the menu: **Tools → AI Assistant Settings**
4. Enter your API key for your preferred provider
5. Select the provider from the dropdown

### 2. Obtaining API Keys

#### OpenAI API Key
1. Visit https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

#### Anthropic API Key
1. Visit https://console.anthropic.com/
2. Sign in or create an account
3. Go to "API Keys" section
4. Generate a new key (starts with `sk-ant-`)

#### Google API Key
1. Visit https://aistudio.google.com/app/apikey
2. Sign in with your Google account
3. Create an API key
4. Copy the key

### 3. Privacy Settings

Configure privacy and analysis features:

- **Builder Mapping**: Enable suggestions for Builder components
- **Performance Optimization**: Enable performance improvement suggestions
- **Best Practices**: Enable PsychoPy best practice recommendations

## Verification

To verify the installation:

1. Open PsychoPy Coder
2. Look for "AI Assistant" items in the Tools menu
3. Check for the AI Assistant button in the toolbar
4. Try analyzing a simple script

## Troubleshooting

### Common Issues

#### 1. Plugin Not Loading
- Ensure PsychoPy version is 2023.1.0 or higher
- Check that the plugin is installed in the correct Python environment
- Restart PsychoPy completely

#### 2. API Key Issues
- Verify the API key format is correct
- Check that the API key has sufficient credits/quota
- Ensure network connectivity to API endpoints

#### 3. Import Errors
```bash
# If you get import errors, try reinstalling dependencies:
pip uninstall psychopy-ai-coder-assistant
pip install --force-reinstall psychopy-ai-coder-assistant
```

#### 4. wxPython Issues
```bash
# On some systems, wxPython may need to be installed separately:
pip install wxpython
```

### Platform-Specific Notes

#### macOS
- May need to install wxPython using conda:
```bash
conda install wxpython
```

#### Linux
- Install wxPython dependencies:
```bash
sudo apt-get install libgtk-3-dev libwebkitgtk-3.0-dev
```

#### Windows
- Usually works out of the box with pip install

## Uninstalling

To remove the plugin:

```bash
pip uninstall psychopy-ai-coder-assistant
```

Configuration files will remain in `~/.psychopy/ai_assistant/` and can be manually deleted if desired.

## Getting Help

- Check the [GitHub Issues](https://github.com/nekoare/psychopy-ai-coder-assistant/issues)
- Review the [Documentation](README.md)
- Post questions on the PsychoPy forums with the tag `ai-assistant`