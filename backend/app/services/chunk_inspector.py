from __future__ import annotations

from backend.app.services.chunking import detect_sections, split_children


def inspect_chunking(text: str) -> dict:
    parents = detect_sections(text)
    children = [child for parent in parents for child in split_children(parent)]
    bad_parent = {"section": "Document", "title": "Bad 1000-token style chunk", "text": text[:4000], "page": 1}
    bad_children = split_children(bad_parent, chunk_size=1000, overlap=0)
    good_children = [child for parent in parents for child in split_children(parent, chunk_size=300, overlap=80)]
    return {
        "tool_definition": "Chunking splits a long document into smaller pieces so retrieval can find the right evidence.",
        "original_preview": text[:600],
        "parent_chunks": [
            {"section": parent["section"], "title": parent["title"], "page": parent["page"], "text_preview": parent["text"][:220]}
            for parent in parents
        ],
        "child_chunks": [
            {"section": child["section"], "child_index": child["child_index"], "engine": child["chunking_engine"], "text_preview": child["text"][:220]}
            for child in children
        ],
        "bad_chunk_example": {
            "chunk_size": 1000,
            "overlap": 0,
            "risk": "Large chunks mix unrelated requirements, so retrieval may return a broad chunk that does not answer the question cleanly.",
            "chunks": [{"child_index": child["child_index"], "text_preview": child["text"][:220]} for child in bad_children[:3]],
        },
        "good_chunk_example": {
            "chunk_size": 300,
            "overlap": 80,
            "why_better": "Smaller overlapping chunks keep section context while making retrieval more precise.",
            "chunks": [{"child_index": child["child_index"], "text_preview": child["text"][:220]} for child in good_children[:5]],
        },
        "good_output": "A learner should see original text -> parent sections -> child chunks -> metadata carried forward.",
    }
