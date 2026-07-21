from datetime import datetime
from typing import Any
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from ecommerce_agent.persistence.models import ApprovalRow, AuditEventRow
from ecommerce_agent.persistence.store import ApprovalRecord, AuditEvent, now


class DatabaseStore:
    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self.sessions = sessions

    @property
    def approvals(self) -> dict[str, ApprovalRecord]:
        with self.sessions() as session:
            rows = session.scalars(select(ApprovalRow).order_by(ApprovalRow.created_at)).all()
            return {row.id: self._approval(row) for row in rows}

    @property
    def audit_events(self) -> list[AuditEvent]:
        with self.sessions() as session:
            rows = session.scalars(select(AuditEventRow).order_by(AuditEventRow.created_at)).all()
            return [self._audit(row) for row in rows]

    def create_approval(
        self,
        action: str,
        arguments: dict[str, Any],
        run_id: str,
        idempotency_key: str | None = None,
        expires_at: datetime | None = None,
    ) -> ApprovalRecord:
        with self.sessions() as session:
            if idempotency_key:
                existing = session.scalar(select(ApprovalRow).where(ApprovalRow.idempotency_key == idempotency_key))
                if existing is not None:
                    return self._approval(existing)
        record = ApprovalRecord(str(uuid4()), action, arguments, run_id, idempotency_key=idempotency_key, expires_at=expires_at)
        with self.sessions.begin() as session:
            session.add(ApprovalRow(**record.__dict__))
        self.record_audit("approval.proposed", run_id, {"approval_id": record.id, "action": action})
        return record

    def update_approval(self, approval_id: str, arguments: dict[str, Any], operator: str) -> ApprovalRecord:
        with self.sessions.begin() as session:
            row = session.get(ApprovalRow, approval_id)
            if row is None:
                raise KeyError(approval_id)
            if row.status == "waiting_approval":
                row.arguments = arguments
                row.operator = operator
                row.edited_at = now()
            return self._approval(row)

    def mark_executed(self, approval_id: str, result: Any) -> ApprovalRecord:
        with self.sessions.begin() as session:
            row = session.get(ApprovalRow, approval_id)
            if row is None:
                raise KeyError(approval_id)
            row.execution_result = result
            row.executed_at = now()
            return self._approval(row)

    def decide_approval(self, approval_id: str, decision: str, operator: str, comment: str | None = None) -> ApprovalRecord:
        if decision not in {"approved", "rejected"}:
            raise ValueError("审批决定只能是 approved 或 rejected")
        with self.sessions.begin() as session:
            row = session.get(ApprovalRow, approval_id)
            if row is None:
                raise KeyError(approval_id)
            if row.status == "waiting_approval":
                row.status = decision
                row.operator = operator
                row.comment = comment
                row.decided_at = now()
            record = self._approval(row)
        self.record_audit(f"approval.{record.status}", record.run_id, {"approval_id": approval_id, "operator": operator})
        return record

    def record_audit(self, event: str, run_id: str, payload: dict[str, Any]) -> AuditEvent:
        item = AuditEvent(str(uuid4()), event, run_id, payload)
        with self.sessions.begin() as session:
            session.add(AuditEventRow(**item.__dict__))
        return item

    @staticmethod
    def _approval(row: ApprovalRow) -> ApprovalRecord:
        return ApprovalRecord(
            row.id,
            row.action,
            row.arguments,
            row.run_id,
            row.status,
            row.operator,
            row.comment,
            row.created_at,
            row.decided_at,
            row.idempotency_key,
            row.expires_at,
            row.edited_at,
            row.execution_result,
            row.executed_at,
        )

    @staticmethod
    def _audit(row: AuditEventRow) -> AuditEvent:
        return AuditEvent(row.id, row.event, row.run_id, row.payload, row.created_at)
