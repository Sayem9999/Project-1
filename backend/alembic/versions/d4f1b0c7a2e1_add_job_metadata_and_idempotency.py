"""add job metadata and idempotency

Revision ID: d4f1b0c7a2e1
Revises: c2d1a4b5e6f7
Create Date: 2026-02-10 12:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4f1b0c7a2e1"
down_revision: Union[str, Sequence[str], None] = "c2d1a4b5e6f7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("jobs", sa.Column("idempotency_key", sa.String(length=64), nullable=True))
    op.add_column("jobs", sa.Column("pacing", sa.String(length=50), server_default="medium", nullable=False))
    op.add_column("jobs", sa.Column("mood", sa.String(length=50), server_default="professional", nullable=False))
    op.add_column("jobs", sa.Column("ratio", sa.String(length=20), server_default="16:9", nullable=False))
    op.add_column("jobs", sa.Column("platform", sa.String(length=50), server_default="youtube", nullable=False))
    op.add_column("jobs", sa.Column("brand_safety", sa.String(length=50), server_default="standard", nullable=False))
    op.add_column("jobs", sa.Column("cancel_requested", sa.Boolean(), server_default=sa.text("false"), nullable=False))
    op.create_index("ix_jobs_user_idempotency", "jobs", ["user_id", "idempotency_key"], unique=True)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index("ix_jobs_user_idempotency", table_name="jobs")
    op.drop_column("jobs", "cancel_requested")
    op.drop_column("jobs", "brand_safety")
    op.drop_column("jobs", "platform")
    op.drop_column("jobs", "ratio")
    op.drop_column("jobs", "mood")
    op.drop_column("jobs", "pacing")
    op.drop_column("jobs", "idempotency_key")
