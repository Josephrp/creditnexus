"""merge clause cache with existing heads

Revision ID: dcf895ebe666
Revises: 5887d0638b42, 5d8daddcc33f
Create Date: 2026-01-08 22:58:40.310841

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dcf895ebe666'
down_revision: Union[str, Sequence[str], None] = ('5887d0638b42', '5d8daddcc33f')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
