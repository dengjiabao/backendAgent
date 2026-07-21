from fastapi.testclient import TestClient

from ecommerce_agent.api.app import create_app


def test_health_and_write_proposal():
    client = TestClient(create_app())
    assert client.get("/health").json() == {"status": "ok", "mode": "standalone"}
    response = client.post(
        "/api/v1/tools/propose",
        json={"action": "product.update", "arguments": {"id": "p-100"}},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "waiting_approval"
    approval_id = response.json()["approval_id"]
    decision = client.post(
        f"/api/v1/approvals/{approval_id}/decision",
        json={"decision": "approved", "operator": "tester"},
    )
    assert decision.status_code == 200
    assert decision.json()["status"] == "approved"


def test_streaming_chat_emits_named_events():
    client = TestClient(create_app())
    response = client.post("/api/v1/chat/stream", json={"message": "查看订单"})
    assert response.status_code == 200
    assert "event: run_started" in response.text
    assert "event: final" in response.text


def test_markdown_ingestion_is_searchable():
    client = TestClient(create_app())
    ingested = client.post(
        "/api/v1/knowledge/markdown",
        headers={"x-filename": "policy.md"},
        content="# 订单权限\n\nadmin:order:list 可以查询订单",
    )
    assert ingested.json()["chunk_count"] == 1
    result = client.post("/api/v1/chat", json={"message": "admin:order:list"})
    assert result.json()["citations"]


def test_chat_routes_refund_request_to_safety_block():
    client = TestClient(create_app())
    result = client.post("/api/v1/chat", json={"message": "给订单退款"}).json()
    assert result["route"] == "safety"
    assert result["status"] == "blocked"
