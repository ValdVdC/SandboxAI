"""Add score and is_correct to test_results

Revision ID: 005_add_validation_fields
Revises: 004_add_batch_id_to_test_results
Create Date: 2026-05-09 10:00:00.000000

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "005_add_validation_fields"
down_revision = "004_add_batch_id_to_test_results"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add validation columns to test_results table
    op.add_column(
        "test_results",
        sa.Column("score", sa.Numeric(precision=3, scale=2), nullable=True),
    )
    op.add_column("test_results", sa.Column("is_correct", sa.Boolean(), nullable=True))


def downgrade() -> None:
    # Remove columns
    op.drop_column("test_results", "is_correct")
    op.drop_column("test_results", "score")
