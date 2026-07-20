from typing import Protocol


class ApprovalPort(Protocol):
    async def create(self, action: str, arguments: dict[str, object], run_id: str) -> str: ...


class AuditPort(Protocol):
    async def record(self, event: str, payload: dict[str, object]) -> None: ...
