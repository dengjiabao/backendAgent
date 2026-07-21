"""增加可恢复运行检查点。"""

import sqlalchemy as sa

from alembic import op

revision = "0005_run_checkpoints"
down_revision = "0004_approval_execution"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "run_checkpoints",
        sa.Column("thread_id", sa.String(length=128), primary_key=True),
        sa.Column("state", sa.JSON(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("run_checkpoints")
