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

echo "Starting TimePilot AI on http://localhost:8000..."
exec "$PYTHON" run.py --serve --port 8000

echo "Starting TimePilot AI on http://localhost:8000..."
exec "$PYTHON" run.py --serve --port 8000

