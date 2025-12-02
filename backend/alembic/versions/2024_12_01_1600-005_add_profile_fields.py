"""add profile fields

Revision ID: 005
Revises: 004
Create Date: 2024-12-01 16:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add profile fields to users table
    op.add_column('users', sa.Column('phone', sa.String(50), nullable=True))
    op.add_column('users', sa.Column('location', sa.String(255), nullable=True))
    op.add_column('users', sa.Column('timezone', sa.String(100), nullable=True))
    op.add_column('users', sa.Column('website', sa.String(255), nullable=True))


def downgrade() -> None:
    # Remove profile fields from users table
    op.drop_column('users', 'website')
    op.drop_column('users', 'timezone')
    op.drop_column('users', 'location')
    op.drop_column('users', 'phone')
