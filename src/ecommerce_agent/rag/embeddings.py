import hashlib
import math
from typing import Protocol

from openai import AsyncOpenAI

from ecommerce_agent.config import Settings


class EmbeddingProvider(Protocol):
    async def embed(self, texts: list[str]) -> list[list[float]]: ...


class HashEmbeddingProvider:
    """无需模型服务的确定性 Embedding，仅用于独立开发、测试和降级。"""

    def __init__(self, dimensions: int = 1536) -> None:
        self.dimensions = dimensions

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        normalized = text.lower().strip()
        tokens = normalized.split() or list(normalized)
        for token in tokens:
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[index] += 1.0 if digest[4] % 2 else -1.0
        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]


class OpenAIEmbeddingProvider:
    def __init__(self, settings: Settings) -> None:
        if settings.model_api_key is None:
            raise ValueError("OpenAI-compatible Embedding 需要 MODEL_API_KEY")
        self.client = AsyncOpenAI(api_key=settings.model_api_key.get_secret_value(), base_url=settings.model_base_url)
        self.model = settings.embedding_model
        self.dimensions = settings.embedding_dimensions

    async def embed(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(model=self.model, input=texts, dimensions=self.dimensions)
        return [item.embedding for item in response.data]


def build_embedding_provider(settings: Settings) -> EmbeddingProvider:
    if settings.embedding_provider == "hash":
        return HashEmbeddingProvider(settings.embedding_dimensions)
    return OpenAIEmbeddingProvider(settings)
