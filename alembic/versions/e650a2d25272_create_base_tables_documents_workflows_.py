"""create_base_tables_documents_workflows_audit

Revision ID: e650a2d25272
Revises: 3a7f8b9c1d2e
Create Date: 2026-01-07 00:26:04.039266

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'e650a2d25272'
down_revision: Union[str, Sequence[str], None] = '3a7f8b9c1d2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create base tables: documents, document_versions, workflows, audit_logs, oauth_tokens, refresh_tokens, staged_extractions."""
    
    # Create documents table
    op.create_table(
        'documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('borrower_name', sa.String(length=255), nullable=True),
        sa.Column('borrower_lei', sa.String(length=20), nullable=True),
        sa.Column('governing_law', sa.String(length=50), nullable=True),
        sa.Column('total_commitment', sa.Numeric(20, 2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=True),
        sa.Column('agreement_date', sa.Date(), nullable=True),
        sa.Column('sustainability_linked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('esg_metadata', JSONB(), nullable=True),
        sa.Column('uploaded_by', sa.Integer(), nullable=True),
        sa.Column('current_version_id', sa.Integer(), nullable=True),
        sa.Column('is_generated', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('template_id', sa.Integer(), nullable=True),
        sa.Column('source_cdm_data', JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], name='fk_documents_uploaded_by')
    )
    op.create_index('ix_documents_borrower_name', 'documents', ['borrower_name'])
    op.create_index('ix_documents_borrower_lei', 'documents', ['borrower_lei'])
    op.create_index('ix_documents_is_generated', 'documents', ['is_generated'])
    
    # Create document_versions table
    op.create_table(
        'document_versions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('extracted_data', JSONB(), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=True),
        sa.Column('source_filename', sa.String(length=255), nullable=True),
        sa.Column('extraction_method', sa.String(length=50), nullable=False, server_default='simple'),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name='fk_document_versions_document_id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_document_versions_created_by')
    )
    op.create_index('ix_document_versions_document_id', 'document_versions', ['document_id'])
    
    # Create workflows table
    op.create_table(
        'workflows',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('state', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('approved_by', sa.Integer(), nullable=True),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='normal'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('document_id'),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name='fk_workflows_document_id'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], name='fk_workflows_assigned_to'),
        sa.ForeignKeyConstraint(['approved_by'], ['users.id'], name='fk_workflows_approved_by')
    )
    op.create_index('ix_workflows_document_id', 'workflows', ['document_id'], unique=True)
    op.create_index('ix_workflows_state', 'workflows', ['state'])
    
    # Create audit_logs table
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.Integer(), nullable=True),
        sa.Column('action_metadata', JSONB(), nullable=True),
        sa.Column('ip_address', sa.String(length=50), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('occurred_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_audit_logs_user_id')
    )
    op.create_index('ix_audit_logs_action', 'audit_logs', ['action'])
    op.create_index('ix_audit_logs_occurred_at', 'audit_logs', ['occurred_at'])
    
    # Create oauth_tokens table
    op.create_table(
        'oauth_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False, server_default='replit'),
        sa.Column('browser_session_key', sa.String(length=255), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=True),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_type', sa.String(length=50), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('id_token', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_oauth_tokens_user_id')
    )
    op.create_index('ix_oauth_tokens_user_id', 'oauth_tokens', ['user_id'])
    op.create_index('ix_oauth_tokens_browser_session_key', 'oauth_tokens', ['browser_session_key'])
    
    # Create refresh_tokens table
    op.create_table(
        'refresh_tokens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('jti', sa.String(length=255), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('is_revoked', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('jti'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_refresh_tokens_user_id')
    )
    op.create_index('ix_refresh_tokens_jti', 'refresh_tokens', ['jti'], unique=True)
    op.create_index('ix_refresh_tokens_user_id', 'refresh_tokens', ['user_id'])
    
    # Create staged_extractions table
    op.create_table(
        'staged_extractions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
        sa.Column('agreement_data', JSONB(), nullable=False),
        sa.Column('original_text', sa.Text(), nullable=True),
        sa.Column('source_filename', sa.String(length=255), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('reviewed_by', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_staged_extractions_status', 'staged_extractions', ['status'])


def downgrade() -> None:
    """Drop base tables."""
    op.drop_index('ix_staged_extractions_status', table_name='staged_extractions')
    op.drop_table('staged_extractions')
    op.drop_index('ix_refresh_tokens_user_id', table_name='refresh_tokens')
    op.drop_index('ix_refresh_tokens_jti', table_name='refresh_tokens')
    op.drop_table('refresh_tokens')
    op.drop_index('ix_oauth_tokens_browser_session_key', table_name='oauth_tokens')
    op.drop_index('ix_oauth_tokens_user_id', table_name='oauth_tokens')
    op.drop_table('oauth_tokens')
    op.drop_index('ix_audit_logs_occurred_at', table_name='audit_logs')
    op.drop_index('ix_audit_logs_action', table_name='audit_logs')
    op.drop_table('audit_logs')
    op.drop_index('ix_workflows_state', table_name='workflows')
    op.drop_index('ix_workflows_document_id', table_name='workflows')
    op.drop_table('workflows')
    op.drop_index('ix_document_versions_document_id', table_name='document_versions')
    op.drop_table('document_versions')
    op.drop_index('ix_documents_is_generated', table_name='documents')
    op.drop_index('ix_documents_borrower_lei', table_name='documents')
    op.drop_index('ix_documents_borrower_name', table_name='documents')
    op.drop_table('documents')
