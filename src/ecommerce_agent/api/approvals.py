from typing import Any, cast

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel


class ApprovalDecisionRequest(BaseModel):
    decision: str
    operator: str
    comment: str | None = None


router = APIRouter(prefix="/api/v1/approvals", tags=["审批"])


@router.get("")
async def list_approvals(request: Request) -> list[dict[str, Any]]:
    service = request.app.state.approvals
    return [item.__dict__ for item in service.store.approvals.values()]


@router.post("/{approval_id}/decision")
async def decide_approval(approval_id: str, body: ApprovalDecisionRequest, request: Request) -> dict[str, Any]:
    try:
        record = request.app.state.approvals.decide(approval_id, body.decision, body.operator, body.comment)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="审批记录不存在") from exc
    return cast(dict[str, Any], vars(record))
