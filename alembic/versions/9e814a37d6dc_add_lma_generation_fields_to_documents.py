"""add_lma_generation_fields_to_documents

Revision ID: 9e814a37d6dc
Revises: 6d7e8f9a0b1c
Create Date: 2026-01-05 23:14:48.441268

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '9e814a37d6dc'
down_revision: Union[str, Sequence[str], None] = '6d7e8f9a0b1c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add LMA template generation fields to documents table."""
    # Add is_generated column
    op.add_column('documents', sa.Column('is_generated', sa.Boolean(), nullable=False, server_default='false'))
    
    # Add template_id column with foreign key
    op.add_column('documents', sa.Column('template_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_documents_template_id',
        'documents',
        'lma_templates',
        ['template_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Add source_cdm_data column
    op.add_column('documents', sa.Column('source_cdm_data', JSONB(), nullable=True))
    
    # Create indexes
    op.create_index('idx_documents_is_generated', 'documents', ['is_generated'])
    op.create_index('idx_documents_template_id', 'documents', ['template_id'])


def downgrade() -> None:
    """Remove LMA template generation fields from documents table."""
    # Drop indexes
    op.drop_index('idx_documents_template_id', table_name='documents')
    op.drop_index('idx_documents_is_generated', table_name='documents')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_documents_template_id', 'documents', type_='foreignkey')
    
    # Drop columns
    op.drop_column('documents', 'source_cdm_data')
    op.drop_column('documents', 'template_id')
    op.drop_column('documents', 'is_generated')
