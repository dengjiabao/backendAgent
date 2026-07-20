from typing import Any

from ecommerce_agent.domain.risk import RiskLevel, RiskPolicy
from ecommerce_agent.persistence.store import ApprovalRecord, InMemoryStore


class ApprovalService:
    def __init__(self, store: InMemoryStore | None = None, policy: RiskPolicy | None = None) -> None:
        self.store = store or InMemoryStore()
        self.policy = policy or RiskPolicy()

    def propose(self, action: str, arguments: dict[str, Any], run_id: str) -> dict[str, Any]:
        risk = self.policy.classify(action)
        if risk is RiskLevel.FORBIDDEN:
            self.store.record_audit("tool.blocked", run_id, {"action": action})
            return {"status": "blocked", "risk": risk.value, "action": action, "run_id": run_id}
        if risk is RiskLevel.READ:
            return {"status": "executing", "risk": risk.value, "action": action, "run_id": run_id}
        record = self.store.create_approval(action, arguments, run_id)
        return {
            "status": record.status,
            "risk": risk.value,
            "approval_id": record.id,
            "run_id": run_id,
        }

    def decide(self, approval_id: str, decision: str, operator: str, comment: str | None = None) -> ApprovalRecord:
        return self.store.decide_approval(approval_id, decision, operator, comment)
