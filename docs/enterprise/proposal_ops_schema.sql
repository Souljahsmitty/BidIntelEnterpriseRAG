-- BidIntel Ch38-Ch43 proposal operations schema
-- Teaching note:
-- The local follow-along stores these rows in Python lists so the project runs
-- without a paid database. In production, these tables live in PostgreSQL.

CREATE TABLE requirements (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    rfp_document_id TEXT NOT NULL,
    requirement_id TEXT NOT NULL,
    requirement_text TEXT NOT NULL,
    section TEXT NOT NULL,
    owner TEXT NOT NULL DEFAULT 'Unassigned',
    status TEXT NOT NULL DEFAULT 'Open',
    risk_level TEXT NOT NULL,
    evidence_summary TEXT NOT NULL DEFAULT 'Not traced yet',
    confidence_score NUMERIC(4, 2) NOT NULL DEFAULT 0.00,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX requirements_tenant_status_idx
    ON requirements (tenant_id, status);

CREATE TABLE requirement_traces (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    requirement_id TEXT NOT NULL REFERENCES requirements(id),
    source_rfp_text TEXT NOT NULL,
    retrieved_evidence JSONB NOT NULL,
    proposed_response_section TEXT NOT NULL,
    confidence_score NUMERIC(4, 2) NOT NULL,
    score_reason TEXT NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE proposals (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    name TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'In Progress',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE proposal_sections (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    proposal_id TEXT NOT NULL REFERENCES proposals(id),
    volume TEXT NOT NULL,
    section_title TEXT NOT NULL,
    assigned_to TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'Drafting',
    percent_complete INTEGER NOT NULL DEFAULT 0,
    content TEXT NOT NULL DEFAULT '',
    linked_requirements JSONB NOT NULL DEFAULT '[]',
    evidence_refs JSONB NOT NULL DEFAULT '[]'
);

CREATE TABLE content_library (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    content_type TEXT NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    approved BOOLEAN NOT NULL DEFAULT false,
    tags JSONB NOT NULL DEFAULT '[]',
    evidence_refs JSONB NOT NULL DEFAULT '[]'
);

CREATE TABLE review_issues (
    id TEXT PRIMARY KEY,
    tenant_id TEXT NOT NULL,
    proposal_section_id TEXT,
    requirement_id TEXT,
    issue TEXT NOT NULL,
    severity TEXT NOT NULL,
    owner TEXT NOT NULL,
    comment TEXT NOT NULL DEFAULT '',
    status TEXT NOT NULL DEFAULT 'Open',
    evidence JSONB NOT NULL DEFAULT '[]',
    response_history JSONB NOT NULL DEFAULT '[]',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX review_issues_tenant_status_idx
    ON review_issues (tenant_id, status);
