#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
elif command -v python >/dev/null 2>&1; then
  PYTHON=python
else
  echo "Python 3.10+ is required. Install it from https://www.python.org/downloads/" >&2
  exit 1
fi
if ! "$PYTHON" -c 'import riva.client' >/dev/null 2>&1; then
  echo "Installing NVIDIA speech-to-text client for first use..."
  if ! "$PYTHON" -m pip install -r backend/requirements.txt; then
    echo "WARNING: STT dependency could not be installed. Calendar/text agent will still start." >&2
    echo "To enable voice later, run: $PYTHON -m pip install -r backend/requirements.txt" >&2
  fi
fi
exec "$PYTHON" -m backend.app
