"""Add batch_id to test_results

Revision ID: 004_add_batch_id_to_test_results
Revises: 003_expand_users_hashed_password
Create Date: 2026-04-04 18:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "004_add_batch_id_to_test_results"
down_revision = "003_expand_users_hashed_password"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add batch_id column to test_results table
    op.add_column("test_results", sa.Column("batch_id", sa.UUID(), nullable=True))
    # Create index for better performance when grouping by batch
    op.create_index(op.f("ix_test_results_batch_id"), "test_results", ["batch_id"], unique=False)


def downgrade() -> None:
    # Remove index and column
    op.drop_index(op.f("ix_test_results_batch_id"), table_name="test_results")
    op.drop_column("test_results", "batch_id")
