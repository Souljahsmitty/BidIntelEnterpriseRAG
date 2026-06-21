from __future__ import annotations

from backend.app.security.classification_guard import can_access_classification
from backend.app.security.rbac_guard import can
from backend.app.security.tenant_guard import assert_tenant_access


def enforce_access(
    *,
    user: str,
    role: str,
    action: str,
    user_tenant_id: str,
    document_tenant_id: str,
    user_clearance: str,
    document_classification: str,
) -> dict:
    role_check = can(role, action)
    tenant_check = assert_tenant_access(user_tenant_id, document_tenant_id)
    classification_check = can_access_classification(user_clearance, document_classification)
    allowed = role_check["allowed"] and tenant_check["allowed"] and classification_check["allowed"]
    failed = [
        name
        for name, check in {
            "rbac": role_check,
            "tenant": tenant_check,
            "classification": classification_check,
        }.items()
        if not check["allowed"]
    ]
    return {
        "allowed": allowed,
        "user": user,
        "role": role,
        "action": action,
        "tenant": tenant_check,
        "classification": classification_check,
        "rbac": role_check,
        "reason": "allowed" if allowed else "blocked_by_" + "_and_".join(failed),
        "production_equivalent": "AWS IAM Identity Center claims plus app RBAC, tenant filters, and classification handling policy.",
    }
