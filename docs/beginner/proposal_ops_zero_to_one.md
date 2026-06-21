# Proposal Operations Zero To One

This chapter block turns BidIntel from a RAG assistant into a proposal operations workspace.

## What You Build

- Compliance Matrix: extracts requirements from an RFP.
- Requirement Traceability: connects a requirement to evidence and a proposed response.
- Proposal Workspace: tracks volumes, owners, draft status, and completion.
- Content Library: reuses approved evidence-backed language.
- Review Workflow: records Red/Pink/Gold team issues and fixes.
- Health Dashboard: calculates readiness from real workflow state.

## Run It

```bash
export USE_REAL_PGVECTOR=false
export USE_BEDROCK=false
export PYTHONPATH="$PWD/backend"
./.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 18143
```

## Verify It

```bash
./scripts/verify/check_proposal_ops.sh
```

Good output ends with:

```text
BidIntel proposal operations script and tests complete.
```

## Common Failure

If PostgreSQL is not running and `USE_REAL_PGVECTOR=true`, the app reports:

```text
unavailable_using_local_fallback
```

Fix:

```bash
docker compose up -d postgres
```

or use local simulation:

```bash
export USE_REAL_PGVECTOR=false
```
