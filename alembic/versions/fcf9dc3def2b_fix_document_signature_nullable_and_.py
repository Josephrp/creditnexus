"""fix_document_signature_nullable_and_updated_at

Revision ID: fcf9dc3def2b
Revises: 07d94713c2c5
Create Date: 2026-01-13 22:54:51.771024

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcf9dc3def2b'
down_revision: Union[str, Sequence[str], None] = '07d94713c2c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix nullable constraints for document_signatures table to match model."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    if 'document_signatures' not in existing_tables:
        return
    
    # Get column information
    columns = inspector.get_columns('document_signatures')
    column_info = {col['name']: col for col in columns}
    
    # Fix document_id: Make nullable (model has nullable=True)
    if 'document_id' in column_info and not column_info['document_id']['nullable']:
        # Drop foreign key constraint first
        conn = op.get_bind()
        result = conn.execute(sa.text("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'document_signatures' 
            AND constraint_name = 'fk_document_signatures_document_id'
            AND constraint_type = 'FOREIGN KEY'
        """))
        fk_exists = result.fetchone() is not None
        
        if fk_exists:
            op.drop_constraint('fk_document_signatures_document_id', 'document_signatures', type_='foreignkey')
        
        # Make nullable
        op.alter_column('document_signatures', 'document_id', nullable=True)
        
        # Recreate foreign key
        if fk_exists:
            op.create_foreign_key(
                'fk_document_signatures_document_id',
                'document_signatures',
                'documents',
                ['document_id'],
                ['id']
            )
    
    # Fix signature_request_id: Make nullable (model has nullable=True)
    if 'signature_request_id' in column_info and not column_info['signature_request_id']['nullable']:
        # Drop unique constraint first (if it exists)
        conn = op.get_bind()
        result = conn.execute(sa.text("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'document_signatures' 
            AND constraint_name LIKE '%signature_request_id%'
            AND constraint_type = 'UNIQUE'
        """))
        unique_constraints = [row[0] for row in result.fetchall()]
        
        for constraint_name in unique_constraints:
            try:
                op.drop_constraint(constraint_name, 'document_signatures', type_='unique')
            except:
                pass
        
        # Make nullable
        op.alter_column('document_signatures', 'signature_request_id', nullable=True)
        
        # Recreate unique constraint (but allow NULLs)
        # Note: PostgreSQL allows multiple NULLs in a unique constraint
        op.create_index(
            'ix_document_signatures_signature_request_id_unique',
            'document_signatures',
            ['signature_request_id'],
            unique=True,
            postgresql_where=sa.text('signature_request_id IS NOT NULL')
        )
    
    # Fix signers: Make nullable (model has nullable=True)
    if 'signers' in column_info and not column_info['signers']['nullable']:
        op.alter_column('document_signatures', 'signers', nullable=True)


def downgrade() -> None:
    """Revert nullable constraint changes."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    if 'document_signatures' not in existing_tables:
        return
    
    columns = inspector.get_columns('document_signatures')
    column_info = {col['name']: col for col in columns}
    
    # Revert signers to NOT NULL (if currently nullable)
    if 'signers' in column_info and column_info['signers']['nullable']:
        # This will fail if there are NULL values - handle with care
        op.alter_column('document_signatures', 'signers', nullable=False, server_default='[]')
    
    # Revert signature_request_id to NOT NULL (if currently nullable)
    if 'signature_request_id' in column_info and column_info['signature_request_id']['nullable']:
        # Drop the partial unique index
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('document_signatures')]
        if 'ix_document_signatures_signature_request_id_unique' in existing_indexes:
            op.drop_index('ix_document_signatures_signature_request_id_unique', table_name='document_signatures')
        
        # This will fail if there are NULL values - handle with care
        op.alter_column('document_signatures', 'signature_request_id', nullable=False)
        
        # Recreate unique constraint
        op.create_index(
            'ix_document_signatures_signature_request_id',
            'document_signatures',
            ['signature_request_id'],
            unique=True
        )
    
    # Revert document_id to NOT NULL (if currently nullable)
    if 'document_id' in column_info and column_info['document_id']['nullable']:
        # Drop foreign key
        conn = op.get_bind()
        result = conn.execute(sa.text("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'document_signatures' 
            AND constraint_name = 'fk_document_signatures_document_id'
            AND constraint_type = 'FOREIGN KEY'
        """))
        if result.fetchone():
            op.drop_constraint('fk_document_signatures_document_id', 'document_signatures', type_='foreignkey')
        
        # This will fail if there are NULL values - handle with care
        op.alter_column('document_signatures', 'document_id', nullable=False)
        
        # Recreate foreign key
        op.create_foreign_key(
            'fk_document_signatures_document_id',
            'document_signatures',
            'documents',
            ['document_id'],
            ['id']
        )
