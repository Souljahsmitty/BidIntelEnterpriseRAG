from __future__ import annotations

def rerank(question: str, chunks: list[dict]) -> list[dict]:
    q_terms = set(question.lower().split())
    ranked = []
    for chunk in chunks:
        text_terms = set(chunk["text"].lower().split())
        overlap = len(q_terms & text_terms)
        citation_bonus = 0.2 if chunk.get("page") else 0
        rrf = float(chunk.get("rrf_score", 0))
        ranked.append({**chunk, "rerank_score": round(overlap + citation_bonus + rrf, 4)})
    return sorted(ranked, key=lambda row: row["rerank_score"], reverse=True)
