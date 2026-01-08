"""merge_migration_heads

Revision ID: 5887d0638b42
Revises: 7f8a9b0c1d2e, e6043869162a
Create Date: 2026-01-08 15:55:16.777781

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5887d0638b42'
down_revision: Union[str, Sequence[str], None] = ('7f8a9b0c1d2e', 'e6043869162a')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
