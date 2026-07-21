"""增加审批执行结果字段。"""

import sqlalchemy as sa

from alembic import op

revision = "0004_approval_execution"
down_revision = "0003_approval_metadata"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("approvals", sa.Column("execution_result", sa.JSON(), nullable=True))
    op.add_column("approvals", sa.Column("executed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("approvals", "executed_at")
    op.drop_column("approvals", "execution_result")
