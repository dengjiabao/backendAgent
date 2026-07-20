from ecommerce_agent.approvals.service import ApprovalService


def test_approval_can_be_approved_once():
    service = ApprovalService()
    proposal = service.propose("product.update", {"id": "p-100"}, "run-1")
    record = service.decide(proposal["approval_id"], "approved", "operator-1")
    assert record.status == "approved"
    again = service.decide(proposal["approval_id"], "rejected", "operator-2")
    assert again.status == "approved"


def test_forbidden_action_is_blocked_without_approval():
    proposal = ApprovalService().propose("order.refund", {"id": "o-1"}, "run-2")
    assert proposal["status"] == "blocked"
