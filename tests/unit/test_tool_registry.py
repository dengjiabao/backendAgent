import pytest

from ecommerce_agent.adapters.mock import MockCommerceAdapter
from ecommerce_agent.tools.policy import ToolPolicy
from ecommerce_agent.tools.registry import ToolRegistry, build_commerce_tools


def test_registry_exposes_mock_read_tools_with_schema_and_capability():
    registry = ToolRegistry()
    for tool in build_commerce_tools(MockCommerceAdapter()):
        registry.register(tool)

    tool = registry.get("product.search")
    assert tool is not None
    assert tool.capability == "product.search"
    assert "query" in tool.input_schema["properties"]
    assert registry.get("order.refund") is None


@pytest.mark.asyncio
async def test_policy_executes_read_tool_and_rejects_missing_capability():
    adapter = MockCommerceAdapter()
    registry = ToolRegistry()
    for tool in build_commerce_tools(adapter):
        registry.register(tool)
    policy = ToolPolicy(registry)

    result = await policy.execute("product.search", {"query": "智能客服"})
    assert result[0].name == "企业级智能客服套装"

    with pytest.raises(PermissionError, match="未声明能力"):
        await policy.execute("order.ship", {"order_id": "o-100"})
