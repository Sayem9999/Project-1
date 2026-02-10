"""merge heads

Revision ID: b6b09e2a4f3b
Revises: 9b90d85e04ae, a3c7b2e9f1a4
Create Date: 2026-02-10 11:15:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b6b09e2a4f3b'
down_revision: Union[str, Sequence[str], None] = ('9b90d85e04ae', 'a3c7b2e9f1a4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
