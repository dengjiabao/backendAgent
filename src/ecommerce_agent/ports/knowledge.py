from collections.abc import Sequence
from typing import Any, Protocol


class KnowledgeSourcePort(Protocol):
    async def ingest(self, path: str) -> str: ...
    async def search(self, query: str, top_k: int = 5) -> list[dict[str, object]]: ...


class KnowledgeDocumentStorePort(Protocol):
    """保存转换结果的端口，具体实现可使用 SQLite、PostgreSQL 或对象存储。"""

    def save(
        self,
        source_uri: str,
        source_hash: str,
        markdown: str,
        chunks: Sequence[Any],
        embeddings: Sequence[Sequence[float]],
    ) -> str: ...


class EmbeddingPort(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class ObjectStorePort(Protocol):
    """保存原始文件和 Markdown 快照的对象存储端口。"""

    def put(self, key: str, content: bytes) -> str: ...
    def get(self, uri: str) -> bytes: ...
