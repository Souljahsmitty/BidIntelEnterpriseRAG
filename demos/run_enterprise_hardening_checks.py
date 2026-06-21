from __future__ import annotations

import json
import os

import httpx


BASE = os.environ.get("BASE_URL", "http://127.0.0.1:18129")


def show(title: str, payload: dict) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2, default=str)[:6000])


def main() -> None:
    with httpx.Client(timeout=30) as client:
        show("security tests pass/fail", client.get(f"{BASE}/api/security/tests").json())
        show(
            "tenant mismatch blocked",
            client.get(
                f"{BASE}/api/security/enforcement-check",
                params={"tenant_id": "tenant_acme", "document_tenant_id": "tenant_other"},
            ).json(),
        )
        show(
            "classification blocked",
            client.get(
                f"{BASE}/api/security/enforcement-check",
                params={"clearance": "cui", "document_classification": "secret"},
            ).json(),
        )
        show("writer audit denied", client.get(f"{BASE}/api/audit", params={"role": "proposal_writer"}).json())
        show("admin audit allowed", client.get(f"{BASE}/api/audit", params={"role": "admin", "user": "admin"}).json())
        show("aws bedrock iam secrets runbook", client.get(f"{BASE}/api/aws/enterprise-runbook").json())
        show("deployment checklist", client.get(f"{BASE}/api/deployment/checklist").json())
        show("monitoring alerts", client.get(f"{BASE}/api/monitoring/alerts").json())


if __name__ == "__main__":
    main()
