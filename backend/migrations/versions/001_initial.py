"""Create initial schema with users, prompts, prompt_versions, and test_results tables

Revision ID: 001_initial
Revises: 
Create Date: 2024-03-21 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email', name='uq_users_email'),
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create prompts table
    op.create_table(
        'prompts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('version_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_prompts_user_id'), 'prompts', ['user_id'])

    # Create prompt_versions table
    op.create_table(
        'prompt_versions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('prompt_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('provider', sa.String(50), nullable=False),
        sa.Column('model', sa.String(100), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['prompt_id'], ['prompts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_prompt_versions_prompt_id'), 'prompt_versions', ['prompt_id'])

    # Create test_results table
    op.create_table(
        'test_results',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('version_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('input', sa.Text(), nullable=False),
        sa.Column('output', sa.Text(), nullable=True),
        sa.Column('expected', sa.Text(), nullable=True),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Numeric(precision=10, scale=6), nullable=True, server_default='0.0'),
        sa.Column('status', sa.String(50), nullable=False, server_default='pending'),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['version_id'], ['prompt_versions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_test_results_version_id'), 'test_results', ['version_id'])


def downgrade() -> None:
    op.drop_index(op.f('ix_test_results_version_id'), table_name='test_results')
    op.drop_table('test_results')
    op.drop_index(op.f('ix_prompt_versions_prompt_id'), table_name='prompt_versions')
    op.drop_table('prompt_versions')
    op.drop_index(op.f('ix_prompts_user_id'), table_name='prompts')
    op.drop_table('prompts')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
