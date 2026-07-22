import json
from collections.abc import AsyncIterator
from datetime import timedelta

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ecommerce_agent.agents.checkpoint import DatabaseRunCheckpoint
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
from ecommerce_agent.security.auth import LocalJWTService


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ProposalRequest(BaseModel):
    action: str
    arguments: dict[str, object] = Field(default_factory=dict)


class ResumeRequest(BaseModel):
    conversation_id: str
    patch: dict[str, object] = Field(default_factory=dict)


class AuthTokenRequest(BaseModel):
    subject: str
    tenant_id: str
    roles: set[str] = Field(default_factory=set)


def create_app() -> FastAPI:
    settings = Settings()
    service = AgentService(settings)
    approvals = ApprovalService(build_state_store(settings))
    persistent_retriever = None
    checkpoint = None
    if settings.state_backend == "database":
        engine = create_database_engine(settings.database_url)
        sessions = create_session_factory(engine)
        persistent_retriever = PersistentHybridRetriever(KnowledgeRepository(sessions), build_embedding_provider(settings))
        checkpoint = DatabaseRunCheckpoint(sessions)
    graph = EcommerceAgentGraph(service, approvals, persistent_retriever, checkpoint)
    jwt_service = LocalJWTService(settings.jwt_secret.get_secret_value())
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

    @app.post("/api/v1/auth/token")
    async def issue_token(request: AuthTokenRequest) -> dict[str, str]:
        token = jwt_service.issue(request.subject, request.tenant_id, request.roles, timedelta(hours=1))
        return {"access_token": token, "token_type": "bearer"}

    @app.get("/api/v1/auth/me")
    async def current_identity(request: Request) -> dict[str, object]:
        authorization = request.headers.get("authorization", "")
        if not authorization.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="缺少 Bearer Token")
        try:
            identity = jwt_service.verify(authorization[7:])
        except ValueError as exc:
            raise HTTPException(status_code=401, detail=str(exc)) from exc
        return {"subject": identity.subject, "tenant_id": identity.tenant_id, "roles": sorted(identity.roles)}

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "mode": settings.runtime_mode}

    @app.post("/api/v1/chat")
    async def chat(request: ChatRequest) -> dict[str, object]:
        return await graph.run(request.message, request.conversation_id)

    @app.post("/api/v1/chat/stream")
    async def chat_stream(request: ChatRequest) -> StreamingResponse:
        result = await graph.run(request.message, request.conversation_id)

        async def events() -> AsyncIterator[str]:
            for event in await collect_public_events(result):
                yield f"event: {event['type']}\ndata: {json.dumps(event, ensure_ascii=False)}\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    @app.post("/api/v1/chat/resume")
    async def resume_chat(request: ResumeRequest) -> dict[str, object]:
        try:
            return await graph.resume(request.conversation_id, request.patch)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail="会话检查点不存在") from exc

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
