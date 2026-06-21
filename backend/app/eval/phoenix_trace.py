from __future__ import annotations
import time
import uuid
from backend.app.services.store import TRACES

def start_trace(name: str) -> dict:
    trace = {"trace_id": f"trace-{uuid.uuid4().hex[:8]}", "name": name, "spans": [], "started_at": time.time()}
    TRACES[trace["trace_id"]] = trace
    return trace

def add_span(trace: dict, name: str, ms: int, status: str, details: dict | None = None) -> None:
    trace["spans"].append({"name": name, "latency_ms": ms, "status": status, "details": details or {}})

def finish_trace(trace: dict) -> dict:
    trace["total_ms"] = sum(span["latency_ms"] for span in trace["spans"])
    trace["tool"] = "Phoenix local trace simulation"
    trace["production_equivalent"] = "Arize Phoenix traces for retrieve, rerank, LLM, eval, and guardrail spans"
    return trace
