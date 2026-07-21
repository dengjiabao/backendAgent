import hashlib
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, sessionmaker

from ecommerce_agent.persistence.models import KnowledgeChunkRow, KnowledgeDocumentRow
from ecommerce_agent.rag.chunker import Chunk


class KnowledgeRepository:
    def __init__(self, sessions: sessionmaker[Session]) -> None:
        self.sessions = sessions

    def save_document(self, source_uri: str, markdown: str, chunks: list[Chunk], embeddings: list[list[float]]) -> str:
        source_hash = hashlib.sha256(markdown.encode("utf-8")).hexdigest()
        with self.sessions.begin() as session:
            existing = session.scalar(select(KnowledgeDocumentRow).where(KnowledgeDocumentRow.source_hash == source_hash))
            if existing is not None:
                return existing.id
            document_id = str(uuid4())
            session.add(
                KnowledgeDocumentRow(
                    id=document_id,
                    source_uri=source_uri,
                    source_hash=source_hash,
                    markdown=markdown,
                    status="completed",
                    created_at=datetime.now(UTC),
                )
            )
            for chunk, embedding in zip(chunks, embeddings, strict=True):
                session.add(
                    KnowledgeChunkRow(
                        id=chunk.id,
                        document_id=document_id,
                        source_uri=source_uri,
                        heading_path=chunk.heading_path,
                        content=chunk.content,
                        metadata_json=chunk.metadata or {},
                        embedding=embedding,
                        lexical_weight=1.0,
                    )
                )
        return document_id

    def list_chunks(self) -> list[KnowledgeChunkRow]:
        with self.sessions() as session:
            return list(session.scalars(select(KnowledgeChunkRow)).all())

    def search_lexical(self, query: str, limit: int = 50) -> list[KnowledgeChunkRow]:
        """按数据库方言执行关键词检索，SQLite 用 LIKE 作为独立模式回退。"""

        terms = [term for term in query.split() if term]
        with self.sessions() as session:
            if session.bind is not None and session.bind.dialect.name == "postgresql":
                statement = select(KnowledgeChunkRow).where(KnowledgeChunkRow.content.match(query)).limit(limit)
            else:
                conditions = [KnowledgeChunkRow.content.ilike(f"%{term}%") for term in terms]
                statement = select(KnowledgeChunkRow).where(or_(*conditions)).limit(limit) if conditions else select(KnowledgeChunkRow).limit(limit)
            return list(session.scalars(statement).all())

    def count_documents(self) -> int:
        with self.sessions() as session:
            return len(list(session.scalars(select(KnowledgeDocumentRow.id)).all()))
