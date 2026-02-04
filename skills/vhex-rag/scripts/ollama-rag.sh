#!/bin/bash
set -e

SCRIPT_DIR=$(dirname "$(realpath "$0")")
PY_SCRIPT="$SCRIPT_DIR/ollama-rag.py"
VENV_PYTHON="/home/vhex/.openclaw/workspace/.venv/bin/python"

if [[ -x "$VENV_PYTHON" ]]; then
  "$VENV_PYTHON" "$PY_SCRIPT" "$@"
else
  python3 "$PY_SCRIPT" "$@"
fi
