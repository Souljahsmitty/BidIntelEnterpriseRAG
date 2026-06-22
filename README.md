# BidIntel Enterprise RAG + Proposal Operations

BidIntel is a working local proof of an enterprise proposal-intelligence system.
It is not a toy chatbot. It shows how a proposal team can upload RFP evidence,
run guarded RAG, retrieve citations, score bid/no-bid risk, and manage proposal
operations such as compliance matrices, requirement traceability, content reuse,
review issues, and proposal health.

## Quick Run Path

For backend proof commands, start here:

```text
docs/BACKEND_VERIFICATION_COMMANDS.md
```

If Docker is available:

```bash
docker compose up --build
```

Open:

```text
http://127.0.0.1:8000
```

In another terminal:

```bash
BASE_URL=http://127.0.0.1:8000 ./scripts/verify/reviewer_smoke.sh
BASE_URL=http://127.0.0.1:8000 python3 scripts/verify/full_pipeline_proof.py
```

Expected proof:

```text
health endpoint: PASS
RAG ask endpoint: PASS
prompt injection guard: PASS
bid score from RAG evidence: PASS
proposal health dashboard API: PASS
FULL PIPELINE PROOF COMPLETE: PASS
```

## Local Python Path With Real pgvector

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

In another terminal:

```bash
source .venv/bin/activate
BASE_URL=http://127.0.0.1:8777 python3 scripts/verify/reviewer_smoke.py
BASE_URL=http://127.0.0.1:8777 python3 scripts/verify/full_pipeline_proof.py
python3 -m pytest tests/test_enterprise_hardening.py -v
```

## What Works Locally

- Frontend pages served by FastAPI
- Document upload and chat attachment handling
- Prompt-injection, PII, secret, RBAC, tenant, and classification checks
- Layered chunking, embeddings, hybrid retrieval, RRF, reranking, citations
- RAGAS/Phoenix-style local evaluation and trace objects
- Bid/no-bid scoring from retrieved evidence
- Proposal operations: compliance matrix, traceability, workspace, content library, reviews, health dashboard
- Docker Compose path for PostgreSQL + pgvector

## Local Mock vs Production Equivalent

- Local mock: Claude Sonnet Bedrock response, deterministic embeddings, local Phoenix/RAGAS-style scoring.
- Real local: FastAPI routes, upload handling, prompt-injection defense, layered chunking, RRF, reranking, citations, audit logs, browser UI.
- Production equivalent: AWS Bedrock, RDS PostgreSQL + pgvector, Phoenix, RAGAS, IAM Identity Center, Secrets Manager, CloudWatch.

See:

```text
docs/BidIntelEnterpriseRAG_Install_Companion.pdf
docs/BACKEND_VERIFICATION_COMMANDS.md
docs/VERIFICATION_GUIDE.md
docs/enterprise/proposal_ops_local_to_production.md
docs/enterprise/proposal_ops_schema.sql
```
