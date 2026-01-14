"""add_document_type_source_type_to_generated_documents

Revision ID: efa5b2aec0c6
Revises: d9300e06ed44
Create Date: 2026-01-14 03:25:15.048493

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'efa5b2aec0c6'
down_revision: Union[str, Sequence[str], None] = 'd9300e06ed44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add document_type and source_type columns to generated_documents table."""
    op.add_column('generated_documents', sa.Column('document_type', sa.String(length=100), nullable=True))
    op.add_column('generated_documents', sa.Column('source_type', sa.String(length=100), nullable=True))


def downgrade() -> None:
    """Remove document_type and source_type columns from generated_documents table."""
    op.drop_column('generated_documents', 'source_type')
    op.drop_column('generated_documents', 'document_type')
