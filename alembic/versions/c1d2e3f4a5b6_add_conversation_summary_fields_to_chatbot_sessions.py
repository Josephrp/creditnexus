"""add conversation summary fields to chatbot_sessions

Revision ID: c1d2e3f4a5b6
Revises: be048ae4e87e
Create Date: 2025-01-14 13:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, None] = 'be048ae4e87e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add conversation summary fields to chatbot_sessions table
    op.add_column('chatbot_sessions', sa.Column('conversation_summary', sa.Text(), nullable=True))
    op.add_column('chatbot_sessions', sa.Column('summary_key_points', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('chatbot_sessions', sa.Column('summary_updated_at', sa.DateTime(), nullable=True))
    op.add_column('chatbot_sessions', sa.Column('message_count', sa.Integer(), server_default='0', nullable=False))


def downgrade() -> None:
    # Remove conversation summary fields
    op.drop_column('chatbot_sessions', 'message_count')
    op.drop_column('chatbot_sessions', 'summary_updated_at')
    op.drop_column('chatbot_sessions', 'summary_key_points')
    op.drop_column('chatbot_sessions', 'conversation_summary')
