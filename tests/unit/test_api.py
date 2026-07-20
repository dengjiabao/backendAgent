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


def test_streaming_chat_emits_named_events():
    client = TestClient(create_app())
    response = client.post("/api/v1/chat/stream", json={"message": "查看订单"})
    assert response.status_code == 200
    assert "event: run_started" in response.text
    assert "event: final" in response.text
