#!/usr/bin/env bash
# ==============================================================================
# CINECLEAR AI // 1-CLICK AUTO-DEPLOY LAUNCHER (Linux / macOS)
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "========================================================================"
echo "   CINECLEAR AI // AGENTIC HOLLYWOOD LEGAL & E&O CLEARANCE SYSTEM       "
echo "========================================================================"
echo ""

# 1. Detect Python 3.10+
if command -v python3 &>/dev/null; then
    PYTHON_BIN="python3"
elif command -v python &>/dev/null; then
    PYTHON_BIN="python"
else
    echo "[!] ERROR: Python 3.10+ is required but was not found."
    echo "    Please install Python from https://www.python.org/downloads/"
    exit 1
fi

# 2. Setup Virtual Environment
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    "$PYTHON_BIN" -m venv .venv
fi

# 3. Activate Virtual Environment
if [ -f ".venv/bin/activate" ]; then
    # shellcheck source=/dev/null
    source .venv/bin/activate
fi

# 4. Run Deploy Orchestrator
python deploy.py "$@"
