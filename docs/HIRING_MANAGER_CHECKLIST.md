# Hiring Manager Checklist

This checklist is the fast review path for BidIntel.

## 1. Clone Or Unzip

Open a terminal in the repo root.

```bash
ls
```

Expected files:

```text
Dockerfile
docker-compose.yml
README.md
backend/
frontend/
tests/
scripts/
docs/
sample_docs/
```

## 2. Start The Full Local Stack

```bash
docker compose up --build
```

Expected proof:

```text
postgres Healthy
app Started
```

Open:

```text
http://127.0.0.1:8000
```

## 3. Verify Health And pgvector

```bash
curl http://127.0.0.1:8000/health
```

Expected proof:

```json
{
  "status": "ok",
  "mode": "REAL LOCAL APP + REAL POSTGRESQL/PGVECTOR",
  "database": {
    "enabled": true,
    "status": "connected",
    "indexes": ["chunks_embedding_hnsw_idx", "chunks_pkey", "chunks_tenant_idx"]
  }
}
```

## 4. Run Reviewer Smoke Test

```bash
python3 scripts/verify/reviewer_smoke.py
```

Expected proof:

```text
health endpoint: PASS
bootstrap endpoint: PASS
RAG ask endpoint: PASS
prompt injection guard: PASS
bid score from RAG evidence: PASS
proposal workspace API: PASS
proposal health dashboard API: PASS
BidIntel reviewer smoke test complete.
```

## 5. Run Test Suite

For local Python:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest tests/test_enterprise_hardening.py -v
```

Expected proof:

```text
16 passed
```

## 6. What To Click In The Browser

Open `http://127.0.0.1:8000`, then inspect:

- Documents: upload and attachment flow
- AI Assistant: guarded RAG ask flow
- Verification: IAM/RBAC simulation, ingestion trace, vector DB viewer
- Bid / No-Bid: score from retrieved evidence
- Compliance Matrix: requirement extraction
- Traceability: requirement -> evidence -> response -> confidence
- Proposal Workspace: proposal volumes and section status
- Content Library: approved language reuse
- Reviews: Red/Pink/Gold issue workflow
- Health Dashboard: readiness score factors
- Audit Logs: who did what and why

## 7. Real vs Simulated Boundary

Real local:

- FastAPI backend
- Browser frontend
- Docker Compose stack
- PostgreSQL + pgvector
- Upload/ask/scoring/proposal APIs
- Security checks
- Tests and smoke scripts

Simulated for no-cost local review:

- Claude Sonnet on Amazon Bedrock
- AWS IAM Identity Center
- AWS Secrets Manager
- CloudWatch/Phoenix/RAGAS external SaaS connections

Production equivalents are documented in:

```text
docs/enterprise/proposal_ops_local_to_production.md
docs/enterprise/proposal_ops_schema.sql
docs/enterprise/proposal_ops_api_map.md
```

## Verification Status

Last local clean-package verification:

```text
docker compose up --build -d: PASS
curl /health: PASS
python3 scripts/verify/reviewer_smoke.py: PASS
```
