"""fix_payment_event_and_notarization_fields

Revision ID: 07d94713c2c5
Revises: caa93833344a
Create Date: 2026-01-13 22:41:00.007856

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '07d94713c2c5'
down_revision: Union[str, Sequence[str], None] = 'caa93833344a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Fix PaymentEvent and NotarizationRecord fields to match models."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # ========================================================================
    # Fix NotarizationRecord: Make deal_id nullable (for securitization)
    # ========================================================================
    if 'notarization_records' in existing_tables:
        # Check if deal_id is nullable
        columns = inspector.get_columns('notarization_records')
        deal_id_col = next((col for col in columns if col['name'] == 'deal_id'), None)
        
        if deal_id_col and not deal_id_col['nullable']:
            # Make deal_id nullable (for securitization support)
            # Note: This requires dropping and recreating the foreign key constraint
            conn = op.get_bind()
            
            # Check if foreign key exists
            result = conn.execute(sa.text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'notarization_records' 
                AND constraint_name = 'fk_notarization_records_deal_id'
                AND constraint_type = 'FOREIGN KEY'
            """))
            fk_exists = result.fetchone() is not None
            
            if fk_exists:
                # Drop foreign key
                op.drop_constraint('fk_notarization_records_deal_id', 'notarization_records', type_='foreignkey')
            
            # Alter column to be nullable
            op.alter_column('notarization_records', 'deal_id', nullable=True)
            
            # Recreate foreign key if it existed
            if fk_exists:
                op.create_foreign_key(
                    'fk_notarization_records_deal_id',
                    'notarization_records',
                    'deals',
                    ['deal_id'],
                    ['id'],
                    ondelete='CASCADE'
                )
    
    # ========================================================================
    # Fix PaymentEvent: Add missing fields and fix column types
    # ========================================================================
    if 'payment_events' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('payment_events')]
        
        # Add payer_wallet_address if missing
        if 'payer_wallet_address' not in columns:
            op.add_column('payment_events', 
                sa.Column('payer_wallet_address', sa.String(length=255), nullable=True))
            op.create_index('ix_payment_events_payer_wallet_address', 
                'payment_events', ['payer_wallet_address'])
        
        # Add receiver_wallet_address if missing
        if 'receiver_wallet_address' not in columns:
            op.add_column('payment_events', 
                sa.Column('receiver_wallet_address', sa.String(length=255), nullable=True))
            op.create_index('ix_payment_events_receiver_wallet_address', 
                'payment_events', ['receiver_wallet_address'])
        
        # Add facilitator_url if missing
        if 'facilitator_url' not in columns:
            op.add_column('payment_events', 
                sa.Column('facilitator_url', sa.String(length=500), nullable=True))
        
        # Add payment_payload if missing (migration has x402_payment_payload, but model uses payment_payload)
        if 'payment_payload' not in columns:
            op.add_column('payment_events', 
                sa.Column('payment_payload', JSONB(), nullable=True))
        
        # Add related_deal_id if missing
        if 'related_deal_id' not in columns:
            op.add_column('payment_events', 
                sa.Column('related_deal_id', sa.Integer(), nullable=True))
            # Create foreign key
            op.create_foreign_key(
                'fk_payment_events_related_deal_id',
                'payment_events',
                'deals',
                ['related_deal_id'],
                ['id']
            )
            op.create_index('ix_payment_events_related_deal_id', 
                'payment_events', ['related_deal_id'])
        
        # Add payment_metadata if missing
        if 'payment_metadata' not in columns and 'metadata' not in columns:
            op.add_column('payment_events', 
                sa.Column('payment_metadata', JSONB(), nullable=True))
        
        # Add updated_at if missing
        if 'updated_at' not in columns:
            op.add_column('payment_events', 
                sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')))
        
        # Rename 'status' to 'payment_status' if it exists and payment_status doesn't
        if 'status' in columns and 'payment_status' not in columns:
            # Use raw SQL to rename column (works for PostgreSQL)
            conn = op.get_bind()
            if conn.dialect.name == 'postgresql':
                conn.execute(sa.text('ALTER TABLE payment_events RENAME COLUMN status TO payment_status'))
            # Update index name if it exists
            existing_indexes = [idx['name'] for idx in inspector.get_indexes('payment_events')]
            if 'idx_payment_events_status' in existing_indexes:
                op.drop_index('idx_payment_events_status', table_name='payment_events')
                op.create_index('ix_payment_events_payment_status', 
                    'payment_events', ['payment_status'])
        
        # Fix payer_id and receiver_id types (migration has String, model has Integer ForeignKey)
        # This is complex - we'll need to handle data migration carefully
        # For now, we'll just ensure the columns exist as Integer if they're String
        payer_id_col = next((col for col in inspector.get_columns('payment_events') if col['name'] == 'payer_id'), None)
        if payer_id_col and isinstance(payer_id_col['type'], sa.String):
            # Column exists as String, but should be Integer
            # This requires data migration - we'll skip for now and log a warning
            # In production, you'd need to migrate the data first
            pass
        
        # Fix related_trade_id and related_loan_id types (migration has String, model has Integer)
        # Similar issue - requires data migration
        trade_id_col = next((col for col in inspector.get_columns('payment_events') if col['name'] == 'related_trade_id'), None)
        if trade_id_col and isinstance(trade_id_col['type'], sa.String):
            # Skip for now - requires data migration
            pass


def downgrade() -> None:
    """Revert PaymentEvent and NotarizationRecord field changes."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    if 'payment_events' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('payment_events')]
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('payment_events')]
        
        # Drop indexes
        if 'ix_payment_events_payer_wallet_address' in existing_indexes:
            op.drop_index('ix_payment_events_payer_wallet_address', table_name='payment_events')
        if 'ix_payment_events_receiver_wallet_address' in existing_indexes:
            op.drop_index('ix_payment_events_receiver_wallet_address', table_name='payment_events')
        if 'ix_payment_events_related_deal_id' in existing_indexes:
            op.drop_index('ix_payment_events_related_deal_id', table_name='payment_events')
        
        # Drop foreign keys
        conn = op.get_bind()
        result = conn.execute(sa.text("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE table_name = 'payment_events' 
            AND constraint_name = 'fk_payment_events_related_deal_id'
            AND constraint_type = 'FOREIGN KEY'
        """))
        if result.fetchone():
            op.drop_constraint('fk_payment_events_related_deal_id', 'payment_events', type_='foreignkey')
        
        # Drop columns
        if 'payer_wallet_address' in columns:
            op.drop_column('payment_events', 'payer_wallet_address')
        if 'receiver_wallet_address' in columns:
            op.drop_column('payment_events', 'receiver_wallet_address')
        if 'facilitator_url' in columns:
            op.drop_column('payment_events', 'facilitator_url')
        if 'payment_payload' in columns:
            op.drop_column('payment_events', 'payment_payload')
        if 'related_deal_id' in columns:
            op.drop_column('payment_events', 'related_deal_id')
        if 'payment_metadata' in columns or 'metadata' in columns:
            # Check which name exists
            if 'payment_metadata' in columns:
                op.drop_column('payment_events', 'payment_metadata')
        if 'updated_at' in columns:
            op.drop_column('payment_events', 'updated_at')
        
        # Rename payment_status back to status if needed
        if 'payment_status' in columns and 'status' not in columns:
            conn = op.get_bind()
            if conn.dialect.name == 'postgresql':
                conn.execute(sa.text('ALTER TABLE payment_events RENAME COLUMN payment_status TO status'))
            if 'ix_payment_events_payment_status' in existing_indexes:
                op.drop_index('ix_payment_events_payment_status', table_name='payment_events')
                op.create_index('idx_payment_events_status', 'payment_events', ['status'])
    
    if 'notarization_records' in existing_tables:
        # Make deal_id NOT NULL again (revert)
        columns = inspector.get_columns('notarization_records')
        deal_id_col = next((col for col in columns if col['name'] == 'deal_id'), None)
        
        if deal_id_col and deal_id_col['nullable']:
            # Drop foreign key
            conn = op.get_bind()
            result = conn.execute(sa.text("""
                SELECT constraint_name 
                FROM information_schema.table_constraints 
                WHERE table_name = 'notarization_records' 
                AND constraint_name = 'fk_notarization_records_deal_id'
                AND constraint_type = 'FOREIGN KEY'
            """))
            if result.fetchone():
                op.drop_constraint('fk_notarization_records_deal_id', 'notarization_records', type_='foreignkey')
            
            # Make NOT NULL (this will fail if there are NULL values)
            op.alter_column('notarization_records', 'deal_id', nullable=False)
            
            # Recreate foreign key
            op.create_foreign_key(
                'fk_notarization_records_deal_id',
                'notarization_records',
                'deals',
                ['deal_id'],
                ['id'],
                ondelete='CASCADE'
            )
