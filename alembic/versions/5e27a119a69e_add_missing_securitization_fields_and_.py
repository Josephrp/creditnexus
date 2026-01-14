"""add_missing_securitization_fields_and_workflow_delegations

Revision ID: 5e27a119a69e
Revises: fcf9dc3def2b
Create Date: 2026-01-13 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB


# revision identifiers, used by Alembic.
revision: str = '5e27a119a69e'
down_revision: Union[str, None] = 'fcf9dc3def2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add missing fields to securitization tables and create workflow_delegations tables."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # ========================================================================
    # 1. Create workflow_delegations table
    # ========================================================================
    if 'workflow_delegations' not in existing_tables:
        op.create_table(
            'workflow_delegations',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('workflow_id', sa.String(length=255), nullable=False, unique=True),
            sa.Column('workflow_type', sa.String(length=50), nullable=False),
            sa.Column('deal_id', sa.Integer(), nullable=True),
            sa.Column('document_id', sa.Integer(), nullable=True),
            sa.Column('sender_user_id', sa.Integer(), nullable=False),
            sa.Column('receiver_user_id', sa.Integer(), nullable=True),
            sa.Column('receiver_email', sa.String(length=255), nullable=True),
            sa.Column('link_payload', sa.Text(), nullable=True),
            sa.Column('workflow_metadata', JSONB(), nullable=True),
            sa.Column('whitelist_config', JSONB(), nullable=True),
            sa.Column('status', sa.String(length=20), nullable=False, server_default='pending'),
            sa.Column('expires_at', sa.DateTime(), nullable=False),
            sa.Column('completed_at', sa.DateTime(), nullable=True),
            sa.Column('callback_url', sa.String(length=500), nullable=True),
            sa.Column('state_synced_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['deal_id'], ['deals.id'], name='fk_workflow_delegations_deal_id', ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['document_id'], ['documents.id'], name='fk_workflow_delegations_document_id', ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['sender_user_id'], ['users.id'], name='fk_workflow_delegations_sender_user_id', ondelete='SET NULL'),
            sa.ForeignKeyConstraint(['receiver_user_id'], ['users.id'], name='fk_workflow_delegations_receiver_user_id', ondelete='SET NULL'),
        )
        op.create_index('ix_workflow_delegations_workflow_id', 'workflow_delegations', ['workflow_id'], unique=True)
        op.create_index('ix_workflow_delegations_workflow_type', 'workflow_delegations', ['workflow_type'])
        op.create_index('ix_workflow_delegations_deal_id', 'workflow_delegations', ['deal_id'])
        op.create_index('ix_workflow_delegations_document_id', 'workflow_delegations', ['document_id'])
        op.create_index('ix_workflow_delegations_sender_user_id', 'workflow_delegations', ['sender_user_id'])
        op.create_index('ix_workflow_delegations_receiver_user_id', 'workflow_delegations', ['receiver_user_id'])
        op.create_index('ix_workflow_delegations_receiver_email', 'workflow_delegations', ['receiver_email'])
        op.create_index('ix_workflow_delegations_status', 'workflow_delegations', ['status'])
        op.create_index('ix_workflow_delegations_expires_at', 'workflow_delegations', ['expires_at'])
    
    # ========================================================================
    # 2. Create workflow_delegation_states table
    # ========================================================================
    if 'workflow_delegation_states' not in existing_tables:
        op.create_table(
            'workflow_delegation_states',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('delegation_id', sa.Integer(), nullable=False),
            sa.Column('state', sa.String(length=50), nullable=False),
            sa.Column('state_metadata', JSONB(), nullable=True),
            sa.Column('timestamp', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.PrimaryKeyConstraint('id'),
            sa.ForeignKeyConstraint(['delegation_id'], ['workflow_delegations.id'], name='fk_workflow_delegation_states_delegation_id', ondelete='CASCADE'),
        )
        op.create_index('ix_workflow_delegation_states_delegation_id', 'workflow_delegation_states', ['delegation_id'])
        op.create_index('ix_workflow_delegation_states_state', 'workflow_delegation_states', ['state'])
        op.create_index('ix_workflow_delegation_states_timestamp', 'workflow_delegation_states', ['timestamp'])
    
    # ========================================================================
    # 3. Add missing fields to securitization_pools
    # ========================================================================
    if 'securitization_pools' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('securitization_pools')]
        
        if 'cdm_data' not in columns:
            op.add_column('securitization_pools', sa.Column('cdm_data', JSONB(), nullable=True))
    
    # ========================================================================
    # 4. Add missing fields to securitization_tranches
    # ========================================================================
    if 'securitization_tranches' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('securitization_tranches')]
        
        # Rename tranche_size to size if it exists
        if 'tranche_size' in columns and 'size' not in columns:
            op.alter_column('securitization_tranches', 'tranche_size', new_column_name='size')
        
        # Add missing fields
        if 'tranche_id' not in columns:
            op.add_column('securitization_tranches', sa.Column('tranche_id', sa.String(length=255), nullable=True))
            op.create_index('ix_securitization_tranches_tranche_id', 'securitization_tranches', ['tranche_id'])
        
        if 'currency' not in columns:
            op.add_column('securitization_tranches', sa.Column('currency', sa.String(length=3), nullable=True))
        
        if 'principal_remaining' not in columns:
            op.add_column('securitization_tranches', sa.Column('principal_remaining', sa.Numeric(precision=20, scale=2), nullable=True))
        
        if 'interest_accrued' not in columns:
            op.add_column('securitization_tranches', sa.Column('interest_accrued', sa.Numeric(precision=20, scale=2), nullable=True, server_default='0'))
        
        if 'token_id' not in columns:
            op.add_column('securitization_tranches', sa.Column('token_id', sa.String(length=255), nullable=True, unique=True))
            op.create_index('ix_securitization_tranches_token_id', 'securitization_tranches', ['token_id'], unique=True)
        
        if 'owner_wallet_address' not in columns:
            op.add_column('securitization_tranches', sa.Column('owner_wallet_address', sa.String(length=255), nullable=True))
            op.create_index('ix_securitization_tranches_owner_wallet_address', 'securitization_tranches', ['owner_wallet_address'])
        
        # Rename cdm_tranche_data to cdm_data if it exists
        if 'cdm_tranche_data' in columns and 'cdm_data' not in columns:
            op.alter_column('securitization_tranches', 'cdm_tranche_data', new_column_name='cdm_data')
    
    # ========================================================================
    # 5. Add missing fields to securitization_pool_assets
    # ========================================================================
    if 'securitization_pool_assets' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('securitization_pool_assets')]
        
        if 'asset_id' not in columns:
            op.add_column('securitization_pool_assets', sa.Column('asset_id', sa.String(length=255), nullable=True))
        
        if 'asset_value' not in columns:
            op.add_column('securitization_pool_assets', sa.Column('asset_value', sa.Numeric(precision=20, scale=2), nullable=True))
        
        if 'currency' not in columns:
            op.add_column('securitization_pool_assets', sa.Column('currency', sa.String(length=3), nullable=True))
    
    # ========================================================================
    # 6. Fix field names in regulatory_filings (rename to match model)
    # ========================================================================
    if 'regulatory_filings' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('regulatory_filings')]
        
        # Rename filing_body to regulatory_body
        if 'filing_body' in columns and 'regulatory_body' not in columns:
            op.alter_column('regulatory_filings', 'filing_body', new_column_name='regulatory_body')
        
        # Rename filing_status to status
        if 'filing_status' in columns and 'status' not in columns:
            # First drop the index if it exists
            existing_indexes = [idx['name'] for idx in inspector.get_indexes('regulatory_filings')]
            if 'idx_regulatory_filings_status' in existing_indexes:
                op.drop_index('idx_regulatory_filings_status', table_name='regulatory_filings')
            
            op.alter_column('regulatory_filings', 'filing_status', new_column_name='status')
            
            # Recreate index with new name
            op.create_index('ix_regulatory_filings_status', 'regulatory_filings', ['status'])
        
        # Rename submitted_at to filed_at
        if 'submitted_at' in columns and 'filed_at' not in columns:
            op.alter_column('regulatory_filings', 'submitted_at', new_column_name='filed_at')
        
        # Add filing_metadata (stored as 'metadata' column)
        if 'metadata' not in columns and 'filing_metadata' not in columns:
            op.add_column('regulatory_filings', sa.Column('metadata', JSONB(), nullable=True))


def downgrade() -> None:
    """Revert changes."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    existing_tables = inspector.get_table_names()
    
    # Drop workflow_delegation_states
    if 'workflow_delegation_states' in existing_tables:
        op.drop_index('ix_workflow_delegation_states_timestamp', table_name='workflow_delegation_states')
        op.drop_index('ix_workflow_delegation_states_state', table_name='workflow_delegation_states')
        op.drop_index('ix_workflow_delegation_states_delegation_id', table_name='workflow_delegation_states')
        op.drop_table('workflow_delegation_states')
    
    # Drop workflow_delegations
    if 'workflow_delegations' in existing_tables:
        op.drop_index('ix_workflow_delegations_expires_at', table_name='workflow_delegations')
        op.drop_index('ix_workflow_delegations_status', table_name='workflow_delegations')
        op.drop_index('ix_workflow_delegations_receiver_email', table_name='workflow_delegations')
        op.drop_index('ix_workflow_delegations_receiver_user_id', table_name='workflow_delegations')
        op.drop_index('ix_workflow_delegations_sender_user_id', table_name='workflow_delegations')
        op.drop_index('ix_workflow_delegations_document_id', table_name='workflow_delegations')
        op.drop_index('ix_workflow_delegations_deal_id', table_name='workflow_delegations')
        op.drop_index('ix_workflow_delegations_workflow_type', table_name='workflow_delegations')
        op.drop_index('ix_workflow_delegations_workflow_id', table_name='workflow_delegations')
        op.drop_table('workflow_delegations')
    
    # Revert regulatory_filings changes
    if 'regulatory_filings' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('regulatory_filings')]
        
        if 'metadata' in columns:
            op.drop_column('regulatory_filings', 'metadata')
        
        if 'filed_at' in columns:
            op.alter_column('regulatory_filings', 'filed_at', new_column_name='submitted_at')
        
        if 'status' in columns:
            op.drop_index('ix_regulatory_filings_status', table_name='regulatory_filings')
            op.alter_column('regulatory_filings', 'status', new_column_name='filing_status')
            op.create_index('idx_regulatory_filings_status', 'regulatory_filings', ['filing_status'])
        
        if 'regulatory_body' in columns:
            op.alter_column('regulatory_filings', 'regulatory_body', new_column_name='filing_body')
    
    # Revert securitization_pool_assets changes
    if 'securitization_pool_assets' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('securitization_pool_assets')]
        
        if 'currency' in columns:
            op.drop_column('securitization_pool_assets', 'currency')
        if 'asset_value' in columns:
            op.drop_column('securitization_pool_assets', 'asset_value')
        if 'asset_id' in columns:
            op.drop_column('securitization_pool_assets', 'asset_id')
    
    # Revert securitization_tranches changes
    if 'securitization_tranches' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('securitization_tranches')]
        
        if 'cdm_data' in columns:
            op.alter_column('securitization_tranches', 'cdm_data', new_column_name='cdm_tranche_data')
        
        if 'owner_wallet_address' in columns:
            op.drop_index('ix_securitization_tranches_owner_wallet_address', table_name='securitization_tranches')
            op.drop_column('securitization_tranches', 'owner_wallet_address')
        
        if 'token_id' in columns:
            op.drop_index('ix_securitization_tranches_token_id', table_name='securitization_tranches')
            op.drop_column('securitization_tranches', 'token_id')
        
        if 'interest_accrued' in columns:
            op.drop_column('securitization_tranches', 'interest_accrued')
        
        if 'principal_remaining' in columns:
            op.drop_column('securitization_tranches', 'principal_remaining')
        
        if 'currency' in columns:
            op.drop_column('securitization_tranches', 'currency')
        
        if 'tranche_id' in columns:
            op.drop_index('ix_securitization_tranches_tranche_id', table_name='securitization_tranches')
            op.drop_column('securitization_tranches', 'tranche_id')
        
        if 'size' in columns:
            op.alter_column('securitization_tranches', 'size', new_column_name='tranche_size')
    
    # Revert securitization_pools changes
    if 'securitization_pools' in existing_tables:
        columns = [col['name'] for col in inspector.get_columns('securitization_pools')]
        
        if 'cdm_data' in columns:
            op.drop_column('securitization_pools', 'cdm_data')
