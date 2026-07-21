from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ValidationError

from ecommerce_agent.domain.risk import RiskLevel, RiskPolicy
from ecommerce_agent.persistence.store import ApprovalRecord, InMemoryStore, StateStore


class ApprovalService:
    def __init__(
        self,
        store: StateStore | None = None,
        policy: RiskPolicy | None = None,
        argument_models: dict[str, type[BaseModel]] | None = None,
    ) -> None:
        self.store = store or InMemoryStore()
        self.policy = policy or RiskPolicy()
        self.argument_models = argument_models or {}
        self._execution_results: dict[str, Any] = {}

    def propose(
        self,
        action: str,
        arguments: dict[str, Any],
        run_id: str,
        idempotency_key: str | None = None,
        expires_at: datetime | None = None,
    ) -> dict[str, Any]:
        risk = self.policy.classify(action)
        self._validate(action, arguments)
        if risk is RiskLevel.FORBIDDEN:
            self.store.record_audit("tool.blocked", run_id, {"action": action})
            return {"status": "blocked", "risk": risk.value, "action": action, "run_id": run_id}
        if risk is RiskLevel.READ:
            return {"status": "executing", "risk": risk.value, "action": action, "run_id": run_id}
        record = self.store.create_approval(action, arguments, run_id, idempotency_key, expires_at)
        return {
            "status": record.status,
            "risk": risk.value,
            "approval_id": record.id,
            "run_id": run_id,
        }

    def decide(self, approval_id: str, decision: str, operator: str, comment: str | None = None) -> ApprovalRecord:
        return self.store.decide_approval(approval_id, decision, operator, comment)

    def edit(self, approval_id: str, arguments: dict[str, Any], operator: str) -> ApprovalRecord:
        record = self.store.approvals[approval_id]
        if record.status != "waiting_approval":
            return record
        self._validate(record.action, arguments)
        record = self.store.update_approval(approval_id, arguments, operator)
        self.store.record_audit("approval.edited", record.run_id, {"approval_id": approval_id, "operator": operator})
        return record

    def expire(self, approval_id: str) -> ApprovalRecord:
        record = self.store.approvals[approval_id]
        if record.status == "waiting_approval":
            record = self.store.decide_approval(approval_id, "rejected", "system", "审批已超时")
            self.store.record_audit("approval.expired", record.run_id, {"approval_id": approval_id})
        return record

    async def execute(self, approval_id: str, executor: Any) -> Any:
        record = self.store.approvals[approval_id]
        if record.status != "approved":
            raise PermissionError("只有 approved 审批才能执行")
        if record.execution_result is not None:
            return record.execution_result
        try:
            result = await executor.execute(record.action, record.arguments)
        except Exception as exc:  # noqa: BLE001
            self.store.record_audit("approval.execution_failed", record.run_id, {"approval_id": approval_id, "error": str(exc)})
            raise
        self._execution_results[approval_id] = result
        self.store.mark_executed(approval_id, result)
        self.store.record_audit("approval.executed", record.run_id, {"approval_id": approval_id})
        return result

    def expire_due(self, now: datetime | None = None) -> list[ApprovalRecord]:
        current = now or datetime.now(UTC)
        due = [
            record
            for record in self.store.approvals.values()
            if record.expires_at and record.expires_at <= current and record.status == "waiting_approval"
        ]
        return [self.expire(record.id) for record in due]

    def _validate(self, action: str, arguments: dict[str, Any]) -> None:
        model = self.argument_models.get(action)
        if model is None:
            return
        try:
            model.model_validate(arguments)
        except ValidationError as exc:
            raise ValueError(f"参数校验失败：{exc}") from exc
