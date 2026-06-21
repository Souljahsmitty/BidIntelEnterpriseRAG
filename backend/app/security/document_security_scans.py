from __future__ import annotations

from backend.app.security.pii_scanner import redact_pii, scan_pii
from backend.app.security.prompt_injection_detector import detect_prompt_injection
from backend.app.security.secret_scanner import redact_secrets, scan_secrets

def scan_upload_document(filename: str, text: str) -> dict:
    injection = detect_prompt_injection(text)
    pii = scan_pii(text)
    secrets = scan_secrets(text)
    blocked = injection["blocked"] or secrets["has_secrets"]
    safe_text = redact_pii(redact_secrets(text))
    return {
        "filename": filename,
        "accepted_for_chunking": not blocked,
        "action": "quarantine" if blocked else ("redact_then_store" if pii["has_pii"] else "store"),
        "prompt_injection": injection,
        "pii": pii,
        "secrets": secrets,
        "safe_text": safe_text,
        "production_equivalent": "Upload quarantine, Textract/OCR, malware scanning, DLP, and audit row before chunking.",
    }
