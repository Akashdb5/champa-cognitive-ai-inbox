"""add hashed_password to users

Revision ID: 002
Revises: 001
Create Date: 2024-11-29 14:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add hashed_password column
    op.add_column('users', sa.Column('hashed_password', sa.String(255), nullable=True))
    
    # Make auth0_id nullable
    op.alter_column('users', 'auth0_id', nullable=True)


def downgrade() -> None:
    # Remove hashed_password column
    op.drop_column('users', 'hashed_password')
    
    # Make auth0_id not nullable again
    op.alter_column('users', 'auth0_id', nullable=False)
