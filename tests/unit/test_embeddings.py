import asyncio
import math

from ecommerce_agent.rag.embeddings import HashEmbeddingProvider


def test_hash_embeddings_are_deterministic_and_normalized():
    provider = HashEmbeddingProvider(dimensions=16)
    first, second = asyncio.run(provider.embed(["订单 权限", "订单 权限"]))
    assert first == second
    assert math.isclose(math.sqrt(sum(value * value for value in first)), 1.0)
