"""add_accounting_documents_and_deep_research_results_tables

Revision ID: d81fee5c6be1
Revises: efa5b2aec0c6
Create Date: 2026-01-14 10:46:17.052050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'd81fee5c6be1'
down_revision: Union[str, Sequence[str], None] = 'efa5b2aec0c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create accounting_documents table
    op.create_table(
        'accounting_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False),
        sa.Column('extracted_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('reporting_period_start', sa.Date(), nullable=True),
        sa.Column('reporting_period_end', sa.Date(), nullable=True),
        sa.Column('period_type', sa.String(length=20), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE')
    )
    op.create_index('ix_accounting_documents_document_id', 'accounting_documents', ['document_id'], unique=True)
    op.create_index('ix_accounting_documents_document_type', 'accounting_documents', ['document_type'], unique=False)
    op.create_index('ix_accounting_documents_period_type', 'accounting_documents', ['period_type'], unique=False)
    op.create_index('ix_accounting_documents_reporting_period', 'accounting_documents', ['reporting_period_start', 'reporting_period_end'], unique=False)
    
    # Create deep_research_results table
    op.create_table(
        'deep_research_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('research_id', sa.String(length=36), nullable=False),
        sa.Column('query', sa.Text(), nullable=False),
        sa.Column('answer', sa.Text(), nullable=True),
        sa.Column('knowledge_items', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('visited_urls', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('searched_queries', postgresql.ARRAY(sa.String()), nullable=True),
        sa.Column('token_usage', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('deal_id', sa.Integer(), nullable=True),
        sa.Column('workflow_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), server_default='pending', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('research_id'),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['workflow_id'], ['workflows.id'], ondelete='SET NULL')
    )
    op.create_index('ix_deep_research_results_research_id', 'deep_research_results', ['research_id'], unique=True)
    op.create_index('ix_deep_research_results_deal_id', 'deep_research_results', ['deal_id'], unique=False)
    op.create_index('ix_deep_research_results_workflow_id', 'deep_research_results', ['workflow_id'], unique=False)
    op.create_index('ix_deep_research_results_status', 'deep_research_results', ['status'], unique=False)
    op.create_index('ix_deep_research_results_created_at', 'deep_research_results', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop deep_research_results table
    op.drop_index('ix_deep_research_results_created_at', table_name='deep_research_results')
    op.drop_index('ix_deep_research_results_status', table_name='deep_research_results')
    op.drop_index('ix_deep_research_results_workflow_id', table_name='deep_research_results')
    op.drop_index('ix_deep_research_results_deal_id', table_name='deep_research_results')
    op.drop_index('ix_deep_research_results_research_id', table_name='deep_research_results')
    op.drop_table('deep_research_results')
    
    # Drop accounting_documents table
    op.drop_index('ix_accounting_documents_reporting_period', table_name='accounting_documents')
    op.drop_index('ix_accounting_documents_period_type', table_name='accounting_documents')
    op.drop_index('ix_accounting_documents_document_type', table_name='accounting_documents')
    op.drop_index('ix_accounting_documents_document_id', table_name='accounting_documents')
    op.drop_table('accounting_documents')
