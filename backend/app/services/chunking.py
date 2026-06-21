from __future__ import annotations
import re

try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception:
    RecursiveCharacterTextSplitter = None

SECTION_RE = re.compile(r"(?im)^(section\s+[a-z]|[clm]\s*\.\s*\d+|\d+\.\d+)\s+(.+)$")

def detect_sections(text: str) -> list[dict]:
    matches = list(SECTION_RE.finditer(text))
    if not matches:
        return [{"section": "Document", "title": "Full document", "text": text, "page": 1}]
    parents = []
    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
        parents.append({
            "section": match.group(1).strip(),
            "title": match.group(2).strip(),
            "text": text[start:end].strip(),
            "page": 1 + text[:start].count("\f"),
        })
    return parents

def split_children(parent: dict, chunk_size: int = 500, overlap: int = 100) -> list[dict]:
    text = parent["text"]
    if RecursiveCharacterTextSplitter:
        splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=overlap)
        pieces = splitter.split_text(text)
        engine = "LangChain RecursiveCharacterTextSplitter"
    else:
        pieces, step = [], max(1, chunk_size - overlap)
        for start in range(0, len(text), step):
            pieces.append(text[start:start + chunk_size])
            if start + chunk_size >= len(text):
                break
        engine = "local recursive fallback"
    return [
        {
            "section": parent["section"],
            "title": parent["title"],
            "page": parent["page"],
            "child_index": idx,
            "text": piece,
            "chunking_engine": engine,
        }
        for idx, piece in enumerate(pieces, start=1)
        if piece.strip()
    ]
