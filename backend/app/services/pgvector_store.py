from __future__ import annotations

import json
import os
import time
from typing import Iterable

import psycopg
from psycopg.rows import dict_row


DEFAULT_DATABASE_URL = "postgresql://bidintel:bidintel_dev_password@localhost:56550/bidintel"
DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)


def enabled() -> bool:
    return os.getenv("USE_REAL_PGVECTOR", "true").lower() in {"1", "true", "yes", "on"}


def vector_literal(values: Iterable[float]) -> str:
    return "[" + ",".join(str(float(value)) for value in values) + "]"


def connect():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def ensure_schema() -> dict:
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS documents (
                    document_id TEXT PRIMARY KEY,
                    tenant_id TEXT NOT NULL,
                    title TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    classification TEXT NOT NULL,
                    access_groups JSONB NOT NULL DEFAULT '[]'::jsonb,
                    status TEXT NOT NULL,
                    chunk_count INTEGER NOT NULL DEFAULT 0,
                    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS chunks (
                    chunk_id INTEGER PRIMARY KEY,
                    document_id TEXT NOT NULL REFERENCES documents(document_id) ON DELETE CASCADE,
                    tenant_id TEXT NOT NULL,
                    document_title TEXT NOT NULL,
                    classification TEXT NOT NULL,
                    status TEXT NOT NULL,
                    section TEXT NOT NULL,
                    title TEXT NOT NULL,
                    page INTEGER NOT NULL,
                    text TEXT NOT NULL,
                    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
                    embedding VECTOR(1536) NOT NULL,
                    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                );
                """
            )
            cur.execute(
                """
                CREATE INDEX IF NOT EXISTS chunks_embedding_hnsw_idx
                ON chunks USING hnsw (embedding vector_cosine_ops);
                """
            )
            cur.execute("CREATE INDEX IF NOT EXISTS chunks_tenant_idx ON chunks (tenant_id, classification, status);")
    return {"schema_ready": True, "extension": "vector", "embedding_column": "VECTOR(1536)", "index": "HNSW"}


def save_document_and_chunks(document: dict, chunks: list[dict]) -> dict:
    ensure_schema()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO documents (
                    document_id, tenant_id, title, filename, classification,
                    access_groups, status, chunk_count, metadata
                )
                VALUES (%s, %s, %s, %s, %s, %s::jsonb, %s, %s, %s::jsonb)
                ON CONFLICT (document_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    filename = EXCLUDED.filename,
                    classification = EXCLUDED.classification,
                    access_groups = EXCLUDED.access_groups,
                    status = EXCLUDED.status,
                    chunk_count = EXCLUDED.chunk_count,
                    metadata = EXCLUDED.metadata;
                """,
                (
                    document["document_id"],
                    document["tenant_id"],
                    document["title"],
                    document["filename"],
                    document["classification"],
                    json.dumps(document.get("access_groups", [])),
                    document["status"],
                    document["chunk_count"],
                    json.dumps({
                        "content_type": document.get("content_type"),
                        "attachment_kind": document.get("attachment_kind"),
                        "extraction_mode": document.get("extraction_mode"),
                        "file_size": document.get("file_size", 0),
                    }),
                ),
            )
            for chunk in chunks:
                cur.execute(
                    """
                    INSERT INTO chunks (
                        chunk_id, document_id, tenant_id, document_title,
                        classification, status, section, title, page, text,
                        metadata, embedding
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s::vector)
                    ON CONFLICT (chunk_id) DO UPDATE SET
                        text = EXCLUDED.text,
                        metadata = EXCLUDED.metadata,
                        embedding = EXCLUDED.embedding;
                    """,
                    (
                        chunk["chunk_id"],
                        chunk["document_id"],
                        chunk["tenant_id"],
                        chunk["document_title"],
                        chunk["classification"],
                        chunk["status"],
                        chunk["section"],
                        chunk["title"],
                        chunk["page"],
                        chunk["text"],
                        json.dumps(chunk["metadata"]),
                        vector_literal(chunk["embedding"]),
                    ),
                )
    return {"saved": True, "documents": 1, "chunks": len(chunks), "store": "real PostgreSQL + pgvector"}


