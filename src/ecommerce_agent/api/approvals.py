from typing import Any, cast

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel


class ApprovalDecisionRequest(BaseModel):
    decision: str
    operator: str
    comment: str | None = None


class ApprovalEditRequest(BaseModel):
    arguments: dict[str, Any]
    operator: str


router = APIRouter(prefix="/api/v1/approvals", tags=["审批"])


@router.get("")
async def list_approvals(request: Request) -> list[dict[str, Any]]:
    service = request.app.state.approvals
    return [item.__dict__ for item in service.store.approvals.values()]


@router.get("/audit/events")
async def list_audit_events(request: Request) -> list[dict[str, Any]]:
    service = request.app.state.approvals
    return [vars(item) for item in service.store.audit_events]


@router.post("/{approval_id}/decision")
async def decide_approval(approval_id: str, body: ApprovalDecisionRequest, request: Request) -> dict[str, Any]:
    try:
        record = request.app.state.approvals.decide(approval_id, body.decision, body.operator, body.comment)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="审批记录不存在") from exc
    return cast(dict[str, Any], vars(record))


@router.patch("/{approval_id}")
async def edit_approval(approval_id: str, body: ApprovalEditRequest, request: Request) -> dict[str, Any]:
    service = request.app.state.approvals
    try:
        record = service.edit(approval_id, body.arguments, body.operator)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="审批记录不存在") from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return cast(dict[str, Any], vars(record))


@router.post("/{approval_id}/expire")
async def expire_approval(approval_id: str, request: Request) -> dict[str, Any]:
    service = request.app.state.approvals
    try:
        record = service.expire(approval_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="审批记录不存在") from exc
    return cast(dict[str, Any], vars(record))
