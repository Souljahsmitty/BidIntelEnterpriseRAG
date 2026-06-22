# BidIntel Verification Guide

This guide explains what works, how to run it, and what proof to expect.

For the complete pasteable backend command list, use:

```text
docs/BACKEND_VERIFICATION_COMMANDS.md
```

## Fastest Docker Path

```bash
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000
```

Run the smoke test in another terminal:

```bash
BASE_URL=http://127.0.0.1:8000 ./scripts/verify/reviewer_smoke.sh
BASE_URL=http://127.0.0.1:8000 python3 scripts/verify/full_pipeline_proof.py
```

Expected proof:

```text
health endpoint: PASS
bootstrap endpoint: PASS
RAG ask endpoint: PASS
prompt injection guard: PASS
bid score from RAG evidence: PASS
proposal health dashboard API: PASS
BidIntel smoke test complete.
FULL PIPELINE PROOF COMPLETE: PASS
```

## Local Python Path With Real pgvector

Use this if you want to run FastAPI directly from Python while still proving
PostgreSQL/pgvector rows and the HNSW index. Docker is used only for the
database.

```bash
docker compose up -d postgres
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
export USE_REAL_PGVECTOR=true
export USE_BEDROCK=false
export DATABASE_URL='postgresql://bidintel:bidintel_dev_password@127.0.0.1:56550/bidintel'
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8777
```

Then in another terminal:

```bash
source .venv/bin/activate
BASE_URL=http://127.0.0.1:8777 python3 scripts/verify/reviewer_smoke.py
BASE_URL=http://127.0.0.1:8777 python3 scripts/verify/full_pipeline_proof.py
python3 -m pytest tests/test_enterprise_hardening.py -v
```

## What Is Real In This Repo

- FastAPI backend routes
- Browser frontend served by FastAPI
- Upload handling and attachment verification
- Prompt injection, PII, secret, classification, tenant, and RBAC checks
- Layered chunking
- Hybrid retrieval with RRF and reranking
- Citation packaging
- RAGAS/Phoenix-style local evaluation and trace objects
- Bid/no-bid scoring from retrieved evidence
- Proposal operations: compliance matrix, traceability, workspace, content library, review workflow, and health dashboard
- PostgreSQL + pgvector path through Docker Compose
- End-to-end proof script for IAM/RBAC simulation, document upload, ingestion,
  vector DB rows, RAG request flow, bid scoring, security tests, audit logs,
  proposal ops, compliance extraction, traceability, and monitoring.

## What Is Simulated Locally

- Claude Sonnet on Amazon Bedrock is represented by a local mock unless `USE_BEDROCK=true`.
- AWS IAM Identity Center and Secrets Manager are represented by runbooks and local RBAC checks.
- RAGAS and Phoenix are local equivalents that expose the same evaluation and trace ideas without requiring external services.

## Why That Is Acceptable For Review

The repo proves the application architecture and engineering workflow locally without requiring paid AWS credentials. Production swap boundaries are documented in:

```text
docs/enterprise/proposal_ops_local_to_production.md
docs/enterprise/proposal_ops_schema.sql
docs/enterprise/proposal_ops_api_map.md
```
