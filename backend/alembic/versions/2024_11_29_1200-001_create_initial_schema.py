"""create initial schema

Revision ID: 001
Revises: 
Create Date: 2024-11-29 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('auth0_id', sa.String(255), nullable=False, unique=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(100), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    
    # Create platform_connections table
    op.create_table(
        'platform_connections',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('access_token', sa.Text, nullable=False),
        sa.Column('refresh_token', sa.Text, nullable=True),
        sa.Column('token_expires_at', sa.TIMESTAMP, nullable=True),
        sa.Column('connected_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('last_sync_at', sa.TIMESTAMP, nullable=True),
        sa.UniqueConstraint('user_id', 'platform', name='uq_user_platform')
    )
    
    # Create messages table
    op.create_table(
        'messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('platform', sa.String(50), nullable=False),
        sa.Column('platform_message_id', sa.String(255), nullable=False),
        sa.Column('sender', sa.String(255), nullable=False),
        sa.Column('content', sa.Text, nullable=False),
        sa.Column('subject', sa.String(500), nullable=True),
        sa.Column('timestamp', sa.TIMESTAMP, nullable=False),
        sa.Column('thread_id', sa.String(255), nullable=True),
        sa.Column('metadata', postgresql.JSONB, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('user_id', 'platform', 'platform_message_id', name='uq_user_platform_message')
    )
    
    # Create indexes for messages table
    op.create_index('idx_messages_user_timestamp', 'messages', ['user_id', 'timestamp'])
    op.create_index('idx_messages_thread', 'messages', ['thread_id'])
    
    # Create message_analysis table
    op.create_table(
        'message_analysis',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('messages.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('summary', sa.Text, nullable=False),
        sa.Column('intent', sa.String(100), nullable=True),
        sa.Column('priority_score', sa.Float, nullable=False),
        sa.Column('analyzed_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    
    # Create index for message_analysis table
    op.create_index('idx_message_analysis_priority', 'message_analysis', ['priority_score'])
    
    # Create actionable_items table
    op.create_table(
        'actionable_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('messages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('type', sa.String(50), nullable=False),
        sa.Column('description', sa.Text, nullable=False),
        sa.Column('deadline', sa.TIMESTAMP, nullable=True),
        sa.Column('completed', sa.Boolean, nullable=False, server_default=sa.text('FALSE')),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP'))
    )
    
    # Create indexes for actionable_items table
    op.create_index('idx_actionables_user_deadline', 'actionable_items', ['user_id', 'deadline'])
    op.create_index('idx_actionables_completed', 'actionable_items', ['user_id', 'completed'])
    
    # Create smart_replies table
    op.create_table(
        'smart_replies',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('message_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('messages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('draft_content', sa.Text, nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('reviewed_at', sa.TIMESTAMP, nullable=True),
        sa.Column('sent_at', sa.TIMESTAMP, nullable=True)
    )
    
    # Create indexes for smart_replies table
    op.create_index('idx_smart_replies_user_status', 'smart_replies', ['user_id', 'status'])
    
    # Create user_persona table
    op.create_table(
        'user_persona',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text('gen_random_uuid()')),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('memory_key', sa.String(255), nullable=False),
        sa.Column('memory_value', postgresql.JSONB, nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP, nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.UniqueConstraint('user_id', 'memory_key', name='uq_user_memory_key')
    )


def downgrade() -> None:
    op.drop_table('user_persona')
    op.drop_index('idx_smart_replies_user_status', table_name='smart_replies')
    op.drop_table('smart_replies')
    op.drop_index('idx_actionables_completed', table_name='actionable_items')
    op.drop_index('idx_actionables_user_deadline', table_name='actionable_items')
    op.drop_table('actionable_items')
    op.drop_index('idx_message_analysis_priority', table_name='message_analysis')
    op.drop_table('message_analysis')
    op.drop_index('idx_messages_thread', table_name='messages')
    op.drop_index('idx_messages_user_timestamp', table_name='messages')
    op.drop_table('messages')
    op.drop_table('platform_connections')
    op.drop_table('users')
