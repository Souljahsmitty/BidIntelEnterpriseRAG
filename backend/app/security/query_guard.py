from __future__ import annotations

from backend.app.security.prompt_injection_detector import detect_prompt_injection
from backend.app.security.rbac_guard import can

def guard_query(question: str, role: str) -> dict:
    permission = can(role, "ask")
    injection = detect_prompt_injection(question)
    allowed = permission["allowed"] and not injection["blocked"]
    return {
        "allowed": allowed,
        "permission": permission,
        "prompt_injection": injection,
        "reason": "allowed" if allowed else ("prompt_injection" if injection["blocked"] else "role_denied"),
    }
