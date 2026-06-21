# BidIntel Enterprise RAG Verification Summary

This clean repo package was verified on 2026-06-20.

## Verification Path

```bash
docker compose up --build -d
curl -fsS http://127.0.0.1:8000/health
BASE_URL=http://127.0.0.1:8000 ./scripts/verify/reviewer_smoke.sh
BASE_URL=http://127.0.0.1:8000 python3 scripts/verify/full_pipeline_proof.py
docker compose down
```

## Verified Results

```text
Health endpoint: PASS
Mode: REAL LOCAL APP + REAL POSTGRESQL/PGVECTOR
Database status: connected
Indexes: chunks_embedding_hnsw_idx, chunks_pkey, chunks_tenant_idx
Smoke test: PASS
Full pipeline proof: PASS
```

The smoke test proves:

- health endpoint
- bootstrap endpoint
- RAG ask endpoint
- prompt injection guard
- bid score from RAG evidence
- proposal workspace API
- proposal health dashboard API
- simulated IAM/RBAC map
- document upload security scan
- ingestion trace
- vector DB row/index proof
- request pipeline with citations and trace
- contract bid score from retrieved evidence
- security pass/fail evidence
- audit log access
- compliance matrix extraction
- requirement traceability
- monitoring alert simulation

The repo runs locally with real PostgreSQL/pgvector in Docker and a local
Claude Sonnet/Bedrock simulation for cost-free review.
