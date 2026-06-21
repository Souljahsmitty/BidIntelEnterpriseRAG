from __future__ import annotations
import re

PII_PATTERNS = {
    "email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "phone": r"\b\d{3}[-.) ]+\d{3}[-. ]+\d{4}\b",
}

def scan_pii(text: str) -> dict:
    findings = {name: re.findall(pattern, text) for name, pattern in PII_PATTERNS.items()}
    findings = {name: values for name, values in findings.items() if values}
    return {"has_pii": bool(findings), "findings": findings}

def redact_pii(text: str) -> str:
    redacted = text
    for pattern in PII_PATTERNS.values():
        redacted = re.sub(pattern, "[REDACTED_PII]", redacted)
    return redacted
