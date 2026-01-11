"""add_demo_data_tracking

Revision ID: 1e2d90fbb7c1
Revises: cb70003e8b8c
Create Date: 2026-01-10 22:05:43.789271

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e2d90fbb7c1'
down_revision: Union[str, Sequence[str], None] = 'cb70003e8b8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create demo_seeding_status table
    op.create_table(
        'demo_seeding_status',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('stage', sa.String(50), nullable=False),
        sa.Column('progress', sa.Numeric(precision=5, scale=2), nullable=False, server_default='0.00'),
        sa.Column('total', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('current', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('status', sa.String(20), nullable=False, server_default='pending'),
        sa.Column('errors', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for demo_seeding_status
    op.create_index(op.f('ix_demo_seeding_status_stage'), 'demo_seeding_status', ['stage'], unique=False)
    op.create_index(op.f('ix_demo_seeding_status_status'), 'demo_seeding_status', ['status'], unique=False)
    
    # Add is_demo column to deals table
    op.add_column('deals', sa.Column('is_demo', sa.Boolean(), nullable=True, server_default='false'))
    
    # Add is_demo column to documents table
    op.add_column('documents', sa.Column('is_demo', sa.Boolean(), nullable=True, server_default='false'))
    
    # Create indexes for filtering demo data
    op.create_index(op.f('ix_deals_is_demo'), 'deals', ['is_demo'], unique=False)
    op.create_index(op.f('ix_documents_is_demo'), 'documents', ['is_demo'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index(op.f('ix_documents_is_demo'), table_name='documents')
    op.drop_index(op.f('ix_deals_is_demo'), table_name='deals')
    
    # Drop columns
    op.drop_column('documents', 'is_demo')
    op.drop_column('deals', 'is_demo')
    
    # Drop indexes for demo_seeding_status
    op.drop_index(op.f('ix_demo_seeding_status_status'), table_name='demo_seeding_status')
    op.drop_index(op.f('ix_demo_seeding_status_stage'), table_name='demo_seeding_status')
    
    # Drop demo_seeding_status table
    op.drop_table('demo_seeding_status')
