from __future__ import annotations

LEVELS = {"public": 0, "internal": 1, "cui": 2, "secret": 3}

def can_access_classification(user_clearance: str, document_level: str) -> dict:
    allowed = LEVELS.get(user_clearance, 0) >= LEVELS.get(document_level, 99)
    return {"allowed": allowed, "user_clearance": user_clearance, "document_level": document_level}
