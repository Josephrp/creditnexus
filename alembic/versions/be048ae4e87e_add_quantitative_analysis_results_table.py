"""add_quantitative_analysis_results_table

Revision ID: be048ae4e87e
Revises: 36f2a45609b9
Create Date: 2026-01-14 13:01:52.199005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'be048ae4e87e'
down_revision: Union[str, Sequence[str], None] = '36f2a45609b9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create quantitative_analysis_results table (with IF NOT EXISTS check)
    from sqlalchemy import inspect
    conn = op.get_bind()
    inspector = inspect(conn)
    existing_tables = inspector.get_table_names()
    
    if 'quantitative_analysis_results' not in existing_tables:
        op.create_table(
            'quantitative_analysis_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('analysis_id', sa.String(length=36), nullable=False),
        sa.Column('analysis_type', sa.String(length=50), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('report', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('market_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('fundamental_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('deal_id', sa.Integer(), nullable=True),
        sa.Column('workflow_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
        )
        
        # Create indexes (check if they exist first)
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('quantitative_analysis_results')] if 'quantitative_analysis_results' in existing_tables else []
        
        if 'ix_quantitative_analysis_results_analysis_id' not in existing_indexes:
            op.create_index(op.f('ix_quantitative_analysis_results_analysis_id'), 'quantitative_analysis_results', ['analysis_id'], unique=True)
        if 'ix_quantitative_analysis_results_analysis_type' not in existing_indexes:
            op.create_index(op.f('ix_quantitative_analysis_results_analysis_type'), 'quantitative_analysis_results', ['analysis_type'], unique=False)
        if 'ix_quantitative_analysis_results_deal_id' not in existing_indexes:
            op.create_index(op.f('ix_quantitative_analysis_results_deal_id'), 'quantitative_analysis_results', ['deal_id'], unique=False)
        if 'ix_quantitative_analysis_results_status' not in existing_indexes:
            op.create_index(op.f('ix_quantitative_analysis_results_status'), 'quantitative_analysis_results', ['status'], unique=False)
        if 'ix_quantitative_analysis_results_user_id' not in existing_indexes:
            op.create_index(op.f('ix_quantitative_analysis_results_user_id'), 'quantitative_analysis_results', ['user_id'], unique=False)
        if 'ix_quantitative_analysis_results_workflow_id' not in existing_indexes:
            op.create_index(op.f('ix_quantitative_analysis_results_workflow_id'), 'quantitative_analysis_results', ['workflow_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index(op.f('ix_quantitative_analysis_results_workflow_id'), table_name='quantitative_analysis_results')
    op.drop_index(op.f('ix_quantitative_analysis_results_user_id'), table_name='quantitative_analysis_results')
    op.drop_index(op.f('ix_quantitative_analysis_results_status'), table_name='quantitative_analysis_results')
    op.drop_index(op.f('ix_quantitative_analysis_results_deal_id'), table_name='quantitative_analysis_results')
    op.drop_index(op.f('ix_quantitative_analysis_results_analysis_type'), table_name='quantitative_analysis_results')
    op.drop_index(op.f('ix_quantitative_analysis_results_analysis_id'), table_name='quantitative_analysis_results')
    
    # Drop table
    op.drop_table('quantitative_analysis_results')
