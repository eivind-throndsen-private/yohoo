#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"

if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "No Yohoo Python environment found. Creating .venv..."
    python3 -m venv "$PROJECT_DIR/.venv"
    PYTHON_BIN="$PROJECT_DIR/.venv/bin/python"
    "$PYTHON_BIN" -m pip install --upgrade pip
    "$PYTHON_BIN" -m pip install -r "$PROJECT_DIR/requirements-title-helper.txt"
fi

cd "$PROJECT_DIR"
exec "$PYTHON_BIN" "$PROJECT_DIR/proxy_server.py"
