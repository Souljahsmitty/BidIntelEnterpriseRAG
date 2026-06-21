#!/usr/bin/env bash
set -euo pipefail

export USE_REAL_PGVECTOR="${USE_REAL_PGVECTOR:-false}"
export USE_BEDROCK="${USE_BEDROCK:-false}"
export PYTHONPATH="$PWD"

./.venv/bin/python scripts/verify/check_proposal_ops.py
./.venv/bin/python -m pytest tests/test_enterprise_hardening.py -v

echo "BidIntel proposal operations script and tests complete."
