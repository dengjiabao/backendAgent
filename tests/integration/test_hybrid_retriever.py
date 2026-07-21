import asyncio
from dataclasses import replace
from pathlib import Path

from ecommerce_agent.persistence.database import create_database_engine, create_session_factory, initialize_database
from ecommerce_agent.persistence.knowledge_repository import KnowledgeRepository
from ecommerce_agent.rag.chunker import chunk_markdown
from ecommerce_agent.rag.embeddings import HashEmbeddingProvider
from ecommerce_agent.rag.hybrid_retriever import PersistentHybridRetriever
from ecommerce_agent.rag.retriever import AccessScope


def test_persistent_hybrid_retriever_is_idempotent_and_cites_source(tmp_path: Path):
    engine = create_database_engine(f"sqlite+pysqlite:///{tmp_path / 'rag.db'}")
    initialize_database(engine)
    repository = KnowledgeRepository(create_session_factory(engine))
    retriever = PersistentHybridRetriever(repository, HashEmbeddingProvider(1536))
    markdown = "# 订单权限\n\nadmin:order:list 用于查询订单"
    chunks = chunk_markdown(markdown, "permissions.md")

    first_id = asyncio.run(retriever.add_markdown("permissions.md", markdown, chunks))
    second_id = asyncio.run(retriever.add_markdown("permissions.md", markdown, chunks))
    result = asyncio.run(retriever.search("admin:order:list"))

    assert first_id == second_id
    assert repository.count_documents() == 1
    assert result and "permissions.md" in result[0].citation


def test_persistent_retriever_filters_scope_and_uses_rrf(tmp_path: Path):
    engine = create_database_engine(f"sqlite+pysqlite:///{tmp_path / 'scope.db'}")
    initialize_database(engine)
    repository = KnowledgeRepository(create_session_factory(engine))
    retriever = PersistentHybridRetriever(repository, HashEmbeddingProvider(1536))
    allowed = chunk_markdown("# 权限\n\nadmin:order:list", "tenant-a/api.md")[0]
    allowed = replace(allowed, metadata={"tenant_id": "tenant-a"})
    denied = chunk_markdown("# 权限\n\nadmin:order:list", "tenant-b/api.md")[0]
    denied = replace(denied, metadata={"tenant_id": "tenant-b"})
    asyncio.run(retriever.add_markdown("tenant-a/api.md", "# 权限\n\nadmin:order:list", [allowed]))
    asyncio.run(retriever.add_markdown("tenant-b/api.md", "# 权限\n\nadmin:order:list-2", [denied]))

    result = asyncio.run(
        retriever.search("admin:order:list", scope=AccessScope(tenant_id="tenant-a"))
    )

    assert result and result[0].source_uri == "tenant-a/api.md"
