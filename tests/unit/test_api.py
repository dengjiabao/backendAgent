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


def test_streaming_chat_accepts_conversation_id_and_resume_patch():
    client = TestClient(create_app())
    response = client.post("/api/v1/chat/stream", json={"message": "修改商品 p-100", "conversation_id": "c-1"})
    assert "event: approval_required" in response.text
    resumed = client.post("/api/v1/chat/resume", json={"conversation_id": "c-1", "patch": {"status": "approved"}})
    assert resumed.status_code == 200
    assert resumed.json()["status"] == "approved"


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


def test_approval_edit_and_expire_endpoints():
    client = TestClient(create_app())
    proposal = client.post("/api/v1/tools/propose", json={"action": "product.update", "arguments": {"id": "p-1"}}).json()
    approval_id = proposal["approval_id"]
    edited = client.patch(f"/api/v1/approvals/{approval_id}", json={"arguments": {"id": "p-2"}, "operator": "tester"})
    assert edited.status_code == 200
    expired = client.post(f"/api/v1/approvals/{approval_id}/expire")
    assert expired.status_code == 200
    assert expired.json()["status"] == "rejected"


def test_local_auth_token_and_identity_endpoint():
    client = TestClient(create_app())
    token = client.post("/api/v1/auth/token", json={"subject": "u-1", "tenant_id": "tenant-a", "roles": ["operator"]}).json()["access_token"]
    identity = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert identity.status_code == 200
    assert identity.json()["tenant_id"] == "tenant-a"
