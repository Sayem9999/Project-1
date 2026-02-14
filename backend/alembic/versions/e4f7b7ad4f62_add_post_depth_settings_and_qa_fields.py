"""add post depth settings and qa fields

Revision ID: e4f7b7ad4f62
Revises: 82ef48fc3c57
Create Date: 2026-02-15 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e4f7b7ad4f62"
down_revision: Union[str, Sequence[str], None] = "82ef48fc3c57"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("jobs", sa.Column("post_settings", sa.JSON(), nullable=True))
    op.add_column("jobs", sa.Column("audio_qa", sa.JSON(), nullable=True))
    op.add_column("jobs", sa.Column("color_qa", sa.JSON(), nullable=True))
    op.add_column("jobs", sa.Column("subtitle_qa", sa.JSON(), nullable=True))


def downgrade() -> None:
    op.drop_column("jobs", "subtitle_qa")
    op.drop_column("jobs", "color_qa")
    op.drop_column("jobs", "audio_qa")
    op.drop_column("jobs", "post_settings")
