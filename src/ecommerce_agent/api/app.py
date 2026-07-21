import json
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ecommerce_agent.agents.events import collect_public_events
from ecommerce_agent.agents.graph import EcommerceAgentGraph
from ecommerce_agent.agents.service import AgentService
from ecommerce_agent.api.approvals import router as approvals_router
from ecommerce_agent.approvals.service import ApprovalService
from ecommerce_agent.config import Settings
from ecommerce_agent.persistence.database import create_database_engine, create_session_factory
from ecommerce_agent.persistence.factory import build_state_store
from ecommerce_agent.persistence.knowledge_repository import KnowledgeRepository
from ecommerce_agent.rag.embeddings import build_embedding_provider
from ecommerce_agent.rag.hybrid_retriever import PersistentHybridRetriever


class ChatRequest(BaseModel):
    message: str


class ProposalRequest(BaseModel):
    action: str
    arguments: dict[str, object] = Field(default_factory=dict)


def create_app() -> FastAPI:
    settings = Settings()
    service = AgentService(settings)
    approvals = ApprovalService(build_state_store(settings))
    persistent_retriever = None
    if settings.state_backend == "database":
        engine = create_database_engine(settings.database_url)
        persistent_retriever = PersistentHybridRetriever(KnowledgeRepository(create_session_factory(engine)), build_embedding_provider(settings))
    graph = EcommerceAgentGraph(service, approvals, persistent_retriever)
    app = FastAPI(title="企业级电商后台 Agent", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.agent_service = service
    app.state.approvals = approvals
    app.state.agent_graph = graph
    app.include_router(approvals_router)

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "mode": settings.runtime_mode}

    @app.post("/api/v1/chat")
    async def chat(request: ChatRequest) -> dict[str, object]:
        return await graph.run(request.message)

    @app.post("/api/v1/chat/stream")
    async def chat_stream(request: ChatRequest) -> StreamingResponse:
        result = await graph.run(request.message)

        async def events() -> AsyncIterator[str]:
            for event in await collect_public_events(result):
                yield f"event: {event['type']}\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    @app.post("/api/v1/tools/propose")
    async def propose(request: ProposalRequest) -> dict[str, object]:
        return graph.propose(request.action, request.arguments)

    @app.post("/api/v1/knowledge/markdown")
    async def ingest_markdown(request: Request) -> dict[str, object]:
        raw = await request.body()
        if len(raw) > settings.max_upload_bytes:
            raise HTTPException(status_code=413, detail="文件超过大小限制")
        filename = request.headers.get("x-filename", "upload.md")
        text = raw.decode("utf-8")
        count = await graph.ingest_async(filename, text)
        return {"source_uri": filename, "chunk_count": count}

    return app
