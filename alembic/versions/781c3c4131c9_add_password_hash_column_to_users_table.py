"""Create users table and add password_hash column

Revision ID: 781c3c4131c9
Revises: 
Create Date: 2025-12-08 15:08:33.998988

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '781c3c4131c9'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create users table with base columns and password_hash."""
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('replit_user_id', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=True),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('profile_image', sa.String(length=500), nullable=True),
        sa.Column('role', sa.String(length=20), nullable=False, server_default='analyst'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_users_replit_user_id', 'users', ['replit_user_id'], unique=True)
    op.create_index('ix_users_email', 'users', ['email'], unique=True)


def downgrade() -> None:
    """Drop users table."""
    op.drop_index('ix_users_email', table_name='users')
    op.drop_index('ix_users_replit_user_id', table_name='users')
    op.drop_table('users')
