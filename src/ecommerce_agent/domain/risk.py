from enum import StrEnum


class RiskLevel(StrEnum):
    READ = "read"
    WRITE_CONFIRM = "write_confirm"
    FORBIDDEN = "forbidden"


class RiskPolicy:
    def __init__(self, overrides: dict[str, RiskLevel] | None = None) -> None:
        self._overrides = overrides or {}

    def classify(self, action: str) -> RiskLevel:
        if action in self._overrides:
            return self._overrides[action]
        if action in {"order.refund", "resource.delete", "role.permission.update"}:
            return RiskLevel.FORBIDDEN
        if action.endswith((".list", ".get", ".metrics", ".search")):
            return RiskLevel.READ
        if action in {"product.update", "product.create", "order.ship", "order.pay"}:
            return RiskLevel.WRITE_CONFIRM
        return RiskLevel.WRITE_CONFIRM
