#!/usr/bin/env bash
# Helper script to install the project into a Standalone PsychoPy internal Python.
# Usage:
#   ./scripts/install_standalone.sh /path/to/Standalone/PsychoPy/python [--dev]
# Example:
#   ./scripts/install_standalone.sh /opt/PsychoPy/python --dev

set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 /path/to/psychopy/python [--dev]" >&2
  exit 1
fi

PY_APP="$1"; shift || true
MODE="normal"
if [ "${1:-}" = "--dev" ]; then
  MODE="dev"
fi

if [ ! -x "$PY_APP" ]; then
  echo "Error: '$PY_APP' is not an executable Python path." >&2
  exit 2
fi

echo "[INFO] Upgrading build tooling..."
"$PY_APP" -m pip install --upgrade pip setuptools wheel >/dev/null

echo "[INFO] Installing psychopy-ai-coder-assistant ($MODE mode)..."
if [ "$MODE" = "dev" ]; then
  "$PY_APP" -m pip install -e .
else
  "$PY_APP" -m pip install .
fi

echo "[INFO] Verifying installation..."
"$PY_APP" - <<'PY'
import importlib, sys
try:
    import psychopy_ai_coder_assistant as m
    print('[OK] Imported psychopy_ai_coder_assistant from', m.__file__)
except Exception as e:
    print('[FAIL] Could not import package:', e)
    sys.exit(1)
PY

echo "[DONE] Installation complete. Restart Standalone PsychoPy to load the plugin."