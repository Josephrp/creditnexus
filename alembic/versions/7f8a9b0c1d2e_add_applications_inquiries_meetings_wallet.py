"""add_applications_inquiries_meetings_wallet

Revision ID: 7f8a9b0c1d2e
Revises: 5c6d7e8f9a0b
Create Date: 2025-01-08 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '7f8a9b0c1d2e'
down_revision: Union[str, Sequence[str], None] = '5c6d7e8f9a0b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add applications, inquiries, meetings tables and wallet_address to users."""
    
    # Add wallet_address column to users table
    op.add_column('users', sa.Column('wallet_address', sa.String(length=255), nullable=True))
    op.create_index('ix_users_wallet_address', 'users', ['wallet_address'], unique=True)
    
    # Create applications table
    op.create_table(
        'applications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('application_type', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('submitted_at', sa.DateTime(), nullable=True),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('rejected_at', sa.DateTime(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('application_data', JSONB(), nullable=True),
        sa.Column('business_data', JSONB(), nullable=True),
        sa.Column('individual_data', JSONB(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_applications_user_id')
    )
    op.create_index('ix_applications_application_type', 'applications', ['application_type'])
    op.create_index('ix_applications_status', 'applications', ['status'])
    op.create_index('ix_applications_user_id', 'applications', ['user_id'])
    
    # Create inquiries table
    op.create_table(
        'inquiries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('inquiry_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='new'),
        sa.Column('priority', sa.String(length=20), nullable=False, server_default='normal'),
        sa.Column('application_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('subject', sa.String(length=500), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_by', sa.Integer(), nullable=True),
        sa.Column('response_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], name='fk_inquiries_application_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_inquiries_user_id'),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], name='fk_inquiries_assigned_to'),
        sa.ForeignKeyConstraint(['resolved_by'], ['users.id'], name='fk_inquiries_resolved_by')
    )
    op.create_index('ix_inquiries_inquiry_type', 'inquiries', ['inquiry_type'])
    op.create_index('ix_inquiries_status', 'inquiries', ['status'])
    op.create_index('ix_inquiries_application_id', 'inquiries', ['application_id'])
    op.create_index('ix_inquiries_user_id', 'inquiries', ['user_id'])
    
    # Create meetings table
    op.create_table(
        'meetings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=False),
        sa.Column('duration_minutes', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('meeting_type', sa.String(length=50), nullable=True),
        sa.Column('application_id', sa.Integer(), nullable=True),
        sa.Column('organizer_id', sa.Integer(), nullable=False),
        sa.Column('attendees', JSONB(), nullable=True),
        sa.Column('meeting_link', sa.String(length=500), nullable=True),
        sa.Column('ics_file_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['application_id'], ['applications.id'], name='fk_meetings_application_id'),
        sa.ForeignKeyConstraint(['organizer_id'], ['users.id'], name='fk_meetings_organizer_id')
    )
    op.create_index('ix_meetings_scheduled_at', 'meetings', ['scheduled_at'])
    op.create_index('ix_meetings_application_id', 'meetings', ['application_id'])


def downgrade() -> None:
    """Drop applications, inquiries, meetings tables and wallet_address column."""
    op.drop_index('ix_meetings_application_id', table_name='meetings')
    op.drop_index('ix_meetings_scheduled_at', table_name='meetings')
    op.drop_table('meetings')
    op.drop_index('ix_inquiries_user_id', table_name='inquiries')
    op.drop_index('ix_inquiries_application_id', table_name='inquiries')
    op.drop_index('ix_inquiries_status', table_name='inquiries')
    op.drop_index('ix_inquiries_inquiry_type', table_name='inquiries')
    op.drop_table('inquiries')
    op.drop_index('ix_applications_user_id', table_name='applications')
    op.drop_index('ix_applications_status', table_name='applications')
    op.drop_index('ix_applications_application_type', table_name='applications')
    op.drop_table('applications')
    op.drop_index('ix_users_wallet_address', table_name='users')
    op.drop_column('users', 'wallet_address')
