"""为知识 Chunk 增加向量和检索权重。"""

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector

from alembic import op

revision: str = "0002_vector_search"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    dialect = op.get_bind().dialect.name
    embedding_type = Vector(1536) if dialect == "postgresql" else sa.JSON()
    op.add_column("knowledge_chunks", sa.Column("embedding", embedding_type, nullable=True))
    op.add_column("knowledge_chunks", sa.Column("lexical_weight", sa.Float(), nullable=False, server_default="1.0"))
    if dialect == "postgresql":
        op.create_index(
            "ix_knowledge_chunks_embedding_hnsw",
            "knowledge_chunks",
            ["embedding"],
            postgresql_using="hnsw",
            postgresql_ops={"embedding": "vector_cosine_ops"},
        )


def downgrade() -> None:
    if op.get_bind().dialect.name == "postgresql":
        op.drop_index("ix_knowledge_chunks_embedding_hnsw", table_name="knowledge_chunks")
    op.drop_column("knowledge_chunks", "lexical_weight")
    op.drop_column("knowledge_chunks", "embedding")
