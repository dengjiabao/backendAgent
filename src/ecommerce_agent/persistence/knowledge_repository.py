import hashlib
from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import select
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

    def count_documents(self) -> int:
        with self.sessions() as session:
            return len(list(session.scalars(select(KnowledgeDocumentRow.id)).all()))