def list_documents(limit: int = 100) -> list[dict]:
    ensure_schema()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    document_id, title, filename, tenant_id, classification,
                    status, chunk_count, metadata, created_at
                FROM documents
                ORDER BY created_at DESC
                LIMIT %s;
                """,
                (limit,),
            )
            rows = cur.fetchall()
    return [dict(row) for row in rows]


def list_vector_rows(limit: int = 50) -> list[dict]:
    ensure_schema()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    chunk_id, document_id, document_title, tenant_id, classification,
                    section, page, LEFT(text, 180) AS text_preview,
                    vector_dims(embedding) AS embedding_dimensions,
                    substring(embedding::text from 1 for 80) AS embedding_preview,
                    metadata
                FROM chunks
                ORDER BY chunk_id DESC
                LIMIT %s;
                """,
                (limit,),
            )
            rows = cur.fetchall()
    return [dict(row) for row in rows]


def count_rows() -> dict:
    ensure_schema()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) AS documents FROM documents;")
            docs = cur.fetchone()["documents"]
            cur.execute("SELECT COUNT(*) AS chunks FROM chunks;")
            chunks = cur.fetchone()["chunks"]
            cur.execute("SELECT indexname FROM pg_indexes WHERE tablename = 'chunks' ORDER BY indexname;")
            indexes = [row["indexname"] for row in cur.fetchall()]
    return {"documents": docs, "chunks": chunks, "indexes": indexes}


def max_ids() -> dict:
    ensure_schema()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(MAX((regexp_match(document_id, 'DOC-([0-9]+)'))[1]::integer), 0) AS max_doc
                FROM documents
                WHERE document_id ~ '^DOC-[0-9]+$';
                """
            )
            max_doc = cur.fetchone()["max_doc"]
            cur.execute("SELECT COALESCE(MAX(chunk_id), 0) AS max_chunk FROM chunks;")
            max_chunk = cur.fetchone()["max_chunk"]
    return {"max_doc": int(max_doc), "max_chunk": int(max_chunk)}


def fetch_chunks_for_retrieval(tenant_id: str, limit: int = 500) -> list[dict]:
    ensure_schema()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    chunk_id, document_id, document_title, tenant_id, classification,
                    status, section, title, page, text, metadata,
                    embedding::text AS embedding_text
                FROM chunks
                WHERE tenant_id = %s AND status = 'approved'
                ORDER BY chunk_id DESC
                LIMIT %s;
                """,
                (tenant_id, limit),
            )
            rows = cur.fetchall()

    chunks = []
    for row in rows:
        chunk = dict(row)
        embedding_text = chunk.pop("embedding_text").strip("[]")
        chunk["embedding"] = [float(value) for value in embedding_text.split(",") if value]
        chunks.append(chunk)
    return chunks


def nearest_vectors(question_embedding: list[float], tenant_id: str, limit: int = 5) -> list[dict]:
    ensure_schema()
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    chunk_id, document_id, document_title, tenant_id, classification,
                    status, section, title, page, text, metadata,
                    1 - (embedding <=> %s::vector) AS vector_score
                FROM chunks
                WHERE tenant_id = %s AND status = 'approved'
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (vector_literal(question_embedding), tenant_id, vector_literal(question_embedding), limit),
            )
            rows = cur.fetchall()
    return [{**dict(row), "source": "pgvector", "vector_score": round(float(row["vector_score"]), 4)} for row in rows]


def explain_vector_query(question_embedding: list[float], tenant_id: str, use_hnsw: bool = True, limit: int = 5) -> dict:
    ensure_schema()
    query = vector_literal(question_embedding)
    with connect() as conn:
        with conn.cursor() as cur:
            if use_hnsw:
                cur.execute("SET enable_seqscan = off;")
            else:
                cur.execute("SET enable_indexscan = off;")
                cur.execute("SET enable_bitmapscan = off;")
            started = time.perf_counter()
            cur.execute(
                """
                EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
                SELECT
                    chunk_id,
                    document_title,
                    section,
                    1 - (embedding <=> %s::vector) AS similarity_score
                FROM chunks
                WHERE tenant_id = %s AND status = 'approved'
                ORDER BY embedding <=> %s::vector
                LIMIT %s;
                """,
                (query, tenant_id, query, limit),
            )
            plan = [row["QUERY PLAN"] for row in cur.fetchall()]
            latency_ms = round((time.perf_counter() - started) * 1000, 3)
            cur.execute("RESET enable_seqscan;")
            cur.execute("RESET enable_indexscan;")
            cur.execute("RESET enable_bitmapscan;")
    return {
        "mode": "hnsw_index_preferred" if use_hnsw else "index_disabled_exact_scan",
        "latency_ms": latency_ms,
        "plan": plan[:8],
    }
