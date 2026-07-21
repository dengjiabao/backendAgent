"""知识文件入库任务的独立模式实现。"""

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from ecommerce_agent.rag.chunker import Chunk, chunk_markdown
from ecommerce_agent.rag.markitdown_converter import MarkItDownConverter
from ecommerce_agent.rag.normalizer import normalize_markdown


class MarkdownConverter(Protocol):
    def convert(self, path: str | Path) -> str: ...


@dataclass
class IngestionJob:
    id: str
    source_uri: str
    source_hash: str
    status: str = "queued"
    attempts: int = 0
    error: str | None = None
    chunks: list[Chunk] = field(default_factory=list)


class IngestionJobService:
    """提供可被 Celery 调用的异步任务状态和幂等处理。"""

    def __init__(self, converter: MarkdownConverter | None = None, max_retries: int = 3) -> None:
        self.converter = converter or MarkItDownConverter()
        self.max_retries = max_retries
        self.jobs: dict[str, IngestionJob] = {}
        self._hash_to_job: dict[str, str] = {}

    async def submit(self, path: str | Path) -> str:
        file_path = Path(path)
        source_hash = hashlib.sha256(file_path.read_bytes()).hexdigest()
        existing_id = self._hash_to_job.get(source_hash)
        if existing_id is not None:
            return existing_id
        job = IngestionJob(str(uuid4()), str(file_path), source_hash)
        self.jobs[job.id] = job
        self._hash_to_job[source_hash] = job.id
        return job.id

    async def run(self, job_id: str) -> IngestionJob:
        job = self.jobs[job_id]
        if job.status == "completed":
            return job
        job.status = "running"
        while job.attempts < self.max_retries:
            job.attempts += 1
            try:
                markdown = normalize_markdown(self.converter.convert(job.source_uri))
                job.chunks = chunk_markdown(markdown, job.source_uri)
                job.status = "completed"
                job.error = None
                return job
            except Exception as exc:  # noqa: BLE001
                job.error = str(exc)
        job.status = "failed"
        return job

    async def get(self, job_id: str) -> IngestionJob:
        return self.jobs[job_id]
