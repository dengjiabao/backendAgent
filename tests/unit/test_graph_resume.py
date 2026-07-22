import asyncio

from ecommerce_agent.agents.graph import EcommerceAgentGraph
from ecommerce_agent.agents.service import AgentService
from ecommerce_agent.config import Settings


def test_graph_persists_waiting_approval_and_can_resume():
    graph = EcommerceAgentGraph(AgentService(Settings(_env_file=None)))
    result = asyncio.run(graph.run("修改商品 p-100", thread_id="conversation-1"))
    assert result["status"] == "waiting_approval"
    assert graph.checkpoint.load("conversation-1")["approval_id"] == result["approval_id"]
    resumed = asyncio.run(graph.resume("conversation-1", {"status": "approved"}))
    assert resumed["status"] == "approved"
