"""add_clause_cache_table

Revision ID: 5d8daddcc33f
Revises: 7f8a9b0c1d2e
Create Date: 2026-01-08 22:28:56.425580

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '5d8daddcc33f'
down_revision: Union[str, Sequence[str], None] = '7f8a9b0c1d2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create clause_cache table for AI-generated clause caching."""
    
    # Check if table already exists (in case it was created manually)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    tables = inspector.get_table_names()
    
    if 'clause_cache' not in tables:
        op.create_table(
            'clause_cache',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('template_id', sa.Integer(), nullable=False),
            sa.Column('field_name', sa.String(length=100), nullable=False),
            sa.Column('clause_content', sa.Text(), nullable=False),
            sa.Column('context_hash', sa.String(length=64), nullable=True),
            sa.Column('context_summary', JSONB(), nullable=True),
            sa.Column('usage_count', sa.Integer(), server_default='0', nullable=False),
            sa.Column('last_used_at', sa.DateTime(), nullable=True),
            sa.Column('created_by', sa.Integer(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['template_id'], ['lma_templates.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
        )
        
        # Create indexes
        op.create_index('ix_clause_cache_template_id', 'clause_cache', ['template_id'])
        op.create_index('ix_clause_cache_field_name', 'clause_cache', ['field_name'])
        op.create_index('ix_clause_cache_context_hash', 'clause_cache', ['context_hash'])
        op.create_index('ix_clause_cache_created_by', 'clause_cache', ['created_by'])
        op.create_index('ix_clause_cache_last_used_at', 'clause_cache', ['last_used_at'])
        
        # Create unique constraint for template+field_name+context_hash combination
        op.create_index('ix_clause_cache_template_field_context', 'clause_cache', ['template_id', 'field_name', 'context_hash'], unique=True)
    else:
        # Table already exists, just ensure indexes exist
        indexes = [idx['name'] for idx in inspector.get_indexes('clause_cache')]
        
        if 'ix_clause_cache_template_id' not in indexes:
            op.create_index('ix_clause_cache_template_id', 'clause_cache', ['template_id'])
        if 'ix_clause_cache_field_name' not in indexes:
            op.create_index('ix_clause_cache_field_name', 'clause_cache', ['field_name'])
        if 'ix_clause_cache_context_hash' not in indexes:
            op.create_index('ix_clause_cache_context_hash', 'clause_cache', ['context_hash'])
        if 'ix_clause_cache_created_by' not in indexes:
            op.create_index('ix_clause_cache_created_by', 'clause_cache', ['created_by'])
        if 'ix_clause_cache_last_used_at' not in indexes:
            op.create_index('ix_clause_cache_last_used_at', 'clause_cache', ['last_used_at'])
        if 'ix_clause_cache_template_field_context' not in indexes:
            op.create_index('ix_clause_cache_template_field_context', 'clause_cache', ['template_id', 'field_name', 'context_hash'], unique=True)


def downgrade() -> None:
    """Drop clause_cache table."""
    op.drop_index('ix_clause_cache_template_field_context', table_name='clause_cache')
    op.drop_index('ix_clause_cache_last_used_at', table_name='clause_cache')
    op.drop_index('ix_clause_cache_created_by', table_name='clause_cache')
    op.drop_index('ix_clause_cache_context_hash', table_name='clause_cache')
    op.drop_index('ix_clause_cache_field_name', table_name='clause_cache')
    op.drop_index('ix_clause_cache_template_id', table_name='clause_cache')
    op.drop_table('clause_cache')
