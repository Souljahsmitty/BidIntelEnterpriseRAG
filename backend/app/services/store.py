from __future__ import annotations

DOCUMENTS: list[dict] = []
CHUNKS: list[dict] = []
AUDIT_LOGS: list[dict] = []
TRACES: dict[str, dict] = {}
REVIEW_QUEUE: list[dict] = []
INGESTION_TRACES: list[dict] = []
REQUIREMENTS: list[dict] = []
REQUIREMENT_TRACES: list[dict] = []
PROPOSALS: list[dict] = []
PROPOSAL_SECTIONS: list[dict] = []
CONTENT_LIBRARY: list[dict] = []
REVIEW_ISSUES: list[dict] = []
NEXT_DOC = 123
NEXT_CHUNK = 0
