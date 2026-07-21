import asyncio

from ecommerce_agent.agents.graph import build_multi_agent_graph
from ecommerce_agent.agents.service import AgentService
from ecommerce_agent.approvals.service import ApprovalService
from ecommerce_agent.config import Settings


def invoke(message: str, thread_id: str):
    service = AgentService(Settings(_env_file=None))
    graph = build_multi_agent_graph(service, ApprovalService())
    return asyncio.run(graph.ainvoke({"message": message}, {"configurable": {"thread_id": thread_id}}))


def test_supervisor_routes_commerce_query():
    result = invoke("查询订单", "commerce-thread")
    assert result["route"] == "commerce"
    assert result["result"]["type"] == "commerce"
    assert result["plan"]


def test_supervisor_routes_write_to_safety():
    result = invoke("修改商品 p-100", "safety-thread")
    assert result["route"] == "safety"
    assert result["result"]["status"] == "waiting_approval"


def test_safety_blocks_refund():
    result = invoke("给订单退款", "refund-thread")
    assert result["result"]["status"] == "blocked"
