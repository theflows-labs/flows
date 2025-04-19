"""add execution tables

Revision ID: 20240323
Revises: merged_20240322
Create Date: 2024-03-23 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240323'
down_revision = 'merged_20240322'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create flow_execution table
    op.create_table(
        'flow_execution',
        sa.Column('execution_id', sa.BigInteger(), primary_key=True),
        sa.Column('flow_config_id', sa.BigInteger(), sa.ForeignKey('theflows.flow_configuration.config_id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='PENDING'),
        sa.Column('start_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('result', postgresql.JSONB(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('logs', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        schema='theflows'
    )

    # Create task_execution table
    op.create_table(
        'task_execution',
        sa.Column('task_execution_id', sa.BigInteger(), primary_key=True),
        sa.Column('flow_execution_id', sa.BigInteger(), sa.ForeignKey('theflows.flow_execution.execution_id', ondelete='CASCADE'), nullable=False),
        sa.Column('task_id', sa.BigInteger(), sa.ForeignKey('theflows.task_configuration.task_id', ondelete='CASCADE'), nullable=False),
        sa.Column('status', sa.String(), nullable=False, server_default='PENDING'),
        sa.Column('start_time', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('end_time', sa.DateTime(), nullable=True),
        sa.Column('result', postgresql.JSONB(), nullable=True),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('logs', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        schema='theflows'
    )

    # Create indexes
    op.create_index(
        'idx_flow_execution_flow_config',
        'flow_execution',
        ['flow_config_id'],
        schema='theflows'
    )

    op.create_index(
        'idx_flow_execution_status',
        'flow_execution',
        ['status'],
        schema='theflows'
    )

    op.create_index(
        'idx_task_execution_flow_execution',
        'task_execution',
        ['flow_execution_id'],
        schema='theflows'
    )

    op.create_index(
        'idx_task_execution_task',
        'task_execution',
        ['task_id'],
        schema='theflows'
    )

    op.create_index(
        'idx_task_execution_status',
        'task_execution',
        ['status'],
        schema='theflows'
    )

    # Create sequences for IDs
    op.execute('CREATE SEQUENCE IF NOT EXISTS theflows.flow_execution_execution_id_seq')
    op.execute('CREATE SEQUENCE IF NOT EXISTS theflows.task_execution_task_execution_id_seq')

    # Set sequence ownership
    op.execute('ALTER SEQUENCE theflows.flow_execution_execution_id_seq OWNED BY theflows.flow_execution.execution_id')
    op.execute('ALTER SEQUENCE theflows.task_execution_task_execution_id_seq OWNED BY theflows.task_execution.task_execution_id')

    # Set default values for ID columns from sequences
    op.alter_column('flow_execution', 'execution_id',
                    server_default=sa.text("nextval('theflows.flow_execution_execution_id_seq')"),
                    schema='theflows')
    op.alter_column('task_execution', 'task_execution_id',
                    server_default=sa.text("nextval('theflows.task_execution_task_execution_id_seq')"),
                    schema='theflows')


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_task_execution_status', table_name='task_execution', schema='theflows')
    op.drop_index('idx_task_execution_task', table_name='task_execution', schema='theflows')
    op.drop_index('idx_task_execution_flow_execution', table_name='task_execution', schema='theflows')
    op.drop_index('idx_flow_execution_status', table_name='flow_execution', schema='theflows')
    op.drop_index('idx_flow_execution_flow_config', table_name='flow_execution', schema='theflows')

    # Drop tables
    op.drop_table('task_execution', schema='theflows')
    op.drop_table('flow_execution', schema='theflows')

    # Drop sequences
    op.execute('DROP SEQUENCE IF EXISTS theflows.task_execution_task_execution_id_seq')
    op.execute('DROP SEQUENCE IF EXISTS theflows.flow_execution_execution_id_seq') 