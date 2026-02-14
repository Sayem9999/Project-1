"""add admin action logs

Revision ID: 7c1d2e8f4a91
Revises: e4f7b7ad4f62
Create Date: 2026-02-15 01:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7c1d2e8f4a91"
down_revision: Union[str, Sequence[str], None] = "e4f7b7ad4f62"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "admin_action_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("admin_user_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=100), nullable=False),
        sa.Column("target_type", sa.String(length=50), nullable=False),
        sa.Column("target_id", sa.String(length=100), nullable=True),
        sa.Column("details", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["admin_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_action_logs_action"), "admin_action_logs", ["action"], unique=False)
    op.create_index(op.f("ix_admin_action_logs_admin_user_id"), "admin_action_logs", ["admin_user_id"], unique=False)
    op.create_index(op.f("ix_admin_action_logs_created_at"), "admin_action_logs", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_admin_action_logs_created_at"), table_name="admin_action_logs")
    op.drop_index(op.f("ix_admin_action_logs_admin_user_id"), table_name="admin_action_logs")
    op.drop_index(op.f("ix_admin_action_logs_action"), table_name="admin_action_logs")
    op.drop_table("admin_action_logs")
