from __future__ import annotations
import time
import uuid
from backend.app.services.store import AUDIT_LOGS

def audit_event(
    action: str,
    user: str,
    role: str,
    status: str,
    details: dict,
    *,
    tenant_id: str = "tenant_acme",
    resource_id: str | None = None,
    reason: str | None = None,
) -> dict:
    row = {
        "event_id": f"audit-{uuid.uuid4().hex[:10]}",
        "time": time.strftime("%H:%M:%S"),
        "timestamp_epoch": round(time.time(), 3),
        "tenant_id": tenant_id,
        "user": user,
        "role": role,
        "action": action,
        "resource_id": resource_id or details.get("document_id") or details.get("trace_id") or "-",
        "status": status,
        "reason": reason or details.get("reason") or status,
        "details": details,
        "retention": "7 years for federal audit evidence in production",
    }
    AUDIT_LOGS.insert(0, row)
    return row
