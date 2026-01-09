"""add is_active to users table

Revision ID: a1b2c3d4e5f
Revises: 44ebbb4b3b9e
Create Date: 2026-01-04 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f'
down_revision = '44ebbb4b3b9e'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add is_active column to users table with default True for existing rows
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')))
    # Remove server_default so future inserts rely on SQLAlchemy model default
    op.alter_column('users', 'is_active', server_default=None)


def downgrade() -> None:
    op.drop_column('users', 'is_active')
