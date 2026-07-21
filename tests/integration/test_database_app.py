from pathlib import Path

from fastapi.testclient import TestClient

from ecommerce_agent.api.app import create_app


def test_database_backend_survives_app_recreation(tmp_path: Path, monkeypatch):
    monkeypatch.setenv("STATE_BACKEND", "database")
    monkeypatch.setenv("DATABASE_URL", f"sqlite+pysqlite:///{tmp_path / 'api.db'}")

    first = TestClient(create_app())
    proposal = first.post(
        "/api/v1/tools/propose",
        json={"action": "product.update", "arguments": {"id": "p-db"}},
    ).json()
    first.post(
        f"/api/v1/approvals/{proposal['approval_id']}/decision",
        json={"decision": "approved", "operator": "db-tester"},
    )

    second = TestClient(create_app())
    approvals = second.get("/api/v1/approvals").json()
    audits = second.get("/api/v1/approvals/audit/events").json()
    assert approvals[0]["status"] == "approved"
    assert [event["event"] for event in audits] == ["approval.proposed", "approval.approved"]
