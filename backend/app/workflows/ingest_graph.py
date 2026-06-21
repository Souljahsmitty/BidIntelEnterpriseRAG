from __future__ import annotations

import uuid
from backend.app.security.document_security_scans import scan_upload_document
from backend.app.services.audit_logger import audit_event
from backend.app.services.chunking import detect_sections, split_children
from backend.app.services.embeddings import embed_text
from backend.app.services import store
from backend.app.services import pgvector_store

def run_ingest_workflow(filename: str, text: str, tenant_id: str, user: str, metadata: dict) -> dict:
    workflow_id = str(uuid.uuid4())
    steps = [{"step": "receive_attachment", "filename": filename, "content_type": metadata.get("content_type", "text/plain")}]
    if metadata.get("attachment_kind") == "executable":
        trace = {
            "workflow_id": workflow_id,
            "filename": filename,
            "status": "rejected",
            "tenant_id": tenant_id,
            "user": user,
            "steps": steps + [{"step": "file_type_guard", "status": "rejected"}],
            "scan": {
                "filename": filename,
                "accepted_for_chunking": False,
                "action": "reject",
                "reason": "unsupported_executable_attachment",
                "production_equivalent": "Antivirus and malware sandbox reject executable uploads before extraction or chunking.",
            },
        }
        store.INGESTION_TRACES.insert(0, trace)
        audit_event("file_type_guard", user, metadata.get("role", "proposal_writer"), "blocked", trace["scan"])
        return {"workflow_status": "rejected", "workflow_id": workflow_id, "scan": trace["scan"], "steps": trace["steps"]}
    scan = scan_upload_document(filename, text)
    steps.append({"step": "document_security_scans.py", "status": scan["action"]})
    audit_event("upload_security_scan", user, metadata.get("role", "proposal_writer"), "blocked" if not scan["accepted_for_chunking"] else "ok", scan)
    if not scan["accepted_for_chunking"]:
        trace = {
            "workflow_id": workflow_id,
            "filename": filename,
            "status": "quarantined",
            "tenant_id": tenant_id,
            "user": user,
            "steps": steps,
            "scan": scan,
        }
        store.INGESTION_TRACES.insert(0, trace)
        return {"workflow_status": "quarantined", "workflow_id": workflow_id, "scan": scan, "steps": steps}

    if pgvector_store.enabled():
        try:
            ids = pgvector_store.max_ids()
            store.NEXT_DOC = max(store.NEXT_DOC, ids["max_doc"])
            store.NEXT_CHUNK = max(store.NEXT_CHUNK, ids["max_chunk"])
        except Exception:
            pass
    store.NEXT_DOC += 1
    document_id = f"DOC-{store.NEXT_DOC:06d}"
    parents = detect_sections(scan["safe_text"])
    children = [child for parent in parents for child in split_children(parent)]
    steps.append({"step": "layered_document_chunking", "parent_chunks": len(parents), "child_chunks": len(children)})
    doc = {
        "document_id": document_id,
        "title": metadata.get("title") or filename,
        "filename": filename,
        "content_type": metadata.get("content_type", "text/plain"),
        "file_size": metadata.get("file_size", 0),
        "attachment_kind": metadata.get("attachment_kind", "text"),
        "extraction_mode": metadata.get("extraction_mode", "direct_text_decode"),
        "tenant_id": tenant_id,
        "classification": metadata.get("classification", "cui"),
        "access_groups": metadata.get("access_groups", ["Proposal_Team", "Capture_Team"]),
        "status": "embedded",
        "chunk_count": len(children),
    }
    store.DOCUMENTS.insert(0, doc)
    new_chunks = []
    for child in children:
        store.NEXT_CHUNK += 1
        chunk = {
            "chunk_id": store.NEXT_CHUNK,
            "document_id": document_id,
            "document_title": doc["title"],
            "tenant_id": tenant_id,
            "classification": doc["classification"],
            "status": "approved",
            "section": child["section"],
            "title": child["title"],
            "page": child["page"],
            "text": child["text"],
            "metadata": {
                "access_groups": doc["access_groups"],
                "chunking_engine": child["chunking_engine"],
                "attachment_kind": doc["attachment_kind"],
                "extraction_mode": doc["extraction_mode"],
            },
            "embedding": embed_text(child["text"]),
        }
        store.CHUNKS.append(chunk)
        new_chunks.append(chunk)
    db_save = {"saved": False, "store": "in-memory fallback"}
    if pgvector_store.enabled():
        try:
            db_save = pgvector_store.save_document_and_chunks(doc, new_chunks)
        except Exception as exc:
            db_save = {"saved": False, "store": "real PostgreSQL + pgvector", "error": str(exc)}
    steps.append({
        "step": "embed_and_store",
        "embedding_dimensions": 1536,
        "store": "real PostgreSQL + pgvector" if db_save.get("saved") else "in-memory fallback",
        "db_save": db_save,
    })
    audit_event("embed_document", user, metadata.get("role", "proposal_writer"), "ok", {"document_id": document_id, "chunks": len(children)})
    trace = {
        "workflow_id": workflow_id,
        "filename": filename,
        "status": "stored",
        "tenant_id": tenant_id,
        "user": user,
        "document_id": document_id,
        "steps": steps,
        "scan": {key: value for key, value in scan.items() if key != "safe_text"},
        "db_save": db_save,
        "vector_rows": [
            {
                "chunk_id": row["chunk_id"],
                "section": row["section"],
                "embedding_dimensions": len(row["embedding"]),
                "metadata": row["metadata"],
            }
            for row in store.CHUNKS
            if row["document_id"] == document_id
        ],
    }
    store.INGESTION_TRACES.insert(0, trace)
    return {"workflow_status": "stored", "workflow_id": workflow_id, "document": doc, "scan": scan, "steps": steps}
