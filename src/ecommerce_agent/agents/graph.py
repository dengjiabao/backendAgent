from typing import Any, TypedDict
from uuid import uuid4

from ecommerce_agent.agents.service import AgentService
from ecommerce_agent.approvals.service import ApprovalService
from ecommerce_agent.rag.chunker import chunk_markdown
from ecommerce_agent.rag.hybrid_retriever import PersistentHybridRetriever
from ecommerce_agent.rag.normalizer import normalize_markdown
from ecommerce_agent.rag.retriever import InMemoryRetriever


class GraphState(TypedDict, total=False):
    message: str
    result: dict[str, Any]


class EnterpriseGraphState(TypedDict, total=False):
    message: str
    route: str
    result: dict[str, Any]


def build_multi_agent_graph(service: AgentService, approvals: ApprovalService) -> Any:
    """Supervisor、Commerce、Knowledge、Safety 四节点状态图。"""
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph import END, START, StateGraph

    graph = StateGraph(EnterpriseGraphState)

    def supervisor(state: EnterpriseGraphState) -> EnterpriseGraphState:
        message = state["message"]
        if any(word in message for word in ("修改", "更新", "发货", "退款", "删除")):
            route = "safety"
        elif any(word in message for word in ("商品", "订单", "库存", "售后")):
            route = "commerce"
        else:
            route = "knowledge"
        return {"route": route}

    async def commerce(state: EnterpriseGraphState) -> EnterpriseGraphState:
        return {"result": await service.answer(state["message"])}

    def knowledge(state: EnterpriseGraphState) -> EnterpriseGraphState:
        return {
            "result": {
                "type": "knowledge",
                "answer": "当前知识库未找到依据，请先上传相关制度或业务文档。",
                "citations": [],
            }
        }

    def safety(state: EnterpriseGraphState) -> EnterpriseGraphState:
        message = state["message"]
        if "退款" in message:
            action = "order.refund"
        elif "删除" in message:
            action = "resource.delete"
        elif "发货" in message:
            action = "order.ship"
        else:
            action = "product.update"
        return {"result": approvals.propose(action, {"request": message}, str(uuid4()))}

    graph.add_node("supervisor", supervisor)
    graph.add_node("commerce", commerce)
    graph.add_node("knowledge", knowledge)
    graph.add_node("safety", safety)
    graph.add_edge(START, "supervisor")
    graph.add_conditional_edges("supervisor", lambda state: state["route"], {"commerce": "commerce", "knowledge": "knowledge", "safety": "safety"})
    graph.add_edge("commerce", END)
    graph.add_edge("knowledge", END)
    graph.add_edge("safety", END)
    return graph.compile(checkpointer=InMemorySaver())


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

    def __init__(
        self,
        service: AgentService,
        approvals: ApprovalService | None = None,
        persistent_retriever: PersistentHybridRetriever | None = None,
    ) -> None:
        self.service = service
        self.approvals = approvals or ApprovalService()
        self.retriever = InMemoryRetriever()
        self.persistent_retriever = persistent_retriever
        self.multi_agent = build_multi_agent_graph(service, self.approvals)

    def ingest(self, source_uri: str, markdown: str) -> int:
        chunks = chunk_markdown(normalize_markdown(markdown), source_uri)
        self.retriever.add(chunks)
        return len(chunks)

    async def ingest_async(self, source_uri: str, markdown: str) -> int:
        count = self.ingest(source_uri, markdown)
        if self.persistent_retriever is not None:
            chunks = chunk_markdown(normalize_markdown(markdown), source_uri)
            await self.persistent_retriever.add_markdown(source_uri, markdown, chunks)
        return count

    async def run(self, message: str) -> dict[str, Any]:
        run_id = str(uuid4())
        if self.persistent_retriever is not None:
            persistent_evidence = await self.persistent_retriever.search(message)
            evidence = [
                type("Evidence", (), {"chunk": type("Chunk", (), {"content": item.content})(), "citation": item.citation})() for item in persistent_evidence
            ]
        else:
            evidence = self.retriever.search(message)
        if evidence:
            return {
                "run_id": run_id,
                "type": "knowledge",
                "answer": "\n\n".join(item.chunk.content for item in evidence),
                "citations": [item.citation for item in evidence],
            }
        state = await self.multi_agent.ainvoke({"message": message}, {"configurable": {"thread_id": run_id}})
        result = dict(state["result"])
        result["run_id"] = run_id
        result["route"] = state["route"]
        return result

    def propose(self, action: str, arguments: dict[str, Any]) -> dict[str, Any]:
        return self.approvals.propose(action, arguments, str(uuid4()))
