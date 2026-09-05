#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
export YDOTOOL_SOCKET="${YDOTOOL_SOCKET:-$RUNTIME_DIR/.ydotool_socket}"

if [[ -x "$ROOT/.venv/bin/python" ]] && "$ROOT/.venv/bin/python" -c "import cv2, mss, PySide6" 2>/dev/null; then
  PYTHON="$ROOT/.venv/bin/python"
else
  PYTHON="python3"
fi
if ! "$PYTHON" -c "import cv2, mss, PySide6" 2>/dev/null; then
  echo "Dependências Python ausentes. Rode: $ROOT/setup-bazzite.sh"
  exit 1
fi

if ! command -v ydotool >/dev/null 2>&1; then
  echo "ydotool não está no PATH. Rode: $ROOT/setup-bazzite.sh"
  exit 1
fi

if [[ ! -S "$YDOTOOL_SOCKET" ]]; then
  if systemctl --user start ydotoold.service 2>/dev/null; then
    sleep 0.4
  fi
fi

if [[ ! -S "$YDOTOOL_SOCKET" ]]; then
  echo "ydotoold não está no ar (socket $YDOTOOL_SOCKET)."
  echo "Rode: $ROOT/setup-bazzite.sh"
  echo "Se o grupo input acabou de ser adicionado, saia e entre de novo no KDE."
  exit 1
fi

exec "$PYTHON" "$ROOT/main.py" "$@"
