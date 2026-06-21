from __future__ import annotations
from collections import Counter

from backend.app.security.classification_guard import can_access_classification
from backend.app.security.tenant_guard import assert_tenant_access
from backend.app.services.embeddings import cosine, embed_text
from backend.app.services.store import CHUNKS
from backend.app.services import pgvector_store

def _terms(text: str) -> list[str]:
    return [token.lower() for token in text.replace("/", " ").replace("-", " ").split()]

def retrieval_filter(chunk: dict, tenant_id: str, clearance: str = "cui") -> bool:
    return (
        assert_tenant_access(tenant_id, chunk["tenant_id"])["allowed"]
        and can_access_classification(clearance, chunk.get("classification", "cui"))["allowed"]
        and chunk.get("status") == "approved"
    )

def bm25_search(question: str, tenant_id: str, limit: int = 5) -> list[dict]:
    q = Counter(_terms(question))
    rows = []
    chunks = CHUNKS
    if pgvector_store.enabled():
        try:
            chunks = pgvector_store.fetch_chunks_for_retrieval(tenant_id)
        except Exception:
            chunks = CHUNKS
    for chunk in chunks:
        if not retrieval_filter(chunk, tenant_id):
            continue
        words = Counter(_terms(chunk["text"] + " " + chunk["section"] + " " + chunk["title"]))
        score = sum(words.get(term, 0) * weight for term, weight in q.items())
        if score:
            rows.append({**chunk, "bm25_score": round(float(score), 3), "source": "bm25"})
    return sorted(rows, key=lambda row: row["bm25_score"], reverse=True)[:limit]

def vector_search(question: str, tenant_id: str, limit: int = 5) -> list[dict]:
    qv = embed_text(question)
    if pgvector_store.enabled():
        try:
            return pgvector_store.nearest_vectors(qv, tenant_id, limit)
        except Exception:
            pass
    rows = []
    for chunk in CHUNKS:
        if retrieval_filter(chunk, tenant_id):
            rows.append({**chunk, "vector_score": round(cosine(qv, chunk["embedding"]), 4), "source": "vector"})
    return sorted(rows, key=lambda row: row["vector_score"], reverse=True)[:limit]

def reciprocal_rank_fusion(rank_lists: list[list[dict]], k: int = 60) -> list[dict]:
    fused = {}
    for results in rank_lists:
        for rank, item in enumerate(results, start=1):
            cid = item["chunk_id"]
            fused.setdefault(cid, {**item, "rrf_score": 0.0, "sources": []})
            fused[cid]["rrf_score"] += 1 / (k + rank)
            fused[cid]["sources"].append(item["source"])
    return sorted(fused.values(), key=lambda row: row["rrf_score"], reverse=True)

def hybrid_search(question: str, tenant_id: str, limit: int = 5) -> dict:
    bm25 = bm25_search(question, tenant_id, limit)
    vector = vector_search(question, tenant_id, limit)
    fused = reciprocal_rank_fusion([bm25, vector])[:limit]
    return {"bm25": bm25, "vector": vector, "rrf_fused": fused}
