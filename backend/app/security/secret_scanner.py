from __future__ import annotations
import re

SECRET_PATTERNS = {
    "aws_access_key": r"AKIA[0-9A-Z]{16}",
    "aws_secret": r"AWS_SECRET_ACCESS_KEY\s*=\s*[A-Za-z0-9/+=]{8,}",
    "bearer_token": r"Bearer\s+[A-Za-z0-9._-]{12,}",
    "private_key": r"-----BEGIN\s+PRIVATE\s+KEY-----",
}

def scan_secrets(text: str) -> dict:
    findings = {name: re.findall(pattern, text) for name, pattern in SECRET_PATTERNS.items()}
    findings = {name: values for name, values in findings.items() if values}
    return {"has_secrets": bool(findings), "findings": findings}

def redact_secrets(text: str) -> str:
    redacted = text
    for pattern in SECRET_PATTERNS.values():
        redacted = re.sub(pattern, "[REDACTED_SECRET]", redacted)
    return redacted
