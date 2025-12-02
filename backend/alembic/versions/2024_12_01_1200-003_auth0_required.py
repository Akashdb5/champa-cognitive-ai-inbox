"""make auth0_id required for Auth0-only authentication

Revision ID: 003
Revises: 002
Create Date: 2024-12-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Set a default auth0_id for existing users without one
    op.execute("UPDATE users SET auth0_id = 'migrated_' || id::text WHERE auth0_id IS NULL")
    
    # Make auth0_id NOT NULL
    op.alter_column('users', 'auth0_id',
                    existing_type=sa.String(255),
                    nullable=False)


def downgrade() -> None:
    # Make auth0_id nullable again
    op.alter_column('users', 'auth0_id',
                    existing_type=sa.String(255),
                    nullable=True)
