from __future__ import annotations

def _evidence_text(evidence: list[dict]) -> str:
    return " ".join(
        " ".join(str(row.get(key, "")) for key in ["text", "section", "document_title", "title"])
        for row in evidence
    ).lower()


def score_opportunity() -> dict:
    factors = {
        "strategic_fit": 88,
        "past_performance_match": 84,
        "technical_capability": 90,
        "contract_vehicle_fit": 95,
        "agency_relationship": 70,
        "security_clearance_fit": 82,
        "timeline_feasibility": 58,
        "staffing_availability": 61,
        "compliance_risk_inverse": 66,
    }
    score = round(sum(factors.values()) / len(factors))
    return {
        "score": score,
        "recommendation": "BID" if score >= 75 else "REVIEW",
        "win_probability": 62,
        "confidence": "High",
        "factors": factors,
        "risks": ["Aggressive 30-day transition", "Incumbent strongly entrenched", "Two cleared staff to backfill"],
        "next_steps": ["Schedule bid/no-bid review", "Generate compliance matrix", "Draft technical approach"],
    }


def score_from_retrieved_evidence(question: str, evidence: list[dict]) -> dict:
    text = _evidence_text(evidence)
    factor_rules = {
        "strategic_fit": {
            "score": 88 if "cyber" in text or "soc" in text else 62,
            "why": "SOC/cybersecurity language matches the company's target capture lane.",
        },
        "technical_capability": {
            "score": 90 if "24/7" in text or "monitoring" in text else 65,
            "why": "Retrieved evidence mentions 24/7 monitoring and technical operations.",
        },
        "past_performance_match": {
            "score": 84 if "past performance" in text or "soc" in text else 58,
            "why": "RAG evidence can support prior SOC modernization language.",
        },
        "contract_vehicle_fit": {
            "score": 92 if "gsa" in text or "mas" in text else 64,
            "why": "Evidence references GSA MAS style acquisition context when present.",
        },
        "security_clearance_fit": {
            "score": 82 if "cleared" in text or "cui" in text or "security" in text else 60,
            "why": "Classification/security language is present in retrieved evidence.",
        },
        "timeline_feasibility": {
            "score": 58 if "30-day" in text or "transition" in text else 76,
            "why": "Aggressive transition language lowers timeline feasibility.",
        },
        "compliance_risk_inverse": {
            "score": 66 if "shall" in text or "requirement" in text else 78,
            "why": "Requirement-heavy language creates compliance work that must be tracked.",
        },
    }
    factors = {name: data["score"] for name, data in factor_rules.items()}
    score = round(sum(factors.values()) / len(factors))
    risks = []
    if factors["timeline_feasibility"] < 70:
        risks.append("Aggressive transition timeline found in retrieved evidence")
    if factors["compliance_risk_inverse"] < 75:
        risks.append("Requirement-heavy RFP language needs compliance matrix review")
    if len(evidence) < 2:
        risks.append("Low evidence count: score needs human review")
    return {
        "score": score,
        "recommendation": "BID" if score >= 75 else "REVIEW",
        "win_probability": max(35, min(78, score - 14)),
        "confidence": "Grounded" if evidence else "Insufficient evidence",
        "question": question,
        "factors": factors,
        "factor_explanations": {name: data["why"] for name, data in factor_rules.items()},
        "evidence_used": [
            {
                "chunk_id": row.get("chunk_id"),
                "document_title": row.get("document_title"),
                "section": row.get("section"),
                "score": row.get("rerank_score") or row.get("rrf_score") or row.get("vector_score"),
                "text_preview": row.get("text", "")[:220],
            }
            for row in evidence
        ],
        "risks": risks or ["No major risk detected in retrieved evidence"],
        "next_steps": ["Open evidence citations", "Generate compliance matrix", "Route bid/no-bid score for human review"],
        "proof": "This score was calculated from the retrieved RAG evidence shown in evidence_used.",
    }
