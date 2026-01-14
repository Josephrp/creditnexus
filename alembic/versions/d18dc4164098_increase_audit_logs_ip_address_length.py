"""increase_audit_logs_ip_address_length

Revision ID: d18dc4164098
Revises: ff16ad99f573
Create Date: 2026-01-14 19:00:47.825242

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd18dc4164098'
down_revision: Union[str, Sequence[str], None] = 'ff16ad99f573'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Increase ip_address column length in audit_logs table to accommodate encrypted values."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    if 'audit_logs' not in existing_tables:
        return
    
    # Get column information
    columns = inspector.get_columns('audit_logs')
    column_info = {col['name']: col for col in columns}
    
    # Increase ip_address column length from 50 to 255
    if 'ip_address' in column_info:
        # Check current length
        current_type = str(column_info['ip_address']['type'])
        if '50' in current_type or 'VARCHAR(50)' in current_type:
            op.alter_column(
                'audit_logs',
                'ip_address',
                type_=sa.String(length=255),
                existing_type=sa.String(length=50),
                existing_nullable=True
            )


def downgrade() -> None:
    """Revert ip_address column length back to 50."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    if 'audit_logs' not in existing_tables:
        return
    
    columns = inspector.get_columns('audit_logs')
    column_info = {col['name']: col for col in columns}
    
    # Revert ip_address column length from 255 to 50
    if 'ip_address' in column_info:
        current_type = str(column_info['ip_address']['type'])
        if '255' in current_type or 'VARCHAR(255)' in current_type:
            # Note: This will fail if there are values longer than 50 characters
            op.alter_column(
                'audit_logs',
                'ip_address',
                type_=sa.String(length=50),
                existing_type=sa.String(length=255),
                existing_nullable=True
            )
