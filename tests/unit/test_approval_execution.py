import asyncio
from datetime import UTC, datetime, timedelta

import pytest
from pydantic import BaseModel

from ecommerce_agent.approvals.service import ApprovalService
from ecommerce_agent.persistence.store import InMemoryStore


class UpdateArgs(BaseModel):
    product_id: str
    price: float


def test_same_idempotency_key_reuses_approval_and_edit_revalidates():
    service = ApprovalService(argument_models={"product.update": UpdateArgs})
    first = service.propose("product.update", {"product_id": "p-1", "price": 10}, "run-1", idempotency_key="k1")
    second = service.propose("product.update", {"product_id": "p-1", "price": 20}, "run-2", idempotency_key="k1")
    assert first["approval_id"] == second["approval_id"]
    edited = service.edit(first["approval_id"], {"product_id": "p-2", "price": 12}, "operator")
    assert edited.arguments["product_id"] == "p-2"
    with pytest.raises(ValueError, match="参数校验失败"):
        service.edit(first["approval_id"], {"product_id": "p-2"}, "operator")


def test_expired_approval_is_rejected_and_cannot_execute():
    store = InMemoryStore()
    service = ApprovalService(store=store)
    proposal = service.propose("product.update", {"id": "p-1"}, "run-1", expires_at=datetime.now(UTC) - timedelta(seconds=1))
    record = service.expire(proposal["approval_id"])
    assert record.status == "rejected"
    assert any(event.event == "approval.expired" for event in store.audit_events)


def test_approved_command_executes_once_and_audits():
    class Executor:
        def __init__(self) -> None:
            self.calls = 0

        async def execute(self, action, arguments):
            self.calls += 1
            return {"action": action, "arguments": arguments}

    executor = Executor()
    service = ApprovalService()
    proposal = service.propose("product.update", {"id": "p-1"}, "run-1", idempotency_key="exec-1")
    service.decide(proposal["approval_id"], "approved", "operator")
    result = asyncio.run(service.execute(proposal["approval_id"], executor))
    again = asyncio.run(service.execute(proposal["approval_id"], executor))
    assert result == again
    assert executor.calls == 1
    assert any(event.event == "approval.executed" for event in service.store.audit_events)
