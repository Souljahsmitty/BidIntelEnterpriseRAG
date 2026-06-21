from __future__ import annotations


def evaluate_alerts(metrics: dict) -> dict:
    rules = [
        {
            "name": "High guardrail block rate",
            "metric": "guardrail_block_rate",
            "threshold": 0.10,
            "actual": metrics.get("guardrail_block_rate", 0),
            "operator": ">",
            "severity": "warning",
        },
        {
            "name": "Slow RAG answer latency",
            "metric": "p95_latency_ms",
            "threshold": 2500,
            "actual": metrics.get("p95_latency_ms", 0),
            "operator": ">",
            "severity": "critical",
        },
        {
            "name": "Retrieval returning empty context",
            "metric": "empty_retrieval_count",
            "threshold": 0,
            "actual": metrics.get("empty_retrieval_count", 0),
            "operator": ">",
            "severity": "critical",
        },
    ]
    alerts = [
        {
            **rule,
            "status": "ALARM",
            "delivery": {
                "email": f"simulated-email: bidintel-alerts@example.com <- {rule['name']}",
                "slack": f"simulated-slack: #bidintel-ops <- {rule['name']}",
                "pagerduty": f"simulated-pagerduty: incident created for {rule['severity']} alert",
            },
            "acknowledge_runbook": [
                "Open monitoring dashboard.",
                "Confirm metric crossed threshold.",
                "Check recent audit/security events.",
                "Assign owner and acknowledge alert.",
                "Run smoke test after fix.",
            ],
        }
        for rule in rules
        if rule["actual"] > rule["threshold"]
    ]
    return {
        "tool": "local CloudWatch-style alert simulation",
        "production_equivalent": "Amazon CloudWatch alarms on API latency, guardrail blocks, retrieval failures, Bedrock errors, and queue depth.",
        "metrics": metrics,
        "rules": rules,
        "alerts": alerts,
        "status": "ALARM" if alerts else "OK",
        "dashboard": {
            "retrieval_latency_ms": metrics.get("p95_latency_ms", 0),
            "token_cost_usd": metrics.get("token_cost_usd", 0.42),
            "error_rate": metrics.get("error_rate", 0.03),
            "retrieval_hit_rate": metrics.get("retrieval_hit_rate", 0.91),
            "guardrail_block_rate": metrics.get("guardrail_block_rate", 0),
        },
    }
