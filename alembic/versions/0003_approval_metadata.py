"""增加审批幂等和超时字段。"""

import sqlalchemy as sa

from alembic import op

revision = "0003_approval_metadata"
down_revision = "0002_vector_search"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("approvals", sa.Column("idempotency_key", sa.String(length=128), nullable=True))
    op.add_column("approvals", sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("approvals", sa.Column("edited_at", sa.DateTime(timezone=True), nullable=True))
    op.create_index("uq_approvals_idempotency_key", "approvals", ["idempotency_key"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_approvals_idempotency_key", table_name="approvals")
    op.drop_column("approvals", "edited_at")
    op.drop_column("approvals", "expires_at")
    op.drop_column("approvals", "idempotency_key")
