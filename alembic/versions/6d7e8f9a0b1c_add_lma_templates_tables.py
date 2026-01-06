"""Add LMA template tables for document generation.

Revision ID: 6d7e8f9a0b1c
Revises: 5c6d7e8f9a0b
Create Date: 2025-01-05 23:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '6d7e8f9a0b1c'
down_revision: Union[str, None] = '5c6d7e8f9a0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create LMA template tables for document generation."""
    
    # Create lma_templates table
    op.create_table(
        'lma_templates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_code', sa.String(length=50), nullable=False, unique=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('category', sa.String(length=100), nullable=False),  # Facility Agreement, Term Sheet, etc.
        sa.Column('subcategory', sa.String(length=100), nullable=True),  # Corporate Lending, REF, etc.
        sa.Column('governing_law', sa.String(length=50), nullable=True),  # English, NY, Delaware, etc.
        sa.Column('version', sa.String(length=20), nullable=False),
        sa.Column('file_path', sa.Text(), nullable=False),  # Path to template Word file
        sa.Column('metadata', JSONB(), nullable=True),  # Template-specific metadata
        sa.Column('required_fields', JSONB(), nullable=True),  # Required CDM field paths
        sa.Column('optional_fields', JSONB(), nullable=True),  # Optional CDM field paths
        sa.Column('ai_generated_sections', JSONB(), nullable=True),  # Sections to be AI-generated
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create generated_documents table
    op.create_table(
        'generated_documents',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('source_document_id', sa.Integer(), nullable=True),  # If generated from existing document
        sa.Column('cdm_data', JSONB(), nullable=False),  # CDM data used for generation
        sa.Column('generated_content', sa.Text(), nullable=True),  # Generated document text (optional)
        sa.Column('file_path', sa.Text(), nullable=True),  # Path to generated Word/PDF file
        sa.Column('status', sa.String(length=50), server_default='draft', nullable=False),  # draft, review, approved, executed
        sa.Column('generation_summary', JSONB(), nullable=True),  # Summary of generation (fields populated, AI fields, etc.)
        sa.Column('created_by', sa.Integer(), nullable=True),  # Foreign key to users
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['template_id'], ['lma_templates.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['source_document_id'], ['documents.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ondelete='SET NULL'),
    )
    
    # Create template_field_mappings table
    op.create_table(
        'template_field_mappings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_id', sa.Integer(), nullable=False),
        sa.Column('template_field', sa.String(length=255), nullable=False),  # Field name in template (e.g., "[BORROWER_NAME]")
        sa.Column('cdm_field', sa.String(length=255), nullable=False),  # CDM field path (e.g., "parties[role='Borrower'].name")
        sa.Column('mapping_type', sa.String(length=50), nullable=True),  # direct, computed, ai_generated
        sa.Column('transformation_rule', sa.Text(), nullable=True),  # Optional transformation rule for computed fields
        sa.Column('is_required', sa.Boolean(), server_default='false', nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['template_id'], ['lma_templates.id'], ondelete='CASCADE'),
    )
    
    # Create indexes for fast queries
    op.create_index('idx_lma_templates_template_code', 'lma_templates', ['template_code'], unique=True)
    op.create_index('idx_lma_templates_category', 'lma_templates', ['category'], unique=False)
    op.create_index('idx_lma_templates_subcategory', 'lma_templates', ['subcategory'], unique=False)
    op.create_index('idx_generated_documents_template_id', 'generated_documents', ['template_id'], unique=False)
    op.create_index('idx_generated_documents_source_document_id', 'generated_documents', ['source_document_id'], unique=False)
    op.create_index('idx_generated_documents_status', 'generated_documents', ['status'], unique=False)
    op.create_index('idx_generated_documents_created_by', 'generated_documents', ['created_by'], unique=False)
    op.create_index('idx_template_field_mappings_template_id', 'template_field_mappings', ['template_id'], unique=False)
    op.create_index('idx_template_field_mappings_template_field', 'template_field_mappings', ['template_field'], unique=False)


def downgrade() -> None:
    """Drop LMA template tables and indexes."""
    op.drop_index('idx_template_field_mappings_template_field', table_name='template_field_mappings')
    op.drop_index('idx_template_field_mappings_template_id', table_name='template_field_mappings')
    op.drop_index('idx_generated_documents_created_by', table_name='generated_documents')
    op.drop_index('idx_generated_documents_status', table_name='generated_documents')
    op.drop_index('idx_generated_documents_source_document_id', table_name='generated_documents')
    op.drop_index('idx_generated_documents_template_id', table_name='generated_documents')
    op.drop_index('idx_lma_templates_subcategory', table_name='lma_templates')
    op.drop_index('idx_lma_templates_category', table_name='lma_templates')
    op.drop_index('idx_lma_templates_template_code', table_name='lma_templates')
    op.drop_table('template_field_mappings')
    op.drop_table('generated_documents')
    op.drop_table('lma_templates')







