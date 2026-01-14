"""add_loan_recovery_tables

Revision ID: d9300e06ed44
Revises: 6f85cf4fc118
Create Date: 2026-01-14 01:03:33.932237

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = 'd9300e06ed44'
down_revision: Union[str, Sequence[str], None] = '6f85cf4fc118'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add loan recovery tables: loan_defaults, recovery_actions, borrower_contacts."""
    
    # Check if tables already exist (idempotent migration)
    bind = op.get_bind()
    inspector = inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Create loan_defaults table
    if 'loan_defaults' not in existing_tables:
        op.create_table(
            'loan_defaults',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('loan_id', sa.String(length=255), nullable=True),
        sa.Column('deal_id', sa.Integer(), nullable=True),
        sa.Column('default_type', sa.String(length=50), nullable=False),
        sa.Column('default_date', sa.DateTime(), nullable=False),
        sa.Column('default_reason', sa.Text(), nullable=True),
        sa.Column('amount_overdue', sa.Numeric(20, 2), nullable=True),
        sa.Column('days_past_due', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('severity', sa.String(length=20), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='open'),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('cdm_events', JSONB(), nullable=True),
        sa.Column('metadata', JSONB(), nullable=True),  # Maps to default_metadata attribute in model (name="metadata" to avoid SQLAlchemy reserved name)
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ondelete='CASCADE', name='fk_loan_defaults_deal_id'),
        sa.CheckConstraint("severity IN ('low', 'medium', 'high', 'critical')", name='ck_loan_defaults_severity'),
        sa.CheckConstraint("status IN ('open', 'in_recovery', 'resolved', 'written_off')", name='ck_loan_defaults_status')
        )
        
        # Create indexes for loan_defaults
        op.create_index('ix_loan_defaults_loan_id', 'loan_defaults', ['loan_id'])
        op.create_index('ix_loan_defaults_deal_id', 'loan_defaults', ['deal_id'])
        op.create_index('ix_loan_defaults_default_date', 'loan_defaults', ['default_date'])
        op.create_index('ix_loan_defaults_status', 'loan_defaults', ['status'])
        op.create_index('ix_loan_defaults_severity', 'loan_defaults', ['severity'])
        op.create_index('ix_loan_defaults_default_type', 'loan_defaults', ['default_type'])
    
    # Create recovery_actions table
    if 'recovery_actions' not in existing_tables:
        op.create_table(
            'recovery_actions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('loan_default_id', sa.Integer(), nullable=False),
        sa.Column('action_type', sa.String(length=50), nullable=False),
        sa.Column('communication_method', sa.String(length=20), nullable=False),
        sa.Column('recipient_phone', sa.String(length=20), nullable=True),
        sa.Column('recipient_email', sa.String(length=255), nullable=True),
        sa.Column('message_template', sa.String(length=255), nullable=False),
        sa.Column('message_content', sa.Text(), nullable=False),
        sa.Column('twilio_message_sid', sa.String(length=255), nullable=True),
        sa.Column('twilio_call_sid', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='pending'),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('response_received_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('metadata', JSONB(), nullable=True),  # Maps to action_metadata attribute in model (name="metadata" to avoid SQLAlchemy reserved name)
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['loan_default_id'], ['loan_defaults.id'], ondelete='CASCADE', name='fk_recovery_actions_loan_default_id'),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], name='fk_recovery_actions_created_by'),
        sa.CheckConstraint("status IN ('pending', 'sent', 'delivered', 'failed', 'responded')", name='ck_recovery_actions_status'),
        sa.CheckConstraint("communication_method IN ('sms', 'voice', 'email')", name='ck_recovery_actions_communication_method')
        )
        
        # Create indexes for recovery_actions
        op.create_index('ix_recovery_actions_loan_default_id', 'recovery_actions', ['loan_default_id'])
        op.create_index('ix_recovery_actions_status', 'recovery_actions', ['status'])
        op.create_index('ix_recovery_actions_action_type', 'recovery_actions', ['action_type'])
        op.create_index('ix_recovery_actions_scheduled_at', 'recovery_actions', ['scheduled_at'])
        op.create_index('ix_recovery_actions_twilio_message_sid', 'recovery_actions', ['twilio_message_sid'])
        op.create_index('ix_recovery_actions_twilio_call_sid', 'recovery_actions', ['twilio_call_sid'])
    
    # Create borrower_contacts table
    if 'borrower_contacts' not in existing_tables:
        op.create_table(
            'borrower_contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('deal_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('contact_name', sa.String(length=255), nullable=False),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('preferred_contact_method', sa.String(length=20), nullable=False, server_default='sms'),
        sa.Column('contact_preferences', JSONB(), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('metadata', JSONB(), nullable=True),  # Maps to contact_metadata attribute in model (name="metadata" to avoid SQLAlchemy reserved name)
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], ondelete='CASCADE', name='fk_borrower_contacts_deal_id'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], name='fk_borrower_contacts_user_id'),
        sa.CheckConstraint("preferred_contact_method IN ('sms', 'voice', 'email')", name='ck_borrower_contacts_preferred_method')
        )
        
        # Create indexes for borrower_contacts
        op.create_index('ix_borrower_contacts_deal_id', 'borrower_contacts', ['deal_id'])
        op.create_index('ix_borrower_contacts_user_id', 'borrower_contacts', ['user_id'])


def downgrade() -> None:
    """Remove loan recovery tables."""
    # Drop indexes first
    op.drop_index('ix_borrower_contacts_user_id', table_name='borrower_contacts')
    op.drop_index('ix_borrower_contacts_deal_id', table_name='borrower_contacts')
    op.drop_index('ix_recovery_actions_twilio_call_sid', table_name='recovery_actions')
    op.drop_index('ix_recovery_actions_twilio_message_sid', table_name='recovery_actions')
    op.drop_index('ix_recovery_actions_scheduled_at', table_name='recovery_actions')
    op.drop_index('ix_recovery_actions_action_type', table_name='recovery_actions')
    op.drop_index('ix_recovery_actions_status', table_name='recovery_actions')
    op.drop_index('ix_recovery_actions_loan_default_id', table_name='recovery_actions')
    op.drop_index('ix_loan_defaults_default_type', table_name='loan_defaults')
    op.drop_index('ix_loan_defaults_severity', table_name='loan_defaults')
    op.drop_index('ix_loan_defaults_status', table_name='loan_defaults')
    op.drop_index('ix_loan_defaults_default_date', table_name='loan_defaults')
    op.drop_index('ix_loan_defaults_deal_id', table_name='loan_defaults')
    op.drop_index('ix_loan_defaults_loan_id', table_name='loan_defaults')
    
    # Drop tables (order matters due to foreign keys)
    op.drop_table('borrower_contacts')
    op.drop_table('recovery_actions')
    op.drop_table('loan_defaults')
