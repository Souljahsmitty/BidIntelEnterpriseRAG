# Backend Verification Commands

Use this page to prove the Python backend is doing the work under the UI:
health, upload, security scans, chunking, embeddings/vector storage, hybrid
retrieval, reranking, RAG answer generation, bid scoring, audit logs,
proposal operations, and enterprise hardening checks.

## 1. Clean Clone

```bash
git clone https://github.com/Souljahsmitty/BidIntelEnterpriseRAG.git /tmp/BidIntelEnterpriseRAG-verify
cd /tmp/BidIntelEnterpriseRAG-verify
```

## 2. Docker Backend + PostgreSQL/pgvector Path

Docker Compose starts the FastAPI app and a local PostgreSQL database with
pgvector enabled.

```bash
docker compose up --build -d
```

Check the backend health endpoint:

```bash
curl -fsS http://127.0.0.1:8000/health | python3 -m json.tool
```

Good output includes:

```text
"status": "ok"
"mode": "REAL LOCAL APP + REAL POSTGRESQL/PGVECTOR"
```

## 3. Quick API Smoke Test

This proves the core routes respond and the guarded RAG path works.

```bash
BASE_URL=http://127.0.0.1:8000 ./scripts/verify/reviewer_smoke.sh
```

Good output includes:

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

## 4. Full Backend Pipeline Proof

This is the strongest single command. It uploads a fresh test document, proves
the ingestion/RAG internals, runs a bid score from retrieved evidence, checks
security rejection, and verifies proposal workflow endpoints.

```bash
BASE_URL=http://127.0.0.1:8000 SLOW_PROOF_SECONDS=2 python3 scripts/verify/full_pipeline_proof.py
```

Good output includes:

```text
01 health before upload: PASS
02 simulated IAM/RBAC map: PASS
03 document upload -> security scan -> layered chunking -> embeddings -> pgvector: PASS
04 ingestion trace visible: PASS
05 vector DB rows and HNSW index visible: PASS
06 documents API pulls ingested document: PASS
07 request pipeline -> retrieval/RRF/rerank -> Claude mock -> citations/trace: PASS
08 contract bid score from retrieved RAG evidence: PASS
09 prompt injection request blocked: PASS
10 security tests pass/fail evidence: PASS
11 audit log shows who did what and why: PASS
12 proposal workspace created: PASS
13 compliance matrix extracted from test RFP: PASS
14 requirement traceability links requirement to evidence: PASS
15 proposal health dashboard metrics: PASS
16 monitoring alerts and production notification simulation: PASS
FULL PIPELINE PROOF COMPLETE: PASS
```

## 5. Local Python Backend Path With Real pgvector

Use this when you want to run FastAPI from Python while still proving real
PostgreSQL/pgvector rows and the HNSW index. Docker is only used for the
database.

```bash
docker compose up -d postgres
```

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
export USE_REAL_PGVECTOR=true
export USE_BEDROCK=false
export DATABASE_URL='postgresql://bidintel:bidintel_dev_password@127.0.0.1:56550/bidintel'
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8777
```

In a second terminal:

```bash
source .venv/bin/activate
BASE_URL=http://127.0.0.1:8777 python3 scripts/verify/reviewer_smoke.py
BASE_URL=http://127.0.0.1:8777 python3 scripts/verify/full_pipeline_proof.py
```

## 6. Direct Python TestClient Proof

This command does not require a running server. It imports the FastAPI app and
calls the backend directly through `TestClient`. This verifies proposal
operations and enterprise hardening behavior, but it is not the pgvector/HNSW
proof. Use section 4 or 5 for the full vector DB proof.

```bash
source .venv/bin/activate
./scripts/verify/check_proposal_ops.sh
```

Good output includes:

```text
Bootstrap: PASS
Ch38 compliance extract: PASS
Ch39 requirement trace: PASS
Ch40 proposal workspace: PASS
Ch41 content reuse: PASS
Ch42 review workflow: PASS
Ch43 health dashboard: PASS
Audit proof: PASS
BidIntel Ch38-Ch43 proposal operations verification complete.
```

## 7. Enterprise Hardening Tests

```bash
source .venv/bin/activate
python3 -m pytest tests/test_enterprise_hardening.py -v
```

Good output includes passing tests for:

```text
RBAC / tenant isolation
audit logging
classification handling
security scan pass/fail evidence
monitoring alert simulation
deployment checklist behavior
```

## 8. Show The Backend Code Being Tested

When recording verification, open these files before running the commands so
the proof connects code to output.

```bash
nl -ba scripts/verify/full_pipeline_proof.py | sed -n '1,260p'
nl -ba scripts/verify/reviewer_smoke.py | sed -n '1,220p'
nl -ba scripts/verify/check_proposal_ops.py | sed -n '1,240p'
nl -ba backend/app/main.py | sed -n '1,260p'
nl -ba backend/app/workflows/ingest_graph.py | sed -n '1,220p'
nl -ba backend/app/services/chunking.py | sed -n '1,220p'
nl -ba backend/app/services/pgvector_store.py | sed -n '1,220p'
nl -ba backend/app/rag/retriever.py | sed -n '1,220p'
nl -ba backend/app/rag/reranker.py | sed -n '1,180p'
nl -ba backend/app/rag/context_builder.py | sed -n '1,200p'
nl -ba backend/app/security/document_security_scans.py | sed -n '1,220p'
nl -ba backend/app/security/prompt_injection_detector.py | sed -n '1,180p'
nl -ba backend/app/services/bid_scoring.py | sed -n '1,220p'
nl -ba backend/app/eval/phoenix_trace.py | sed -n '1,180p'
nl -ba backend/app/eval/ragas_eval.py | sed -n '1,180p'
```

## 9. Shutdown

```bash
docker compose down -v --remove-orphans
```
