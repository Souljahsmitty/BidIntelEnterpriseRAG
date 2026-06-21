# BidIntel Ch38-Ch43 Local To Production Replacement Guide

The Ch38-Ch43 follow-along has two tracks.

## Track A - Local Runnable Teaching Version

Use this when the learner is building on a laptop without paid cloud resources.

```text
frontend/app.js
    ↓ fetch()
backend/app/main.py
    ↓ service calls
backend/app/services/proposal_ops.py
    ↓ local training store
backend/app/services/store.py
```

What is real:

- the FastAPI routes are real
- the frontend buttons are real
- the service functions are real
- the tests are real
- the audit events are real inside the local app state

What is simulated:

- persistence uses Python lists instead of PostgreSQL tables
- content library search uses keyword scoring instead of full hybrid retrieval
- proposal health uses local state instead of a production reporting table

Why we do this:

- the learner can run the project with no paid AWS account
- the chapter can prove behavior before cloud deployment
- the production swap is visible and controlled

## Track B - Production Enterprise Version

Use this when BidIntel is deployed for a real organization.

```text
frontend/app.js
    ↓ HTTPS fetch()
FastAPI on ECS or App Runner
    ↓ SQLAlchemy repository layer
Amazon RDS PostgreSQL + pgvector
    ↓ retrieval and evidence joins
Bedrock Claude Sonnet
    ↓ answer, scoring, audit
CloudWatch / Phoenix / RAGAS
```

Production replacement steps:

1. Create PostgreSQL tables from `docs/enterprise/proposal_ops_schema.sql`.
2. Replace the Python list store in `backend/app/services/store.py` with a repository module.
3. Use tenant-scoped SQL queries for every route.
4. Store requirement traces and review issues as database rows.
5. Replace keyword content search with approved-content hybrid retrieval.
6. Keep the FastAPI route names stable so the frontend does not need to change.
7. Keep the tests, then add database-backed integration tests.

## Production Repository Interface

The service functions should eventually call a repository object instead of global lists.

```python
class ProposalOpsRepository:
    def insert_requirements(self, tenant_id, document_id, rows): ...
    def list_requirements(self, tenant_id): ...
    def save_requirement_trace(self, tenant_id, trace): ...
    def create_proposal(self, tenant_id, proposal): ...
    def update_section(self, tenant_id, section_id, payload): ...
    def search_approved_content(self, tenant_id, query): ...
    def create_review_issue(self, tenant_id, issue): ...
    def proposal_health(self, tenant_id): ...
```

## How A Beginner Knows The Swap Worked

Local good output:

```text
Database mode: not_used
Ch38 compliance extract: PASS
16 passed
```

Production good output:

```text
Database mode: real_pgvector
requirements rows inserted: 6
requirement_traces rows inserted: 1
proposal_sections rows updated: 1
review_issues rows updated: 1
16 passed
```

If production fails:

```text
psycopg.OperationalError: connection refused
```

Fix:

```bash
docker compose up -d postgres
export DATABASE_URL="postgresql://bidintel:bidintel_dev_password@127.0.0.1:56550/bidintel"
export USE_REAL_PGVECTOR=true
```
