from __future__ import annotations
import hashlib
import math
import re

DIMENSIONS = 1536

def tokens(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z0-9]+", text.lower())

def embed_text(text: str, dimensions: int = DIMENSIONS) -> list[float]:
    vec = [0.0] * dimensions
    for token in tokens(text):
        digest = hashlib.sha256(token.encode()).digest()
        idx = int.from_bytes(digest[:4], "big") % dimensions
        sign = 1 if digest[4] % 2 == 0 else -1
        vec[idx] += sign
    norm = math.sqrt(sum(value * value for value in vec)) or 1.0
    return [round(value / norm, 6) for value in vec]

def cosine(left: list[float], right: list[float]) -> float:
    return sum(a * b for a, b in zip(left, right))
