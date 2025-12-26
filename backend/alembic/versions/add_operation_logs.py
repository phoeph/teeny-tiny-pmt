"""add operation logs table

Revision ID: add_operation_logs
Revises: fix_creator_id_not_null
Create Date: 2024-12-25 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_operation_logs'
down_revision = 'fix_creator_id_not_null'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'operation_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('operation_type', sa.String(length=50), nullable=False),
        sa.Column('entity_type', sa.String(length=20), nullable=False),
        sa.Column('entity_id', sa.Integer(), nullable=False),
        sa.Column('operation_content', sa.Text(), nullable=False),
        sa.Column('result_status', sa.String(length=20), nullable=False),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("entity_type IN ('project', 'work_item', 'job', 'comment')", name='valid_operation_log_entity_type'),
        sa.CheckConstraint("result_status IN ('success', 'failure')", name='valid_operation_log_result_status')
    )
    op.create_index('idx_operation_logs_entity', 'operation_logs', ['entity_type', 'entity_id'])
    op.create_index('idx_operation_logs_user', 'operation_logs', ['user_id'])
    op.create_index('idx_operation_logs_created', 'operation_logs', ['created_at'])


def downgrade() -> None:
    op.drop_index('idx_operation_logs_created', table_name='operation_logs')
    op.drop_index('idx_operation_logs_user', table_name='operation_logs')
    op.drop_index('idx_operation_logs_entity', table_name='operation_logs')
    op.drop_table('operation_logs')