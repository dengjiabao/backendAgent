from ecommerce_agent.rag.chunker import chunk_markdown
from ecommerce_agent.rag.retriever import AccessScope, InMemoryRetriever, RRFHybridRetriever


def test_retriever_returns_source_citation():
    retriever = InMemoryRetriever()
    retriever.add(chunk_markdown("# 权限\n\nadmin:order:list 可以查询订单", "policy.md"))
    result = retriever.search("admin:order:list")
    assert result
    assert "policy.md" in result[0].citation


def test_rrf_retriever_filters_tenant_and_source_before_fusion():
    allowed = chunk_markdown("# 制度\n\n中文制度说明", "tenant-a/policy.md")[0]
    exact = chunk_markdown("# 权限\n\nadmin:order:list", "tenant-a/api.java")[0]
    forbidden = chunk_markdown("# 制度\n\n中文制度说明", "tenant-b/policy.md")[0]
    chunks = [allowed, exact, forbidden]
    retriever = RRFHybridRetriever()
    retriever.add(chunks)

    result = retriever.search(
        "admin:order:list",
        scope=AccessScope(tenant_id="tenant-a", allowed_sources={"tenant-a/api.java"}),
    )

    assert [item.chunk.source_uri for item in result] == ["tenant-a/api.java"]


def test_rrf_retriever_combines_exact_and_semantic_rankings():
    exact = chunk_markdown("# API\n\nadmin:order:list", "api.java")[0]
    semantic = chunk_markdown("# 制度\n\n订单查询权限说明", "policy.md")[0]
    retriever = RRFHybridRetriever()
    retriever.add([exact, semantic])
    result = retriever.search("订单查询权限 admin:order:list")

    assert len(result) == 2
    assert all(item.citation.startswith("[") for item in result)
