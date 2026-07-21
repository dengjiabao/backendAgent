from typing import Any

from ecommerce_agent.persistence.store import AuditEvent, StateStore


class AuditService:
    """统一写入带 Trace ID 的结构化审计事件。"""

    def __init__(self, store: StateStore) -> None:
        self.store = store

    def record(self, event: str, run_id: str, payload: dict[str, Any], trace_id: str | None = None) -> AuditEvent:
        data = dict(payload)
        if trace_id is not None:
            data["trace_id"] = trace_id
        return self.store.record_audit(event, run_id, data)
