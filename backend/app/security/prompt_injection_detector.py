from __future__ import annotations
import re

PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"reveal\s+(the\s+)?system\s+prompt",
    r"disable\s+citations",
    r"dump\s+(the\s+)?db",
    r"show\s+me\s+all\s+payroll",
    r"bypass\s+(tenant|role|security)",
]

def detect_prompt_injection(text: str) -> dict:
    lowered = text.lower()
    matches = [pattern for pattern in PATTERNS if re.search(pattern, lowered)]
    return {
        "blocked": bool(matches),
        "matches": matches,
        "reason": "prompt_injection_detected" if matches else "clean",
    }
