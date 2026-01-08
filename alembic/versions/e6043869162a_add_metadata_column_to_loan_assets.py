"""add_metadata_column_to_loan_assets

Revision ID: e6043869162a
Revises: 9e814a37d6dc
Create Date: 2026-01-07 00:31:59.003503

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'e6043869162a'
down_revision: Union[str, Sequence[str], None] = '9e814a37d6dc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add metadata column to loan_assets table for storing additional asset metadata."""
    op.add_column('loan_assets', sa.Column('metadata', JSONB(), nullable=True))


def downgrade() -> None:
    """Remove metadata column from loan_assets table."""
    op.drop_column('loan_assets', 'metadata')
