from __future__ import annotations

import time

from backend.app.rag.retriever import bm25_search, hybrid_search, vector_search
from backend.app.services import pgvector_store
from backend.app.services.embeddings import embed_text


def retrieval_debug_panel(question: str, tenant_id: str = "tenant_acme") -> dict:
    """Show why each retrieval result appeared before the LLM sees it."""
    bm25 = bm25_search(question, tenant_id)
    vector = vector_search(question, tenant_id)
    fused = hybrid_search(question, tenant_id)["rrf_fused"]
    rows = []
    for rank, item in enumerate(fused, start=1):
        rows.append(
            {
                "rank": rank,
                "chunk_id": item["chunk_id"],
                "document": item["document_title"],
                "section": item["section"],
                "bm25_score": item.get("bm25_score"),
                "vector_score": item.get("vector_score"),
                "rrf_score": round(item.get("rrf_score", 0.0), 6),
                "why_retrieved": item.get("sources", [item.get("source", "unknown")]),
                "text_preview": item["text"][:220],
            }
        )
    return {
        "question": question,
        "explain_like_beginner": "This panel answers: why did this chunk get retrieved?",
        "bm25_top": [{"chunk_id": r["chunk_id"], "score": r.get("bm25_score"), "section": r["section"]} for r in bm25],
        "vector_top": [{"chunk_id": r["chunk_id"], "score": r.get("vector_score"), "section": r["section"]} for r in vector],
        "rrf_fused": rows,
        "good_output": "The learner should see exact keyword results, vector results, then RRF fused results with chunk IDs and scores.",
    }


def hnsw_latency_probe(question: str, tenant_id: str = "tenant_acme") -> dict:
    """Run an explainable local probe for exact vs indexed vector retrieval."""
    query_vector = embed_text(question)
    result = {
        "question": question,
        "tool_definition": "HNSW = Hierarchical Navigable Small World, a pgvector index that makes nearest-neighbor vector search fast at high volume.",
        "without_hnsw": {"mode": "exact_or_seq_scan", "latency_ms": None, "plan": []},
        "with_hnsw": {"mode": "indexed_search", "latency_ms": None, "plan": []},
        "production_value": "At 100 chunks you may not notice. At millions of chunks, HNSW keeps retrieval usable.",
    }
    if not pgvector_store.enabled():
        result["simulation_boundary"] = "Real EXPLAIN ANALYZE requires PostgreSQL + pgvector. This local run is using the in-memory fallback."
        result["without_hnsw"]["latency_ms"] = 1800
        result["with_hnsw"]["latency_ms"] = 120
        return result
    try:
        exact = pgvector_store.explain_vector_query(query_vector, tenant_id, use_hnsw=False)
        indexed = pgvector_store.explain_vector_query(query_vector, tenant_id, use_hnsw=True)
        result["without_hnsw"].update(exact)
        result["with_hnsw"].update(indexed)
    except Exception as exc:
        started = time.perf_counter()
        vector_search(question, tenant_id)
        elapsed = round((time.perf_counter() - started) * 1000, 3)
        result["warning"] = f"EXPLAIN probe failed, fallback latency measured only: {exc}"
        result["without_hnsw"]["latency_ms"] = elapsed
        result["with_hnsw"]["latency_ms"] = elapsed
    return result
