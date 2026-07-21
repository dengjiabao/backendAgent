from collections.abc import Sequence
from typing import Protocol

from ecommerce_agent.rag.retriever import AccessScope


class RerankerPort(Protocol):
    def rerank(self, query: str, results: Sequence[object], scope: AccessScope | None = None) -> list[object]: ...


class KeywordReranker:
    """离线可用的确定性重排器，生产环境可替换为模型服务。"""

    def rerank(self, query: str, results: Sequence[object], scope: AccessScope | None = None) -> list[object]:
        del scope
        terms = set(query.lower().split())
        return sorted(
            results,
            key=lambda item: len(terms.intersection(set(str(getattr(item, "content", "")).lower().split()))),
            reverse=True,
        )
