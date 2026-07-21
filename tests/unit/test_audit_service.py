from ecommerce_agent.audit.service import AuditService
from ecommerce_agent.persistence.store import InMemoryStore


def test_audit_service_records_trace_and_action_metadata():
    store = InMemoryStore()
    event = AuditService(store).record("tool.executed", "run-1", {"action": "product.update"}, trace_id="trace-1")
    assert event.payload["trace_id"] == "trace-1"
    assert event.payload["action"] == "product.update"
