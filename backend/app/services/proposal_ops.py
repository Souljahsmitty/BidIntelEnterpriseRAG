from __future__ import annotations

import re
import uuid
from collections import Counter

from backend.app.rag.bedrock_client import MockClaudeSonnetBedrock
from backend.app.rag.reranker import rerank
from backend.app.rag.retriever import hybrid_search
from backend.app.security.rbac_guard import can
from backend.app.services.audit_logger import audit_event
from backend.app.services.store import (
    CONTENT_LIBRARY,
    PROPOSAL_SECTIONS,
    PROPOSALS,
    REQUIREMENT_TRACES,
    REQUIREMENTS,
    REVIEW_ISSUES,
)


DEFAULT_TENANT = "tenant_acme"

REQUIREMENT_PATTERNS = [
    r"\b(?:contractor|offeror|proposal|vendor)\s+(?:shall|must|required to)\s+[^.\n]+[.]?",
    r"\b(?:shall|must|required)\s+[^.\n]+[.]?",
]

DEFAULT_PROPOSAL_SECTIONS = [
    ("Technical Volume", "Technical Approach", "Tech Lead"),
    ("Technical Volume", "Security Architecture", "Security Lead"),
    ("Management Volume", "Staffing Plan", "Capture Manager"),
    ("Management Volume", "Risk Management", "Program Manager"),
    ("Past Performance", "Relevant Experience", "Proposal Writer"),
    ("Pricing Narrative", "Cost Narrative", "Finance"),
]


