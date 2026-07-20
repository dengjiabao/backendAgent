import asyncio

from ecommerce_agent.agents.service import AgentService
from ecommerce_agent.config import Settings


def test_mock_product_query_returns_standard_model():
    result = asyncio.run(AgentService(Settings(_env_file=None)).answer("查询商品"))
    assert result["type"] == "commerce"
    assert result["source"] == "mock"


def test_write_proposal_requires_approval():
    proposal = AgentService(Settings(_env_file=None)).propose("product.update", {"id": "p-100"})
    assert proposal["status"] == "waiting_approval"
