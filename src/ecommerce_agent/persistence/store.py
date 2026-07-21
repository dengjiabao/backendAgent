from dataclasses import dataclass, field
from datetime import UTC, datetime
from threading import Lock
from typing import Any, Protocol
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
    idempotency_key: str | None = None
    expires_at: datetime | None = None
    edited_at: datetime | None = None
    execution_result: Any = None
    executed_at: datetime | None = None


@dataclass
class AuditEvent:
    id: str
    event: str
    run_id: str
    payload: dict[str, Any]
    created_at: datetime = field(default_factory=now)


class StateStore(Protocol):
    @property
    def approvals(self) -> dict[str, ApprovalRecord]: ...

    @property
    def audit_events(self) -> list[AuditEvent]: ...

    def create_approval(
        self,
        action: str,
        arguments: dict[str, Any],
        run_id: str,
        idempotency_key: str | None = None,
        expires_at: datetime | None = None,
    ) -> ApprovalRecord: ...

    def decide_approval(self, approval_id: str, decision: str, operator: str, comment: str | None = None) -> ApprovalRecord: ...

    def update_approval(self, approval_id: str, arguments: dict[str, Any], operator: str) -> ApprovalRecord: ...

    def mark_executed(self, approval_id: str, result: Any) -> ApprovalRecord: ...

    def record_audit(self, event: str, run_id: str, payload: dict[str, Any]) -> AuditEvent: ...


class InMemoryStore:
    """独立模式默认存储；生产模式可替换为 PostgreSQL 实现。"""

    def __init__(self) -> None:
        self.approvals: dict[str, ApprovalRecord] = {}
        self.audit_events: list[AuditEvent] = []
        self._idempotency: dict[str, str] = {}
        self._lock = Lock()

    def create_approval(
        self,
        action: str,
        arguments: dict[str, Any],
        run_id: str,
        idempotency_key: str | None = None,
        expires_at: datetime | None = None,
    ) -> ApprovalRecord:
        with self._lock:
            if idempotency_key and idempotency_key in self._idempotency:
                return self.approvals[self._idempotency[idempotency_key]]
            record = ApprovalRecord(
                str(uuid4()), action, arguments, run_id, idempotency_key=idempotency_key, expires_at=expires_at
            )
            self.approvals[record.id] = record
            if idempotency_key:
                self._idempotency[idempotency_key] = record.id
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

    def update_approval(self, approval_id: str, arguments: dict[str, Any], operator: str) -> ApprovalRecord:
        with self._lock:
            record = self.approvals[approval_id]
            if record.status == "waiting_approval":
                record.arguments = arguments
                record.edited_at = now()
                record.operator = operator
            return record

    def record_audit(self, event: str, run_id: str, payload: dict[str, Any]) -> AuditEvent:
        item = AuditEvent(str(uuid4()), event, run_id, payload)
        self.audit_events.append(item)
        return item

    def mark_executed(self, approval_id: str, result: Any) -> ApprovalRecord:
        with self._lock:
            record = self.approvals[approval_id]
            record.execution_result = result
            record.executed_at = now()
            return record
