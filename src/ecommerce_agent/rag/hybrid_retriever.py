import math
import re
from collections.abc import Sequence
from dataclasses import dataclass

from ecommerce_agent.persistence.knowledge_repository import KnowledgeRepository
from ecommerce_agent.rag.embeddings import EmbeddingProvider


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

    async def search(self, query: str, top_k: int = 5) -> list[HybridResult]:
        query_vector = (await self.embeddings.embed([query]))[0]
        query_tokens = _tokens(query)
        scored: list[HybridResult] = []
        for row in self.repository.list_chunks():
            embedding = list(row.embedding or [])
            vector_score = _cosine(query_vector, embedding) if embedding else 0.0
            terms = _tokens(f"{row.heading_path} {row.content}")
            lexical_score = len(query_tokens & terms) / max(len(query_tokens), 1)
            score = vector_score * 0.65 + lexical_score * 0.35
            if score > 0:
                scored.append(
                    HybridResult(
                        row.id,
                        row.content,
                        row.source_uri,
                        row.heading_path,
                        score,
                        f"[{row.source_uri}#{row.id}]",
                    )
                )
        return sorted(scored, key=lambda item: item.score, reverse=True)[:top_k]
