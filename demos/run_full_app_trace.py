from __future__ import annotations
import json
from backend.app.workflows.ingest_graph import run_ingest_workflow
from backend.app.main import AskRequest, ask

text = "3.1 Technical Approach\nThe contractor shall provide 24/7 SOC monitoring services.\nM.1 Evaluation\nTechnical approach is weighted 40 percent."
upload = run_ingest_workflow("demo_rfp.txt", text, "tenant_acme", "learner", {"title": "Demo RFP", "classification": "cui", "role": "proposal_writer"})
answer = ask(AskRequest(question="Find SOC modernization proposal language."))
print(json.dumps({
    "expected_output": "upload stored, ask returns citations, RAGAS score, Phoenix trace",
    "upload_status": upload["workflow_status"],
    "citation_count": len(answer.get("citations", [])),
    "trace_id": answer.get("trace", {}).get("trace_id"),
    "eval": answer.get("eval"),
}, indent=2))
