"""add_updated_at_to_document_signatures

Revision ID: 6f85cf4fc118
Revises: 5e27a119a69e
Create Date: 2026-01-13 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6f85cf4fc118'
down_revision: Union[str, Sequence[str], None] = '5e27a119a69e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add updated_at column to document_signatures table."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    if 'document_signatures' not in existing_tables:
        return
    
    # Get existing columns
    existing_columns = [col['name'] for col in inspector.get_columns('document_signatures')]
    
    # Add updated_at if it doesn't exist
    if 'updated_at' not in existing_columns:
        op.add_column('document_signatures', 
            sa.Column('updated_at', sa.DateTime(), nullable=False, 
                     server_default=sa.text('now()'), onupdate=sa.text('now()')))


def downgrade() -> None:
    """Remove updated_at column from document_signatures table."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    if 'document_signatures' not in existing_tables:
        return
    
    # Get existing columns
    existing_columns = [col['name'] for col in inspector.get_columns('document_signatures')]
    
    # Drop updated_at if it exists
    if 'updated_at' in existing_columns:
        op.drop_column('document_signatures', 'updated_at')
