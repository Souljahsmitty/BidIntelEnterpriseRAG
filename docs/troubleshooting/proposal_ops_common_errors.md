# Proposal Operations Common Errors

## Database Connection Refused

Symptom:

```text
connection refused on port 56550
```

Cause: Docker/PostgreSQL is not running.

Fix:

```bash
docker compose up -d postgres
```

or:

```bash
export USE_REAL_PGVECTOR=false
```

## Uvicorn Not Found

Symptom:

```text
No module named uvicorn
```

Cause: using system Python instead of project virtual environment.

Fix:

```bash
./.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 18143
```

## Empty Compliance Matrix

Symptom: no requirements appear.

Cause: the uploaded file does not include clear requirement language.

Fix: use RFP language containing terms like `shall`, `must`, `offeror`, or `contractor shall`.
