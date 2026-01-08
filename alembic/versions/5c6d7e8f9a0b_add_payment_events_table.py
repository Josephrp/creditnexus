"""Add payment_events table for x402 payments.

Revision ID: 5c6d7e8f9a0b
Revises: 4b5c6d7e8f9a
Create Date: 2025-01-05 22:00:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '5c6d7e8f9a0b'
down_revision: Union[str, None] = '4b5c6d7e8f9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create payment_events table with x402 payment support."""
    op.create_table(
        'payment_events',
        sa.Column('id', sa.Integer(), nullable=False),
        
        # Payment identification
        sa.Column('payment_id', sa.String(length=255), nullable=False, unique=True),
        sa.Column('payment_method', sa.String(length=50), nullable=False),  # x402, wire, ach, swift
        sa.Column('payment_type', sa.String(length=50), nullable=False),  # loan_disbursement, trade_settlement, etc.
        
        # Party information
        sa.Column('payer_id', sa.String(length=255), nullable=False),
        sa.Column('payer_name', sa.String(length=255), nullable=False),
        sa.Column('receiver_id', sa.String(length=255), nullable=False),
        sa.Column('receiver_name', sa.String(length=255), nullable=False),
        
        # Payment amount
        sa.Column('amount', sa.Numeric(precision=20, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        
        # Payment status (CDM state machine)
        sa.Column('status', sa.String(length=20), nullable=False),  # pending, verified, settled, failed, cancelled
        
        # x402-specific fields (JSONB for flexibility)
        sa.Column('x402_payment_payload', JSONB(), nullable=True),
        sa.Column('x402_verification', JSONB(), nullable=True),
        sa.Column('x402_settlement', JSONB(), nullable=True),
        sa.Column('transaction_hash', sa.String(length=255), nullable=True),
        
        # CDM references
        sa.Column('related_trade_id', sa.String(length=255), nullable=True),
        sa.Column('related_loan_id', sa.String(length=255), nullable=True),
        sa.Column('related_facility_id', sa.String(length=255), nullable=True),
        
        # Full CDM event (JSONB for complete CDM compliance)
        sa.Column('cdm_event', JSONB(), nullable=True),
        
        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('settled_at', sa.DateTime(), nullable=True),
        
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create indexes for fast queries
    op.create_index('idx_payment_events_payment_id', 'payment_events', ['payment_id'], unique=True)
    op.create_index('idx_payment_events_status', 'payment_events', ['status'], unique=False)
    op.create_index('idx_payment_events_related_trade_id', 'payment_events', ['related_trade_id'], unique=False)
    op.create_index('idx_payment_events_related_loan_id', 'payment_events', ['related_loan_id'], unique=False)
    op.create_index('idx_payment_events_created_at', 'payment_events', ['created_at'], unique=False)


def downgrade() -> None:
    """Drop payment_events table and indexes."""
    op.drop_index('idx_payment_events_created_at', table_name='payment_events')
    op.drop_index('idx_payment_events_related_loan_id', table_name='payment_events')
    op.drop_index('idx_payment_events_related_trade_id', table_name='payment_events')
    op.drop_index('idx_payment_events_status', table_name='payment_events')
    op.drop_index('idx_payment_events_payment_id', table_name='payment_events')
    op.drop_table('payment_events')
















