from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any
from uuid import uuid4


def now() -> datetime:
    return datetime.now(UTC)


@dataclass
class ApprovalRecord:
    id: str
    action: str
    arguments: dict[str, Any]
    run_id: str
    status: str = "waiting_approval"
    operator: str | None = None
    comment: str | None = None
    created_at: datetime = field(default_factory=now)
    decided_at: datetime | None = None


@dataclass
class AuditEvent:
    id: str
    event: str
    run_id: str
    payload: dict[str, Any]
    created_at: datetime = field(default_factory=now)


class InMemoryStore:
    """独立模式默认存储；生产模式可替换为 PostgreSQL 实现。"""

    def __init__(self) -> None:
        self.approvals: dict[str, ApprovalRecord] = {}
        self.audit_events: list[AuditEvent] = []
        self._lock = Lock()

    def create_approval(self, action: str, arguments: dict[str, Any], run_id: str) -> ApprovalRecord:
        with self._lock:
            record = ApprovalRecord(str(uuid4()), action, arguments, run_id)
            self.approvals[record.id] = record
            self.record_audit("approval.proposed", run_id, {"approval_id": record.id, "action": action})
            return record

    def decide_approval(self, approval_id: str, decision: str, operator: str, comment: str | None = None) -> ApprovalRecord:
        with self._lock:
            record = self.approvals[approval_id]
            if record.status != "waiting_approval":
                return record
            if decision not in {"approved", "rejected"}:
                raise ValueError("审批决定只能是 approved 或 rejected")
            record.status = decision
            record.operator = operator
            record.comment = comment
            record.decided_at = now()
            self.record_audit(
                f"approval.{decision}",
                record.run_id,
                {"approval_id": approval_id, "operator": operator},
            )
            return record

    def record_audit(self, event: str, run_id: str, payload: dict[str, Any]) -> AuditEvent:
        item = AuditEvent(str(uuid4()), event, run_id, payload)
        self.audit_events.append(item)
        return item
