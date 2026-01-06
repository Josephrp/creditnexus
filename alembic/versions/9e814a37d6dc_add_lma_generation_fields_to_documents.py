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
    """Add LMA template generation fields to documents table.
    
    Note: The columns is_generated, template_id, and source_cdm_data were already
    created in migration e650a2d25272. This migration only adds the foreign key
    constraint for template_id (since lma_templates table didn't exist then).
    """
    # Add foreign key constraint for template_id (column already exists)
    op.create_foreign_key(
        'fk_documents_template_id',
        'documents',
        'lma_templates',
        ['template_id'],
        ['id'],
        ondelete='SET NULL'
    )
    
    # Create index for template_id (if it doesn't already exist)
    # Note: is_generated index already exists as ix_documents_is_generated
    op.create_index('idx_documents_template_id', 'documents', ['template_id'])


def downgrade() -> None:
    """Remove LMA template generation fields from documents table.
    
    Note: We only drop the foreign key and index added in this migration.
    The columns themselves remain (they were created in e650a2d25272).
    """
    # Drop index
    op.drop_index('idx_documents_template_id', table_name='documents')
    
    # Drop foreign key constraint
    op.drop_constraint('fk_documents_template_id', 'documents', type_='foreignkey')
