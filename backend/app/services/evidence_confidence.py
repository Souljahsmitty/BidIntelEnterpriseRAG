from __future__ import annotations


def evidence_confidence(packet: dict) -> dict:
    citations = packet.get("citations", [])
    contexts = packet.get("retrieved_context", [])
    if not citations:
        return {
            "score": 0.0,
            "label": "insufficient_evidence",
            "calculation": "0 citations means the system must refuse instead of guessing.",
        }
    citation_factor = min(1.0, len(citations) / 4)
    context_factor = min(1.0, len(contexts) / 4)
    score = round((citation_factor * 0.55 + context_factor * 0.45) * 100, 1)
    return {
        "score": score,
        "label": "high" if score >= 85 else "medium" if score >= 60 else "low",
        "calculation": "55% citation coverage + 45% retrieved context coverage",
        "citation_count": len(citations),
        "context_count": len(contexts),
    }


def insufficient_evidence_response(question: str) -> dict:
    return {
        "question": question,
        "answer": "Insufficient evidence. BidIntel could not find cited internal evidence for this question, so it will not guess.",
        "citations": [],
        "evidence_confidence": evidence_confidence({"citations": [], "retrieved_context": []}),
        "why_companies_use_it": "Federal proposal teams need refusals when evidence is missing because hallucinated contract claims create compliance and credibility risk.",
    }
