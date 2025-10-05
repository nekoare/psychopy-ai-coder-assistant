Param(
  [switch]$WithOpenAI
)

Write-Host "[1/4] Cleaning previous build" -ForegroundColor Cyan
Remove-Item -Recurse -Force build,dist -ErrorAction SilentlyContinue

Write-Host "[2/4] Installing deps" -ForegroundColor Cyan
pip install --upgrade pip > $null
pip install . | Out-Null

if ($WithOpenAI) {
  Write-Host "[3/4] Building EXE (OpenAI)" -ForegroundColor Cyan
  pyinstaller -F -n ai-coder-assistant-openai `
    --hidden-import openai `
    --exclude-module psychopy `
    --exclude-module wx `
    --exclude-module wxPython `
    src/psychopy_ai_coder_assistant/cli.py
} else {
  Write-Host "[3/4] Building EXE (minimal)" -ForegroundColor Cyan
  pyinstaller -F -n ai-coder-assistant `
    --exclude-module psychopy `
    --exclude-module wx `
    --exclude-module wxPython `
    --exclude-module google.generativeai `
    --exclude-module tiktoken `
    src/psychopy_ai_coder_assistant/cli.py
}

Write-Host "[4/4] Done. Output in dist/" -ForegroundColor Green