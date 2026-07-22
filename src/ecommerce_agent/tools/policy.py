import asyncio
from typing import Any

from ecommerce_agent.domain.risk import RiskLevel, RiskPolicy
from ecommerce_agent.security.identity import Identity, RBACService, TenantContext
from ecommerce_agent.tools.registry import ToolRegistry


class ToolPolicy:
    def __init__(self, registry: ToolRegistry, risk_policy: RiskPolicy | None = None) -> None:
        self.registry = registry
        self.risk_policy = risk_policy or RiskPolicy()

    async def execute(
        self,
        name: str,
        arguments: dict[str, Any],
        identity: Identity | None = None,
        tenant: TenantContext | None = None,
    ) -> Any:
        tool = self.registry.get(name)
        if tool is None:
            raise PermissionError(f"未声明能力：{name}")
        if self.risk_policy.classify(name) is not RiskLevel.READ or tool.risk != RiskLevel.READ.value:
            raise PermissionError(f"工具不允许自动执行：{name}")
        if tool.required_roles:
            if identity is None or tenant is None:
                raise PermissionError("工具需要身份和租户上下文")
            RBACService().require(identity, set(tool.required_roles), tenant)
        validated = tool.input_model.model_validate(arguments)
        return await asyncio.wait_for(tool.handler(validated.model_dump()), timeout=tool.timeout_seconds)
