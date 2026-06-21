from __future__ import annotations

def score_answer(answer_packet: dict) -> dict:
    answer = answer_packet.get("answer", "")
    evidence = answer_packet.get("retrieved_context", [])
    citations = answer_packet.get("citations", [])
    faithfulness = 0.94 if citations else 0.35
    answer_relevance = 0.89 if len(answer) > 80 else 0.55
    context_precision = min(0.95, 0.55 + len(evidence) * 0.09)
    return {
        "tool": "RAGAS local simulation",
        "faithfulness": round(faithfulness, 2),
        "answer_relevance": round(answer_relevance, 2),
        "context_precision": round(context_precision, 2),
        "production_equivalent": "ragas.evaluate over golden examples and retrieved contexts",
    }
