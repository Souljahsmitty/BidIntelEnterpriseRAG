# BidIntel Ch38-Ch43 Click-By-Click Build Path

This is the slow path for a zero-knowledge learner. The video should show these same commands, files, and checks.

## 1. Open The Project

```bash
cd "/Users/adamsmith/Documents/editing the V8 BidIntel video to truly be a follow along video/live_builds/bidintel_ch21_ch26_full_app_integration_20260620"
code .
```

Good output: VS Code opens the BidIntel project folder.

## 2. Create The Proposal Operations Files

```bash
mkdir -p backend/app/services scripts/verify docs/beginner docs/enterprise docs/troubleshooting
touch backend/app/services/proposal_ops.py
touch scripts/verify/check_proposal_ops.py
touch scripts/verify/check_proposal_ops.sh
touch docs/enterprise/proposal_ops_schema.sql
touch docs/enterprise/proposal_ops_api_map.md
touch docs/beginner/proposal_ops_click_by_click.md
```

Good output: each file appears in the folder tree.

## 3. Wire The Backend

Open `backend/app/main.py`, then add routes for:

```text
POST /api/compliance/extract
GET  /api/compliance/requirements
GET  /api/compliance/requirements/{requirement_id}/trace
POST /api/proposals
GET  /api/proposals/workspace
GET  /api/content-library/search
POST /api/reviews/issues
GET  /api/proposal-health
```

Good output: FastAPI can import the app without crashing.

## 4. Wire The Frontend

Open `frontend/app.js`, then add page renderers:

```text
renderCompliance()
renderTraceability()
renderProposalWorkspace()
renderContentLibrary()
renderReviews()
renderHealthDashboard()
```

Good output: the left navigation can open each new page.

## 5. Start The Local App

```bash
export USE_REAL_PGVECTOR=false
export USE_BEDROCK=false
export PYTHONPATH="$PWD/backend"
./.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 18143
```

Good output:

```text
Application startup complete.
Uvicorn running on http://127.0.0.1:18143
```

## 6. Verify The API

```bash
curl -s http://127.0.0.1:18143/health
curl -s -X POST http://127.0.0.1:18143/api/compliance/extract \
  -F rfp_file=@sample_docs/fresh_mock_contract_rfp.txt
curl -s http://127.0.0.1:18143/api/proposal-health
```

Good output: health returns `{"status":"ok"}` and proposal health returns a `readiness_score`.

## 7. Run The Full Verification

```bash
./scripts/verify/check_proposal_ops.sh
```

Good output:

```text
Ch38 compliance extract: PASS
Ch39 requirement trace: PASS
Ch40 proposal workspace: PASS
Ch41 content reuse: PASS
Ch42 review workflow: PASS
Ch43 health dashboard: PASS
16 passed
```

## Common Failure

Failure:

```text
ModuleNotFoundError: No module named 'backend'
```

Cause: the script is importing `backend.app.main`, so `PYTHONPATH` must point at the project root.

Fix:

```bash
export PYTHONPATH="$PWD"
```
