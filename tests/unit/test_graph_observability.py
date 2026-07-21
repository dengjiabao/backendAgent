import asyncio

from ecommerce_agent.agents.graph import EcommerceAgentGraph
from ecommerce_agent.agents.service import AgentService
from ecommerce_agent.config import Settings
from ecommerce_agent.observability.otel import InMemoryTracer, MetricsRegistry


def test_graph_records_run_span_and_metric():
    tracer = InMemoryTracer()
    metrics = MetricsRegistry()
    graph = EcommerceAgentGraph(AgentService(Settings(_env_file=None)), tracer=tracer, metrics=metrics)
    asyncio.run(graph.run("查询订单"))
    assert tracer.spans[0].name == "agent.run"
    assert metrics.snapshot()["agent_runs"] == 1.0
