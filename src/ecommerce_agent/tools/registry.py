from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel


class ProductSearchArgs(BaseModel):
    query: str


class OrderListArgs(BaseModel):
    status: str | None = None


class OrderGetArgs(BaseModel):
    order_id: str


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    capability: str
    input_model: type[BaseModel]
    handler: Callable[[dict[str, Any]], Awaitable[Any]]
    risk: str = "read"
    timeout_seconds: float = 10.0
    idempotent: bool = True
    required_roles: frozenset[str] = frozenset()

    @property
    def input_schema(self) -> dict[str, Any]:
        return self.input_model.model_json_schema()


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(self, tool: ToolDefinition) -> None:
        if tool.name in self._tools:
            raise ValueError(f"工具已注册：{tool.name}")
        self._tools[tool.name] = tool

    def get(self, name: str) -> ToolDefinition | None:
        return self._tools.get(name)

    def list(self) -> list[ToolDefinition]:
        return list(self._tools.values())


def build_commerce_tools(adapter: Any) -> list[ToolDefinition]:
    capabilities: dict[str, bool] = getattr(adapter, "capabilities", lambda: {})()
    async def search(arguments: dict[str, Any]) -> Any:
        args = ProductSearchArgs.model_validate(arguments)
        return await adapter.search_products(args.query)

    async def list_orders(arguments: dict[str, Any]) -> Any:
        args = OrderListArgs.model_validate(arguments)
        return await adapter.list_orders(args.status)

    async def get_order(arguments: dict[str, Any]) -> Any:
        args = OrderGetArgs.model_validate(arguments)
        return await adapter.get_order(args.order_id)

    tools = [
        ToolDefinition("product.search", "按名称搜索商品", "product.search", ProductSearchArgs, search),
        ToolDefinition("order.list", "查询订单列表", "order.list", OrderListArgs, list_orders),
        ToolDefinition("order.get", "查询订单详情", "order.get", OrderGetArgs, get_order),
    ]
    return [tool for tool in tools if capabilities.get(tool.capability, True)]
