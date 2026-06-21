from __future__ import annotations

import json
import os
from pathlib import Path

import httpx


ROOT = Path(__file__).resolve().parents[1]
BASE = os.environ.get("BASE_URL", "http://127.0.0.1:18129")
DOC = ROOT / "sample_docs" / "fresh_mock_contract_rfp.txt"


def show(title: str, payload: dict) -> None:
    print(f"\n=== {title} ===")
    print(json.dumps(payload, indent=2, default=str)[:5000])


def main() -> None:
    with httpx.Client(timeout=30) as client:
        show("health before fresh upload", client.get(f"{BASE}/health").json())

        with DOC.open("rb") as handle:
            upload = client.post(
                f"{BASE}/api/upload",
                data={
                    "title": "Fresh Mock Contract RFP",
                    "tenant_id": "tenant_acme",
                    "classification": "cui",
                    "user": "adam.davis",
                    "role": "proposal_writer",
                },
                files={"files": (DOC.name, handle, "text/plain")},
            ).json()
        show("upload -> security -> chunk -> embed -> pgvector", upload)

        vector_db = client.get(f"{BASE}/api/vector-db").json()
        show("vector db rows after upload", {
            "store": vector_db.get("store"),
            "row_count": vector_db.get("row_count"),
            "document_count": vector_db.get("document_count"),
            "indexes": vector_db.get("indexes"),
            "first_rows": vector_db.get("rows", [])[:3],
        })

        ask = client.post(
            f"{BASE}/api/ask",
            json={
                "question": "What does the fresh contract require for SOC monitoring and what risk factors affect bid scoring?",
                "tenant_id": "tenant_acme",
                "user": "adam.davis",
                "role": "proposal_writer",
            },
        ).json()
        show("ask -> pgvector retrieval -> RRF -> rerank -> citations -> trace", {
            "answer": ask.get("answer"),
            "citations": ask.get("citations"),
            "retrieved_context": ask.get("retrieved_context", [])[:3],
            "eval": ask.get("eval"),
            "trace": ask.get("trace"),
        })

        show("health after fresh upload", client.get(f"{BASE}/health").json())


if __name__ == "__main__":
    main()