def _short_id(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _tenant_rows(rows: list[dict], tenant_id: str) -> list[dict]:
    return [row for row in rows if row.get("tenant_id") == tenant_id]


def _risk_for_requirement(text: str) -> str:
    lowered = text.lower()
    if any(term in lowered for term in ["fedramp", "clearance", "secret", "transition", "30 days", "compliance"]):
        return "High"
    if any(term in lowered for term in ["monthly", "staff", "metrics", "report", "response"]):
        return "Medium"
    return "Low"


def _section_for_requirement(text: str, index: int) -> str:
    match = re.search(r"\b([CLMH]\.\d+(?:\.\d+)?)\b|\b(section\s+\d+(?:\.\d+)?)\b", text, re.I)
    if match:
        return match.group(0).upper()
    return f"REQ-{index:02d}"


def _extract_sentences(text: str) -> list[str]:
    normalized = re.sub(r"\s+", " ", text).strip()
    matches: list[str] = []
    for pattern in REQUIREMENT_PATTERNS:
        matches.extend(re.findall(pattern, normalized, flags=re.I))
    seen = set()
    clean = []
    for item in matches:
        sentence = item.strip()
        key = sentence.lower()
        if key not in seen and len(sentence) > 20:
            seen.add(key)
            clean.append(sentence)
    return clean


def seed_demo_content(tenant_id: str = DEFAULT_TENANT) -> None:
    if not _tenant_rows(CONTENT_LIBRARY, tenant_id):
        CONTENT_LIBRARY.extend(
            [
                {
                    "id": _short_id("LIB"),
                    "tenant_id": tenant_id,
                    "content_type": "Past Performance",
                    "title": "24/7 SOC Monitoring Past Performance",
                    "body": "Provided 24/7 security operations center monitoring, incident triage, escalation, and monthly performance reporting for federal customers.",
                    "approved": True,
                    "tags": ["soc", "monitoring", "cybersecurity"],
                    "evidence_refs": [{"document": "Past_Performance_SOC", "score": 0.93}],
                },
                {
                    "id": _short_id("LIB"),
                    "tenant_id": tenant_id,
                    "content_type": "Win Theme",
                    "title": "Low-Risk Transition Win Theme",
                    "body": "Our transition method reduces schedule risk through a named transition lead, day-one staffing plan, and weekly readiness checkpoints.",
                    "approved": True,
                    "tags": ["transition", "risk", "staffing"],
                    "evidence_refs": [{"document": "Transition_Playbook", "score": 0.88}],
                },
            ]
        )
    if not _tenant_rows(REVIEW_ISSUES, tenant_id):
        REVIEW_ISSUES.append(
            {
                "id": _short_id("REV"),
                "tenant_id": tenant_id,
                "proposal_section_id": None,
                "requirement_id": None,
                "issue": "Technical approach does not yet cite the monitoring SLA evidence.",
                "severity": "High",
                "owner": "adam.davis",
                "comment": "Add source-backed SLA language before Red Team.",
                "status": "Open",
                "evidence": [{"document": "DHS Cyber RFP", "section": "C.3.1"}],
                "response_history": [],
            }
        )


def extract_requirements_from_text(
    text: str,
    *,
    tenant_id: str = DEFAULT_TENANT,
    document_id: str = "uploaded-rfp",
    user: str = "adam.davis",
    role: str = "proposal_writer",
) -> dict:
    permission = can(role, "upload")
    if not permission["allowed"]:
        audit_event("extract_requirements", user, role, "blocked", permission, tenant_id=tenant_id, reason=permission["reason"])
        return {"blocked": True, "guard": permission, "requirements": []}

    sentences = _extract_sentences(text)
    if not sentences:
        sentences = [
            "The contractor shall provide 24/7 cybersecurity monitoring services.",
            "The offeror must document incident escalation procedures.",
            "The contractor shall provide monthly performance reports.",
        ]

    created = []
    for index, sentence in enumerate(sentences, start=1):
        section = _section_for_requirement(sentence, index)
        row = {
            "id": _short_id("REQ"),
            "tenant_id": tenant_id,
            "rfp_document_id": document_id,
            "requirement_id": f"R-{len(_tenant_rows(REQUIREMENTS, tenant_id)) + 1:03d}",
            "requirement_text": sentence,
            "section": section,
            "owner": "Unassigned",
            "status": "Open",
            "risk_level": _risk_for_requirement(sentence),
            "evidence_summary": "Not traced yet",
            "confidence_score": 0.0,
        }
        REQUIREMENTS.append(row)
        created.append(row)

    audit_event(
        "extract_requirements",
        user,
        role,
        "ok",
        {"document_id": document_id, "count": len(created)},
        tenant_id=tenant_id,
        resource_id=document_id,
        reason="requirements_extracted_from_uploaded_rfp",
    )
    return {"tenant_id": tenant_id, "document_id": document_id, "count": len(created), "requirements": created}


def list_requirements(tenant_id: str = DEFAULT_TENANT) -> dict:
    rows = _tenant_rows(REQUIREMENTS, tenant_id)
    high = sum(1 for row in rows if row["risk_level"] == "High")
    complete = sum(1 for row in rows if row["status"] == "Complete")
    return {
        "summary": {"total": len(rows), "high": high, "open": sum(1 for row in rows if row["status"] != "Complete"), "complete": complete},
        "requirements": rows,
    }


def assign_requirement(requirement_id: str, owner: str, status: str, tenant_id: str = DEFAULT_TENANT, user: str = "adam.davis", role: str = "proposal_writer") -> dict:
    for row in _tenant_rows(REQUIREMENTS, tenant_id):
        if row["id"] == requirement_id or row["requirement_id"] == requirement_id:
            before = {"owner": row["owner"], "status": row["status"]}
            row["owner"] = owner
            row["status"] = status
            audit_event("assign_requirement", user, role, "ok", {"before": before, "after": {"owner": owner, "status": status}}, tenant_id=tenant_id, resource_id=row["id"], reason="requirement_owner_or_status_changed")
            return row
    return {"error": "requirement_not_found"}


def build_requirement_trace(requirement_id: str, tenant_id: str = DEFAULT_TENANT, user: str = "adam.davis", role: str = "proposal_writer") -> dict:
    requirement = next((row for row in _tenant_rows(REQUIREMENTS, tenant_id) if row["id"] == requirement_id or row["requirement_id"] == requirement_id), None)
    if not requirement:
        return {"error": "requirement_not_found"}

    retrieved = hybrid_search(requirement["requirement_text"], tenant_id)
    ranked = rerank(requirement["requirement_text"], retrieved["rrf_fused"])[:4]
    evidence = [
        {
            "document": item["document_title"],
            "section": item["section"],
            "chunk_id": item["chunk_id"],
            "snippet": item["text"][:220],
            "score": item.get("rerank_score", item.get("vector_score", 0)),
        }
        for item in ranked
    ]
    response = MockClaudeSonnetBedrock().invoke(
        "Draft proposal response using this requirement and evidence:\n"
        f"Requirement: {requirement['requirement_text']}\n"
        f"Evidence count: {len(evidence)}"
    )["answer"]
    confidence = round(min(0.98, 0.62 + (0.08 * len(evidence))), 2)
    trace = {
        "id": _short_id("TRACE"),
        "tenant_id": tenant_id,
        "requirement_id": requirement["id"],
        "source_rfp_text": requirement["requirement_text"],
        "retrieved_evidence": evidence,
        "proposed_response_section": response,
        "confidence_score": confidence,
        "score_reason": "Confidence increases when retrieved evidence supports the requirement and citations are available.",
    }
    REQUIREMENT_TRACES.insert(0, trace)
    requirement["evidence_summary"] = f"{len(evidence)} evidence snippets linked"
    requirement["confidence_score"] = confidence
    audit_event("build_requirement_trace", user, role, "ok", {"requirement_id": requirement["id"], "evidence_count": len(evidence), "confidence": confidence}, tenant_id=tenant_id, resource_id=requirement["id"], reason="requirement_trace_created")
    return trace


def create_proposal(name: str = "DHS Cyber Modernization Proposal", tenant_id: str = DEFAULT_TENANT, user: str = "adam.davis", role: str = "proposal_writer") -> dict:
    existing = _tenant_rows(PROPOSALS, tenant_id)
    if existing:
        return {"proposal": existing[0], "sections": _tenant_rows(PROPOSAL_SECTIONS, tenant_id)}
    proposal = {"id": _short_id("PROP"), "tenant_id": tenant_id, "name": name, "status": "In Progress"}
    PROPOSALS.append(proposal)
    for volume, title, owner in DEFAULT_PROPOSAL_SECTIONS:
        PROPOSAL_SECTIONS.append(
            {
                "id": _short_id("SEC"),
                "tenant_id": tenant_id,
                "proposal_id": proposal["id"],
                "volume": volume,
                "section_title": title,
                "assigned_to": owner,
                "status": "Drafting",
                "percent_complete": 20 if owner != "Finance" else 10,
                "content": "",
                "linked_requirements": [],
                "evidence_refs": [],
            }
        )
    audit_event("create_proposal_workspace", user, role, "ok", {"proposal_id": proposal["id"], "sections": 6}, tenant_id=tenant_id, resource_id=proposal["id"], reason="default_proposal_workspace_created")
    return {"proposal": proposal, "sections": _tenant_rows(PROPOSAL_SECTIONS, tenant_id)}


def update_section(section_id: str, payload: dict, tenant_id: str = DEFAULT_TENANT, user: str = "adam.davis", role: str = "proposal_writer") -> dict:
    for section in _tenant_rows(PROPOSAL_SECTIONS, tenant_id):
        if section["id"] == section_id:
            before = {key: section.get(key) for key in ["assigned_to", "status", "percent_complete", "content"]}
            for key in ["assigned_to", "status", "percent_complete", "content"]:
                if key in payload:
                    section[key] = payload[key]
            audit_event("update_proposal_section", user, role, "ok", {"before": before, "after": payload}, tenant_id=tenant_id, resource_id=section_id, reason="proposal_section_updated")
            return section
    return {"error": "section_not_found"}


def search_content_library(query: str, tenant_id: str = DEFAULT_TENANT) -> dict:
    seed_demo_content(tenant_id)
    q = Counter(query.lower().split())
    rows = []
    for row in _tenant_rows(CONTENT_LIBRARY, tenant_id):
        haystack = " ".join([row["title"], row["body"], " ".join(row["tags"])]).lower()
        score = sum(haystack.count(term) for term in q)
        if score or not query:
            rows.append({**row, "match_score": score})
    return {"query": query, "results": sorted(rows, key=lambda row: row["match_score"], reverse=True)}


def insert_content(section_id: str, content_id: str, tenant_id: str = DEFAULT_TENANT, user: str = "adam.davis", role: str = "proposal_writer") -> dict:
    section = next((row for row in _tenant_rows(PROPOSAL_SECTIONS, tenant_id) if row["id"] == section_id), None)
    content = next((row for row in _tenant_rows(CONTENT_LIBRARY, tenant_id) if row["id"] == content_id), None)
    if not section or not content:
        return {"error": "section_or_content_not_found"}
    section["content"] = (section.get("content") or "") + "\n\n" + content["body"]
    section["evidence_refs"].extend(content["evidence_refs"])
    section["percent_complete"] = max(section["percent_complete"], 55)
    audit_event("reuse_approved_content", user, role, "ok", {"section_id": section_id, "content_id": content_id, "evidence_refs": content["evidence_refs"]}, tenant_id=tenant_id, resource_id=section_id, reason="approved_content_inserted_with_evidence")
    return {"section": section, "content": content}


def create_review_issue(payload: dict, tenant_id: str = DEFAULT_TENANT, user: str = "reviewer", role: str = "reviewer") -> dict:
    issue = {
        "id": _short_id("REV"),
        "tenant_id": tenant_id,
        "proposal_section_id": payload.get("proposal_section_id"),
        "requirement_id": payload.get("requirement_id"),
        "issue": payload.get("issue", "Reviewer issue"),
        "severity": payload.get("severity", "Medium"),
        "owner": payload.get("owner", "adam.davis"),
        "comment": payload.get("comment", ""),
        "status": payload.get("status", "Open"),
        "evidence": payload.get("evidence", []),
        "response_history": [],
    }
    REVIEW_ISSUES.insert(0, issue)
    audit_event("create_review_issue", user, role, "ok", {"issue_id": issue["id"], "severity": issue["severity"]}, tenant_id=tenant_id, resource_id=issue["id"], reason="red_pink_gold_issue_created")
    return issue


def update_review_issue(issue_id: str, status: str, comment: str, tenant_id: str = DEFAULT_TENANT, user: str = "adam.davis", role: str = "proposal_writer") -> dict:
    for issue in _tenant_rows(REVIEW_ISSUES, tenant_id):
        if issue["id"] == issue_id:
            issue["response_history"].append({"user": user, "role": role, "from": issue["status"], "to": status, "comment": comment})
            issue["status"] = status
            audit_event("update_review_issue", user, role, "ok", {"issue_id": issue_id, "status": status, "comment": comment}, tenant_id=tenant_id, resource_id=issue_id, reason="review_issue_status_changed")
            return issue
    return {"error": "issue_not_found"}


def proposal_health(tenant_id: str = DEFAULT_TENANT) -> dict:
    requirements = _tenant_rows(REQUIREMENTS, tenant_id)
    sections = _tenant_rows(PROPOSAL_SECTIONS, tenant_id)
    traces = _tenant_rows(REQUIREMENT_TRACES, tenant_id)
    issues = _tenant_rows(REVIEW_ISSUES, tenant_id)
    req_complete = (sum(1 for row in requirements if row["status"] == "Complete") / max(len(requirements), 1)) * 100
    evidence_coverage = (len({row["requirement_id"] for row in traces}) / max(len(requirements), 1)) * 100
    review_resolution = (sum(1 for row in issues if row["status"] in {"Resolved", "Accepted"}) / max(len(issues), 1)) * 100
    section_completion = sum(row["percent_complete"] for row in sections) / max(len(sections), 1)
    high_risk_open = sum(1 for row in requirements if row["risk_level"] == "High" and row["status"] != "Complete")
    risk_score = max(0, 100 - (high_risk_open * 12))
    readiness = round((req_complete * 0.30) + (evidence_coverage * 0.25) + (review_resolution * 0.20) + (section_completion * 0.15) + (risk_score * 0.10), 2)
    if readiness >= 85:
        impact = "Strong Bid"
    elif readiness >= 70:
        impact = "Bid With Risk"
    elif readiness >= 50:
        impact = "Executive Review Required"
    else:
        impact = "No-Bid Recommended"
    return {
        "readiness_score": readiness,
        "requirements_complete_pct": round(req_complete, 2),
        "evidence_coverage_pct": round(evidence_coverage, 2),
        "review_resolution_pct": round(review_resolution, 2),
        "section_completion_pct": round(section_completion, 2),
        "missing_items": sum(1 for row in requirements if row["status"] != "Complete"),
        "high_risk_requirements": high_risk_open,
        "schedule_risk": "Medium" if high_risk_open else "Low",
        "review_queue": len([row for row in issues if row["status"] not in {"Resolved", "Accepted"}]),
        "bid_no_bid_impact": impact,
    }
