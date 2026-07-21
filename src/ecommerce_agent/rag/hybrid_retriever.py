import math
import re
from collections.abc import Sequence
from dataclasses import dataclass

from ecommerce_agent.persistence.knowledge_repository import KnowledgeRepository
from ecommerce_agent.persistence.models import KnowledgeChunkRow
from ecommerce_agent.rag.embeddings import EmbeddingProvider
from ecommerce_agent.rag.retriever import AccessScope


@dataclass(frozen=True)
class HybridResult:
    chunk_id: str
    content: str
    source_uri: str
    heading_path: str
    score: float
    citation: str


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[A-Za-z0-9_:.\-/]+|[\u4e00-\u9fff]", text.lower()))


def _cosine(left: list[float], right: list[float]) -> float:
    numerator = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    return numerator / (left_norm * right_norm) if left_norm and right_norm else 0.0


class PersistentHybridRetriever:
    def __init__(self, repository: KnowledgeRepository, embeddings: EmbeddingProvider) -> None:
        self.repository = repository
        self.embeddings = embeddings

    async def add_markdown(self, source_uri: str, markdown: str, chunks: Sequence[object]) -> str:
        from ecommerce_agent.rag.chunker import Chunk

        typed_chunks = [chunk for chunk in chunks if isinstance(chunk, Chunk)]
        vectors = await self.embeddings.embed([chunk.content for chunk in typed_chunks])
        return self.repository.save_document(source_uri, markdown, typed_chunks, vectors)

    async def search(
        self, query: str, top_k: int = 5, scope: AccessScope | None = None
    ) -> list[HybridResult]:
        query_vector = (await self.embeddings.embed([query]))[0]
        query_tokens = _tokens(query)
        rows = [row for row in self.repository.list_chunks() if self._visible(row.source_uri, row.metadata_json, scope)]
        vector_ranked: list[tuple[float, KnowledgeChunkRow]] = []
        lexical_ranked: list[tuple[float, KnowledgeChunkRow]] = []
        for row in rows:
            embedding = list(row.embedding or [])
            vector_score = _cosine(query_vector, embedding) if embedding else 0.0
            terms = _tokens(f"{row.heading_path} {row.content}")
            lexical_score = len(query_tokens & terms) / max(len(query_tokens), 1)
            if vector_score > 0:
                vector_ranked.append((vector_score, row))
            if lexical_score > 0:
                lexical_ranked.append((lexical_score, row))
        vector_ranked.sort(key=lambda item: item[0], reverse=True)
        lexical_ranked.sort(key=lambda item: item[0], reverse=True)
        scores: dict[str, float] = {}
        by_id: dict[str, KnowledgeChunkRow] = {row.id: row for row in rows}
        for rank, (_, row) in enumerate(vector_ranked, start=1):
            scores[row.id] = scores.get(row.id, 0.0) + 1 / (60 + rank)
        for rank, (_, row) in enumerate(lexical_ranked, start=1):
            scores[row.id] = scores.get(row.id, 0.0) + 1 / (60 + rank)
        return [
            HybridResult(
                by_id[row_id].id,
                by_id[row_id].content,
                by_id[row_id].source_uri,
                by_id[row_id].heading_path,
                score,
                f"[{by_id[row_id].source_uri}#{row_id}]",
            )
            for row_id, score in sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
        ]

    @staticmethod
    def _visible(source_uri: str, metadata: dict[str, object] | None, scope: AccessScope | None) -> bool:
        if scope is None:
            return True
        if scope.allowed_sources is not None and source_uri not in scope.allowed_sources:
            return False
        if scope.tenant_id is None:
            return True
        return (metadata or {}).get("tenant_id") == scope.tenant_id or source_uri.startswith(f"{scope.tenant_id}/")
