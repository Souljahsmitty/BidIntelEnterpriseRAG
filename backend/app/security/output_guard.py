from __future__ import annotations

from backend.app.security.pii_scanner import redact_pii, scan_pii
from backend.app.security.secret_scanner import redact_secrets, scan_secrets

def guard_output(answer_packet: dict) -> dict:
    answer = answer_packet.get("answer", "")
    pii = scan_pii(answer)
    secrets = scan_secrets(answer)
    safe_answer = redact_pii(redact_secrets(answer))
    citations = answer_packet.get("citations", [])
    answer_packet["answer"] = safe_answer
    answer_packet["output_guard"] = {
        "passed": not secrets["has_secrets"] and bool(citations),
        "pii_redacted": pii["has_pii"],
        "secret_redacted": secrets["has_secrets"],
        "citation_gate": bool(citations),
    }
    return answer_packet
