from uuid import uuid4

from ecommerce_agent.adapters.registry import build_adapter
from ecommerce_agent.config import Settings
from ecommerce_agent.domain.risk import RiskPolicy, RiskLevel
from ecommerce_agent.rag.chunker import chunk_markdown
from ecommerce_agent.rag.normalizer import normalize_markdown


class AgentService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.commerce = build_adapter(settings)
        self.risk = RiskPolicy()
        self.documents: dict[str, list[object]] = {}

    async def answer(self, message: str) -> dict[str, object]:
        run_id = str(uuid4())
        lower = message.lower()
        if "商品" in message or "product" in lower:
            products = await self.commerce.search_products(message.replace("商品", "").strip())
            return {"run_id": run_id, "type": "commerce", "data": [p.model_dump(mode="json") for p in products], "source": "mock"}
        if "订单" in message or "order" in lower:
            orders = await self.commerce.list_orders()
            return {"run_id": run_id, "type": "commerce", "data": [o.model_dump(mode="json") for o in orders], "source": "mock"}
        return {"run_id": run_id, "type": "knowledge", "answer": "当前知识库尚未找到与该问题匹配的依据。", "citations": []}

    def propose(self, action: str, arguments: dict[str, object]) -> dict[str, object]:
        risk = self.risk.classify(action)
        proposal = {"run_id": str(uuid4()), "action": action, "arguments": arguments, "risk": risk.value}
        if risk is RiskLevel.FORBIDDEN:
            proposal["status"] = "blocked"
        elif risk is RiskLevel.WRITE_CONFIRM:
            proposal["status"] = "waiting_approval"
        else:
            proposal["status"] = "executing"
        return proposal

    def ingest_markdown(self, source_uri: str, text: str) -> list[dict[str, str]]:
        chunks = chunk_markdown(normalize_markdown(text), source_uri)
        self.documents[source_uri] = chunks
        return [{"id": c.id, "heading_path": c.heading_path, "source_uri": c.source_uri, "content": c.content} for c in chunks]
