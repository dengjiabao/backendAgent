import asyncio

from ecommerce_agent.agents.graph import build_langgraph
from ecommerce_agent.agents.service import AgentService
from ecommerce_agent.config import Settings


def test_mock_product_query_returns_standard_model():
    result = asyncio.run(AgentService(Settings(_env_file=None)).answer("查询商品"))
    assert result["type"] == "commerce"
    assert result["source"] == "mock"


def test_write_proposal_requires_approval():
    proposal = AgentService(Settings(_env_file=None)).propose("product.update", {"id": "p-100"})
    assert proposal["status"] == "waiting_approval"


def test_langgraph_runtime_can_invoke_agent_node():
    graph = build_langgraph(AgentService(Settings(_env_file=None)))
    result = asyncio.run(graph.ainvoke({"message": "查询商品"}))
    assert result["result"]["type"] == "commerce"
