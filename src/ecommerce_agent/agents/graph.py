from typing import Any, TypedDict
from uuid import uuid4

from ecommerce_agent.agents.service import AgentService
from ecommerce_agent.approvals.service import ApprovalService
from ecommerce_agent.rag.chunker import chunk_markdown
from ecommerce_agent.rag.normalizer import normalize_markdown
from ecommerce_agent.rag.retriever import InMemoryRetriever


class GraphState(TypedDict, total=False):
    message: str
    result: dict[str, Any]


def build_langgraph(service: AgentService) -> Any:
    """构建最小 LangGraph，生产环境可替换为带 Checkpointer 的完整图。"""
    from langgraph.graph import END, START, StateGraph

    graph = StateGraph(GraphState)

    async def run_agent(state: GraphState) -> GraphState:
        return {"result": await service.answer(state["message"])}

    graph.add_node("agent", run_agent)
    graph.add_edge(START, "agent")
    graph.add_edge("agent", END)
    return graph.compile()


class EcommerceAgentGraph:
    """可替换为 LangGraph Checkpointer 的最小状态图实现。"""

    def __init__(self, service: AgentService, approvals: ApprovalService | None = None) -> None:
        self.service = service
        self.approvals = approvals or ApprovalService()
        self.retriever = InMemoryRetriever()

    def ingest(self, source_uri: str, markdown: str) -> int:
        chunks = chunk_markdown(normalize_markdown(markdown), source_uri)
        self.retriever.add(chunks)
        return len(chunks)

    async def run(self, message: str) -> dict[str, Any]:
        run_id = str(uuid4())
        evidence = self.retriever.search(message)
        if evidence:
            return {
                "run_id": run_id,
                "type": "knowledge",
                "answer": "\n\n".join(item.chunk.content for item in evidence),
                "citations": [item.citation for item in evidence],
            }
        result = await self.service.answer(message)
        result["run_id"] = run_id
        return result

    def propose(self, action: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return self.approvals.propose(action, arguments, str(uuid4()))
