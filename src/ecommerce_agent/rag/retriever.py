import re
from dataclasses import dataclass

from ecommerce_agent.rag.chunker import Chunk


@dataclass(frozen=True)
class Retrieval:
    chunk: Chunk
    score: float
    citation: str


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
