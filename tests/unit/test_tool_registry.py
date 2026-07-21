import pytest

from ecommerce_agent.adapters.mock import MockCommerceAdapter
from ecommerce_agent.security.identity import Identity, TenantContext
from ecommerce_agent.tools.policy import ToolPolicy
from ecommerce_agent.tools.registry import ProductSearchArgs, ToolDefinition, ToolRegistry, build_commerce_tools


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


@pytest.mark.asyncio
async def test_tool_policy_checks_identity_role_and_tenant():
    async def handler(arguments):
        return arguments

    registry = ToolRegistry()
    registry.register(
        ToolDefinition(
            "product.search",
            "搜索商品",
            "product.search",
            ProductSearchArgs,
            handler,
            required_roles=frozenset({"operator"}),
        )
    )
    policy = ToolPolicy(registry)
    with pytest.raises(PermissionError, match="角色不足"):
        await policy.execute(
            "product.search",
            {"query": "a"},
            identity=Identity("u-1", "tenant-a", {"viewer"}),
            tenant=TenantContext("tenant-a"),
        )
