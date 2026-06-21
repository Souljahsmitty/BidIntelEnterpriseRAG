# BidIntel Ch38-Ch43 API Map

This map shows exactly how the frontend pages call the FastAPI backend and which service function runs behind each route.

## Ch38 - Compliance Matrix

Frontend function: `extractComplianceMatrix()` in `frontend/app.js`

Route:

```http
POST /api/compliance/extract
```

Backend route: `compliance_extract()` in `backend/app/main.py`

Service function: `extract_requirements_from_text()` in `backend/app/services/proposal_ops.py`

Good output:

```json
{
  "count": 3,
  "requirements": [
    {
      "requirement_id": "R-001",
      "status": "Open",
      "risk_level": "High"
    }
  ]
}
```

## Ch39 - Requirement Traceability

Frontend function: `renderTraceability()` and `openTrace()` in `frontend/app.js`

Route:

```http
GET /api/compliance/requirements/{requirement_id}/trace
```

Backend route: `compliance_trace()` in `backend/app/main.py`

Service function: `build_requirement_trace()` in `backend/app/services/proposal_ops.py`

The trace object must include `requirement_id`, retrieved evidence with `chunk_id`, a generated response section, and `confidence_score`.

## Ch40 - Proposal Workspace

Frontend function: `renderProposalWorkspace()` in `frontend/app.js`

Routes:

```http
POST /api/proposals
GET /api/proposals/workspace
POST /api/proposals/sections/{section_id}
```

Backend functions: `proposals_create()`, `proposals_workspace()`, `proposals_update_section()`

Service functions: `create_proposal()` and `update_section()`

## Ch41 - Content Library Reuse

Frontend function: `renderContentLibrary()` and `insertLibraryContent()` in `frontend/app.js`

Routes:

```http
GET /api/content-library/search?q=monitoring
POST /api/content-library/insert
```

Service functions: `search_content_library()` and `insert_content()`

Production note: this local chapter uses keyword scoring over approved content. In the production RAG version, this becomes hybrid search over approved content chunks using PostgreSQL + pgvector, BM25, RRF, and reranking.

## Ch42 - Red / Pink / Gold Reviews

Frontend function: `renderReviews()`, `createReviewIssue()`, and `resolveIssue()`

Routes:

```http
POST /api/reviews/issues
GET /api/reviews/issues
POST /api/reviews/issues/{issue_id}
```

Service functions: `create_review_issue()` and `update_review_issue()`

Good output preserves `response_history` so the reviewer can see who changed what and why.

## Ch43 - Proposal Health Dashboard

Frontend function: `renderHealthDashboard()`

Route:

```http
GET /api/proposal-health
```

Service function: `proposal_health()`

The dashboard is calculated from requirement completion, evidence coverage, review resolution, section completion, and risk.
