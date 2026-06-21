from __future__ import annotations

def assert_tenant_access(user_tenant_id: str, document_tenant_id: str) -> dict:
    allowed = user_tenant_id == document_tenant_id
    return {"allowed": allowed, "reason": "tenant_match" if allowed else "tenant_mismatch"}
