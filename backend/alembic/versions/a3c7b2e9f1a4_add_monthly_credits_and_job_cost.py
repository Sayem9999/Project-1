"""add monthly credits and job cost tracking

Revision ID: a3c7b2e9f1a4
Revises: f89cfc8f9762
Create Date: 2026-02-10 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a3c7b2e9f1a4'
down_revision: Union[str, Sequence[str], None] = 'f89cfc8f9762'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('monthly_credits', sa.Integer(), server_default='10', nullable=False))
    op.add_column('users', sa.Column('last_credit_reset', sa.Date(), nullable=True))
    op.add_column('jobs', sa.Column('tier', sa.String(length=50), server_default='standard', nullable=False))
    op.add_column('jobs', sa.Column('credits_cost', sa.Integer(), server_default='1', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('jobs', 'credits_cost')
    op.drop_column('jobs', 'tier')
    op.drop_column('users', 'last_credit_reset')
    op.drop_column('users', 'monthly_credits')
