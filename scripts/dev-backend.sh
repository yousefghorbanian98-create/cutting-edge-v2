#!/usr/bin/env bash
# Cutting Edge v2 — start the AI engine backend (Linux / macOS / WSL).
#
# Boots the FastAPI app as the installed `ai_engine` package:
#     uvicorn ai_engine.main:app
#
# Env overrides:
#   CE_VENV_DIR   venv directory        (default: ai-engine/.venv)
#   CE_HOST       bind host             (default: 127.0.0.1)
#   CE_PORT       bind port             (default: 8001)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AI_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/ai-engine"
VENV_DIR="${CE_VENV_DIR:-$AI_DIR/.venv}"
HOST="${CE_HOST:-127.0.0.1}"
PORT="${CE_PORT:-8001}"

cd "$AI_DIR"

# 1. Create the venv if needed.
if [ ! -f "$VENV_DIR/bin/python" ]; then
  echo "[dev-backend] Creating virtualenv at $VENV_DIR"
  python3 -m venv "$VENV_DIR"
fi

# 2. Bootstrapping: make sure the package and its web deps are importable.
if ! "$VENV_DIR/bin/python" -c "import ai_engine.main, uvicorn, fastapi, psutil, requests" >/dev/null 2>&1; then
  echo "[dev-backend] Installing web deps + editable package into $VENV_DIR"
  "$VENV_DIR/bin/python" -m pip install --quiet --upgrade pip
  # The full media/AI stack is heavy; we install only the deps needed to boot
  # here. `requirements.txt` is used for a full production install (CI / Users).
  "$VENV_DIR/bin/python" -m pip install --quiet \
    "fastapi==0.115.6" "uvicorn[standard]==0.32.1" "python-multipart==0.0.18" \
    "pydantic==2.10.4" "python-dotenv==1.0.1" "psutil==6.1.0" "requests==2.32.3"
  "$VENV_DIR/bin/python" -m pip install --quiet --no-deps -e .
fi

# 3. Run.
echo "[dev-backend] Starting backend on $HOST:$PORT"
exec "$VENV_DIR/bin/python" -m uvicorn ai_engine.main:app --host "$HOST" --port "$PORT"
