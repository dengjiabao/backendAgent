import re
from collections.abc import Callable
from dataclasses import dataclass

from ecommerce_agent.rag.chunker import Chunk


@dataclass(frozen=True)
class Retrieval:
    chunk: Chunk
    score: float
    citation: str


@dataclass(frozen=True)
class AccessScope:
    """检索权限范围，避免检索层依赖具体身份系统。"""

    tenant_id: str | None = None
    allowed_sources: set[str] | None = None


def _terms(text: str) -> set[str]:
    words = set(re.findall(r"[A-Za-z0-9_:.\-/]+|[\u4e00-\u9fff]", text.lower()))
    return words


class InMemoryRetriever:
    """独立模式的轻量检索器，后续可替换为 pgvector + 全文检索。"""

    def __init__(self) -> None:
        self._chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        self._chunks.extend(chunks)

    def search(self, query: str, top_k: int = 5) -> list[Retrieval]:
        query_terms = _terms(query)
        scored: list[tuple[float, Chunk]] = []
        for chunk in self._chunks:
            content_terms = _terms(chunk.content + " " + chunk.heading_path)
            overlap = len(query_terms & content_terms)
            if overlap:
                scored.append((overlap / max(len(query_terms), 1), chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [Retrieval(c, score, f"[{c.source_uri}#{c.id}] ") for score, c in scored[:top_k]]


class RRFHybridRetriever(InMemoryRetriever):
    """对关键词和语义候选按 Reciprocal Rank Fusion 合并。"""

    def __init__(self, semantic_ranker: Callable[[str, list[Chunk]], list[Chunk]] | None = None) -> None:
        super().__init__()
        self.semantic_ranker = semantic_ranker

    @staticmethod
    def _visible(chunk: Chunk, scope: AccessScope) -> bool:
        if scope.allowed_sources is not None and chunk.source_uri not in scope.allowed_sources:
            return False
        if scope.tenant_id is None:
            return True
        metadata_tenant = (chunk.metadata or {}).get("tenant_id")
        return metadata_tenant == scope.tenant_id or chunk.source_uri.startswith(f"{scope.tenant_id}/")

    def search(self, query: str, top_k: int = 5, scope: AccessScope | None = None) -> list[Retrieval]:
        access_scope = scope or AccessScope()
        candidates = [chunk for chunk in self._chunks if self._visible(chunk, access_scope)]
        lexical = self._lexical_rank(query, candidates)
        semantic_chunks = self.semantic_ranker(query, candidates) if self.semantic_ranker else [item[1] for item in lexical]
        semantic = {chunk.id: rank for rank, chunk in enumerate(semantic_chunks, start=1)}
        scores: dict[str, float] = {}
        by_id = {chunk.id: chunk for chunk in candidates}
        for rank, (_, chunk) in enumerate(lexical, start=1):
            scores[chunk.id] = scores.get(chunk.id, 0.0) + 1 / (60 + rank)
        for chunk_id, rank in semantic.items():
            scores[chunk_id] = scores.get(chunk_id, 0.0) + 1 / (60 + rank)
        ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)[:top_k]
        return [Retrieval(by_id[chunk_id], score, f"[{by_id[chunk_id].source_uri}#{chunk_id}]") for chunk_id, score in ordered]

    @staticmethod
    def _lexical_rank(query: str, candidates: list[Chunk]) -> list[tuple[float, Chunk]]:
        query_terms = _terms(query)
        scored = []
        for chunk in candidates:
            overlap = len(query_terms & _terms(f"{chunk.heading_path} {chunk.content}"))
            if overlap:
                scored.append((overlap / max(len(query_terms), 1), chunk))
        return sorted(scored, key=lambda item: item[0], reverse=True)
