from __future__ import annotations

ROLE_PERMISSIONS = {
    "proposal_writer": {"upload", "ask", "view_documents", "view_bid"},
    "proposal_manager": {"upload", "ask", "view_documents", "view_bid", "review"},
    "admin": {"upload", "ask", "view_documents", "view_bid", "review", "view_audit"},
}

def can(role: str, action: str) -> dict:
    allowed = action in ROLE_PERMISSIONS.get(role, set())
    return {"allowed": allowed, "role": role, "action": action, "reason": "role_allowed" if allowed else "role_denied"}
