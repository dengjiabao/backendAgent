import asyncio
from pathlib import Path

from ecommerce_agent.persistence.database import create_database_engine, create_session_factory, initialize_database
from ecommerce_agent.persistence.knowledge_repository import KnowledgeRepository
from ecommerce_agent.rag.chunker import chunk_markdown
from ecommerce_agent.rag.embeddings import HashEmbeddingProvider
from ecommerce_agent.rag.hybrid_retriever import PersistentHybridRetriever


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
