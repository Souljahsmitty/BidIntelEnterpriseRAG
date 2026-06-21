#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${BASE_URL:-http://127.0.0.1:8000}"
export BASE_URL

if command -v python3 >/dev/null 2>&1; then
  python3 scripts/verify/reviewer_smoke.py
elif command -v python >/dev/null 2>&1; then
  python scripts/verify/reviewer_smoke.py
else
  echo "Python is required. Install Python 3.12+ or activate the virtual environment." >&2
  exit 1
fi
