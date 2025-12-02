"""add spam detection fields

Revision ID: 004
Revises: 003
Create Date: 2024-12-01 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add spam detection fields to message_analysis table
    op.add_column('message_analysis', sa.Column('is_spam', sa.Boolean(), nullable=True))
    op.add_column('message_analysis', sa.Column('spam_score', sa.Float(), nullable=True))
    op.add_column('message_analysis', sa.Column('spam_type', sa.String(50), nullable=True))
    op.add_column('message_analysis', sa.Column('unsubscribe_link', sa.Text(), nullable=True))
    
    # Set default values for existing records
    op.execute("UPDATE message_analysis SET is_spam = false WHERE is_spam IS NULL")
    op.execute("UPDATE message_analysis SET spam_score = 0.0 WHERE spam_score IS NULL")
    op.execute("UPDATE message_analysis SET spam_type = 'none' WHERE spam_type IS NULL")
    
    # Make fields non-nullable after setting defaults
    op.alter_column('message_analysis', 'is_spam', nullable=False)
    op.alter_column('message_analysis', 'spam_score', nullable=False)
    op.alter_column('message_analysis', 'spam_type', nullable=False)


def downgrade() -> None:
    # Remove spam detection fields
    op.drop_column('message_analysis', 'unsubscribe_link')
    op.drop_column('message_analysis', 'spam_type')
    op.drop_column('message_analysis', 'spam_score')
    op.drop_column('message_analysis', 'is_spam')
