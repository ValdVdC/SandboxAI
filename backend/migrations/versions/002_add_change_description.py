"""Add change_description column to prompt_versions table

Revision ID: 002_add_change_description
Revises: 001_initial
Create Date: 2024-03-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_add_change_description'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add change_description column to prompt_versions table
    op.add_column(
        'prompt_versions',
        sa.Column('change_description', sa.Text(), nullable=True)
    )


def downgrade() -> None:
    # Remove change_description column from prompt_versions table
    op.drop_column('prompt_versions', 'change_description')
