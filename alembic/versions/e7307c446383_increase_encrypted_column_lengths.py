"""increase_encrypted_column_lengths

Revision ID: e7307c446383
Revises: d18dc4164098
Create Date: 2026-01-14 19:53:02.504092

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7307c446383'
down_revision: Union[str, Sequence[str], None] = 'd18dc4164098'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # documents table
    op.execute("ALTER TABLE documents ALTER COLUMN borrower_name TYPE TEXT")
    op.execute("ALTER TABLE documents ALTER COLUMN borrower_lei TYPE TEXT")
    
    # users table
    op.execute("ALTER TABLE users ALTER COLUMN email TYPE TEXT")
    op.execute("ALTER TABLE users ALTER COLUMN display_name TYPE TEXT")
    op.execute("ALTER TABLE users ALTER COLUMN wallet_address TYPE TEXT")
    
    # document_versions table
    op.execute("ALTER TABLE document_versions ALTER COLUMN source_filename TYPE TEXT")
    
    # audit_logs table
    op.execute("ALTER TABLE audit_logs ALTER COLUMN ip_address TYPE TEXT")


def downgrade() -> None:
    """Downgrade schema (reverting to original lengths)."""
    # Note: downgrade might fail if data exceeds original lengths
    op.execute("ALTER TABLE audit_logs ALTER COLUMN ip_address TYPE VARCHAR(255)")
    op.execute("ALTER TABLE document_versions ALTER COLUMN source_filename TYPE VARCHAR(255)")
    op.execute("ALTER TABLE users ALTER COLUMN wallet_address TYPE VARCHAR(255)")
    op.execute("ALTER TABLE users ALTER COLUMN display_name TYPE VARCHAR(255)")
    op.execute("ALTER TABLE users ALTER COLUMN email TYPE VARCHAR(255)")
    op.execute("ALTER TABLE documents ALTER COLUMN borrower_lei TYPE VARCHAR(20)")
    op.execute("ALTER TABLE documents ALTER COLUMN borrower_name TYPE VARCHAR(255)")
