"""add unique constraint to prompt_version

Revision ID: 111111111111
Revises: 94bd77c5d6e7
Create Date: 2026-05-25 00:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "111111111111"
down_revision = "94bd77c5d6e7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(
        "uq_prompt_version", "prompt_versions", ["prompt_id", "version"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_prompt_version", "prompt_versions", type_="unique")
