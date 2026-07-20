from collections.abc import AsyncIterator
import json

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ecommerce_agent.agents.service import AgentService
from ecommerce_agent.config import Settings


class ChatRequest(BaseModel):
    message: str


class ProposalRequest(BaseModel):
    action: str
    arguments: dict[str, object] = Field(default_factory=dict)


def create_app() -> FastAPI:
    settings = Settings()
    service = AgentService(settings)
    app = FastAPI(title="企业级电商后台 Agent", version="0.1.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.state.agent_service = service

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "mode": settings.runtime_mode}

    @app.post("/api/v1/chat")
    async def chat(request: ChatRequest) -> dict[str, object]:
        return await service.answer(request.message)

    @app.post("/api/v1/chat/stream")
    async def chat_stream(request: ChatRequest) -> StreamingResponse:
        result = await service.answer(request.message)

        async def events() -> AsyncIterator[str]:
            yield f"event: run_started\ndata: {json.dumps({'run_id': result['run_id']}, ensure_ascii=False)}\n\n"
            yield f"event: final\ndata: {json.dumps(result, ensure_ascii=False)}\n\n"

        return StreamingResponse(events(), media_type="text/event-stream")

    @app.post("/api/v1/tools/propose")
    async def propose(request: ProposalRequest) -> dict[str, object]:
        return service.propose(request.action, request.arguments)

    @app.post("/api/v1/knowledge/markdown")
    async def ingest_markdown(request: Request) -> dict[str, object]:
        raw = await request.body()
        if len(raw) > settings.max_upload_bytes:
            raise HTTPException(status_code=413, detail="文件超过大小限制")
        filename = request.headers.get("x-filename", "upload.md")
        chunks = service.ingest_markdown(filename, raw.decode("utf-8"))
        return {"source_uri": filename, "chunks": chunks}

    return app
