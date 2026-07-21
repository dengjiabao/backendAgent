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

    def create_approval(self, action: str, arguments: dict[str, Any], run_id: str) -> ApprovalRecord:
        record = ApprovalRecord(str(uuid4()), action, arguments, run_id)
        with self.sessions.begin() as session:
            session.add(ApprovalRow(**record.__dict__))
        self.record_audit("approval.proposed", run_id, {"approval_id": record.id, "action": action})
        return record

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
        return ApprovalRecord(row.id, row.action, row.arguments, row.run_id, row.status, row.operator, row.comment, row.created_at, row.decided_at)

    @staticmethod
    def _audit(row: AuditEventRow) -> AuditEvent:
        return AuditEvent(row.id, row.event, row.run_id, row.payload, row.created_at)
