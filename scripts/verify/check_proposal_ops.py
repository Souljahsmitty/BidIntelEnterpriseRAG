from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app


def show(label: str, value) -> None:
    print(f"{label}: {value}")


def main() -> None:
    client = TestClient(app)

    boot = client.post("/api/bootstrap").json()
    show("Bootstrap", "PASS")
    show("Database mode", boot["database"]["status"])

    rfp_text = (
        "C.3.1 The contractor shall provide 24/7 SOC monitoring services. "
        "C.3.2 The offeror must document incident escalation procedures. "
        "M.1 The proposal must show transition risk controls."
    )
    extract = client.post(
        "/api/compliance/extract",
        files={"rfp_file": ("proposal_ops_demo_rfp.txt", rfp_text, "text/plain")},
    ).json()
    assert extract["count"] >= 3
    show("Ch38 compliance extract", f"PASS ({extract['count']} requirements)")

    requirements = client.get("/api/compliance/requirements").json()["requirements"]
    requirement = requirements[0]
    trace = client.get(f"/api/compliance/requirements/{requirement['id']}/trace").json()
    assert trace["confidence_score"] > 0
    show("Ch39 requirement trace", f"PASS (confidence={trace['confidence_score']})")

    workspace = client.post("/api/proposals", json={"name": "DHS Cyber Modernization Proposal"}).json()
    assert len(workspace["sections"]) >= 4
    section_id = workspace["sections"][0]["id"]
    show("Ch40 proposal workspace", f"PASS ({len(workspace['sections'])} sections)")

    library = client.get("/api/content-library/search", params={"q": "monitoring"}).json()["results"]
    assert library
    inserted = client.post(
        "/api/content-library/insert",
        json={"section_id": section_id, "content_id": library[0]["id"]},
    ).json()
    assert inserted["section"]["evidence_refs"]
    show("Ch41 content reuse", f"PASS ({len(inserted['section']['evidence_refs'])} evidence refs)")

    issue = client.post(
        "/api/reviews/issues",
        json={
            "issue": "Red Team: cite the SLA evidence.",
            "severity": "High",
            "owner": "adam.davis",
            "comment": "Tie the answer to requirement trace evidence.",
        },
    ).json()
    resolved = client.post(
        f"/api/reviews/issues/{issue['id']}",
        json={"status": "Resolved", "comment": "Evidence citation added."},
    ).json()
    assert resolved["response_history"]
    show("Ch42 review workflow", "PASS (history preserved)")

    health = client.get("/api/proposal-health").json()
    assert "readiness_score" in health
    show("Ch43 health dashboard", f"PASS (readiness={health['readiness_score']})")

    audit = client.get("/api/audit", params={"role": "admin", "user": "admin"}).json()
    assert audit["events"]
    show("Audit proof", f"PASS ({len(audit['events'])} events)")

    print("BidIntel Ch38-Ch43 proposal operations verification complete.")


if __name__ == "__main__":
    main()
