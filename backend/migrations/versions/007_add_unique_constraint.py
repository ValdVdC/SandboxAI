"""add unique constraint to prompt_version

Revision ID: 007_add_unique_constraint
Revises: 006_add_human_override_flag
Create Date: 2026-05-25 00:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "007_add_unique_constraint"
down_revision = "006_add_human_override_flag"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Deduplicate existing duplicate (prompt_id, version) pairs
    conn = op.get_bind()
    from sqlalchemy import text

    conn.execute(
        text(
            """
        DELETE FROM prompt_versions
        WHERE id IN (
            SELECT id
            FROM (
                SELECT id,
                ROW_NUMBER() OVER( PARTITION BY prompt_id, version ORDER BY created_at DESC ) as row_num
                FROM prompt_versions
            ) t
            WHERE t.row_num > 1
        )
        """
        )
    )
    op.create_unique_constraint("uq_prompt_version", "prompt_versions", ["prompt_id", "version"])


def downgrade() -> None:
    op.drop_constraint("uq_prompt_version", "prompt_versions", type_="unique")
