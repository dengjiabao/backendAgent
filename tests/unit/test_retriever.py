from ecommerce_agent.rag.chunker import chunk_markdown
from ecommerce_agent.rag.retriever import InMemoryRetriever


def test_retriever_returns_source_citation():
    retriever = InMemoryRetriever()
    retriever.add(chunk_markdown("# 权限\n\nadmin:order:list 可以查询订单", "policy.md"))
    result = retriever.search("admin:order:list")
    assert result
    assert "policy.md" in result[0].citation
