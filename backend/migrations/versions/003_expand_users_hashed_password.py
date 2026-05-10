"""Expand users.hashed_password column length

Revision ID: 003_expand_users_hashed_password
Revises: 002_add_change_description
Create Date: 2026-03-25 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "003_expand_users_hashed_password"
down_revision = "002_add_change_description"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=255),
        type_=sa.String(length=512),
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "users",
        "hashed_password",
        existing_type=sa.String(length=512),
        type_=sa.String(length=255),
        existing_nullable=False,
    )
