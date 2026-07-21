import json
from collections.abc import AsyncIterator

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from ecommerce_agent.agents.graph import EcommerceAgentGraph
from ecommerce_agent.agents.service import AgentService
from ecommerce_agent.api.approvals import router as approvals_router
from ecommerce_agent.approvals.service import ApprovalService
from ecommerce_agent.config import Settings
from ecommerce_agent.persistence.factory import build_state_store


class ChatRequest(BaseModel):
    message: str


class ProposalRequest(BaseModel):
    action: str
    arguments: dict[str, object] = Field(default_factory=dict)


def create_app() -> FastAPI:
    settings = Settings()
    service = AgentService(settings)
    approvals = ApprovalService(build_state_store(settings))
    graph = EcommerceAgentGraph(service, approvals)
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
            yield f"event: run_started\ndata: {json.dumps({'run_id': result['run_id']}, ensure_ascii=False)}\n\n"
            yield f"event: final\ndata: {json.dumps(result, ensure_ascii=False)}\n\n"

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
        count = graph.ingest(filename, text)
        return {"source_uri": filename, "chunk_count": count}

    return app
