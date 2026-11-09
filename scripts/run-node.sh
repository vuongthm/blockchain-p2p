#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT/source"
if [[ -x .venv/bin/python ]]; then
  exec .venv/bin/python app.py "$@"
else
  exec python3 app.py "$@"
fi
