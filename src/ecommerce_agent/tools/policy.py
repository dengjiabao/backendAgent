import asyncio
from typing import Any

from ecommerce_agent.domain.risk import RiskLevel, RiskPolicy
from ecommerce_agent.tools.registry import ToolRegistry


class ToolPolicy:
    def __init__(self, registry: ToolRegistry, risk_policy: RiskPolicy | None = None) -> None:
        self.registry = registry
        self.risk_policy = risk_policy or RiskPolicy()

    async def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        tool = self.registry.get(name)
        if tool is None:
            raise PermissionError(f"未声明能力：{name}")
        if self.risk_policy.classify(name) is not RiskLevel.READ or tool.risk != RiskLevel.READ.value:
            raise PermissionError(f"工具不允许自动执行：{name}")
        validated = tool.input_model.model_validate(arguments)
        return await asyncio.wait_for(tool.handler(validated.model_dump()), timeout=tool.timeout_seconds)
