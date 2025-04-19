"""Merged schema creation with flow configuration

Revision ID: merged_20240322
Revises: 
Create Date: 2024-03-22 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'merged_20240322'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    print("Starting upgrade...")
    
    # Create theflows schema
    print("Creating theflows schema...")
    op.execute('CREATE SCHEMA IF NOT EXISTS theflows')
    print("Schema created!")

    # Create sequences
    print("Creating sequences...")
    op.execute('CREATE SEQUENCE IF NOT EXISTS theflows.flow_configuration_config_id_seq')
    op.execute('CREATE SEQUENCE IF NOT EXISTS theflows.task_configuration_task_id_seq')
    print("Sequences created!")

    # Create flow_configuration table (renamed from dag_configuration)
    print("Creating flow_configuration table...")
    op.create_table(
        'flow_configuration',
        sa.Column('config_id', sa.BigInteger(), server_default=sa.text("nextval('theflows.flow_configuration_config_id_seq')"), nullable=False),
        sa.Column('flow_id', sa.Text(), nullable=False),
        sa.Column('config_details', postgresql.JSONB(), nullable=True),  # Changed to JSONB
        sa.Column('config_details_yaml', sa.Text(), nullable=True),  # Added YAML column
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_dt', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_dt', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        schema='theflows',
        comment='Configuration for Flows'
    )
    print("Flow configuration table created!")

    # Create task_configuration table
    print("Creating task_configuration table...")
    op.create_table(
        'task_configuration',
        sa.Column('task_id', sa.BigInteger(), server_default=sa.text("nextval('theflows.task_configuration_task_id_seq')"), nullable=False),
        sa.Column('task_type', sa.Text(), nullable=False),
        sa.Column('flow_config_id', sa.BigInteger(), nullable=False),
        sa.Column('task_sequence', sa.Integer(), nullable=False),
        sa.Column('config_details', postgresql.JSONB(), nullable=True),  # Changed to JSONB
        sa.Column('config_details_yaml', sa.Text(), nullable=True),  # Added YAML column
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_dt', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_dt', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        schema='theflows',
        comment='Configuration for tasks'
    )
    print("Task configuration table created!")

    # Create task_dependency table
    print("Creating task_dependency table...")
    op.create_table(
        'task_dependency',
        sa.Column('dependency_id', sa.BigInteger(), sa.Identity(), nullable=False),
        sa.Column('flow_config_id', sa.BigInteger(), nullable=False),
        sa.Column('task_id', sa.BigInteger(), nullable=False),
        sa.Column('depends_on_task_id', sa.BigInteger(), nullable=False),
        sa.Column('dependency_type', sa.Text(), nullable=False),
        sa.Column('condition', sa.Text(), nullable=True),
        sa.Column('created_dt', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_dt', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        schema='theflows'
    )
    print("Task dependency table created!")

    # Create primary key constraints
    print("Creating primary key constraints...")
    op.create_primary_key('flow_configuration_pkey', 'flow_configuration', ['config_id'], schema='theflows')
    op.create_primary_key('task_configuration_pkey', 'task_configuration', ['task_id'], schema='theflows')
    op.create_primary_key('task_dependency_pkey', 'task_dependency', ['dependency_id'], schema='theflows')
    print("Primary key constraints created!")

    # Create unique constraints
    print("Creating unique constraints...")
    op.create_unique_constraint('flow_configuration_flow_id_key', 'flow_configuration', ['flow_id'], schema='theflows')
    op.create_unique_constraint('task_dependency_unique', 'task_dependency', ['flow_config_id', 'task_id', 'depends_on_task_id'], schema='theflows')
    print("Unique constraints created!")

    # Create foreign key constraints
    print("Creating foreign key constraints...")
    op.create_foreign_key(
        'task_configuration_flow_config_id_fkey',
        'task_configuration', 'flow_configuration',
        ['flow_config_id'], ['config_id'],
        source_schema='theflows', referent_schema='theflows',
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'task_dependency_flow_config_id_fkey',
        'task_dependency', 'flow_configuration',
        ['flow_config_id'], ['config_id'],
        source_schema='theflows', referent_schema='theflows',
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'task_dependency_task_id_fkey',
        'task_dependency', 'task_configuration',
        ['task_id'], ['task_id'],
        source_schema='theflows', referent_schema='theflows',
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'task_dependency_depends_on_task_id_fkey',
        'task_dependency', 'task_configuration',
        ['depends_on_task_id'], ['task_id'],
        source_schema='theflows', referent_schema='theflows',
        ondelete='CASCADE'
    )
    print("Foreign key constraints created!")

    # Create indexes for task_dependency
    print("Creating indexes...")
    op.create_index('idx_task_dependency_flow_config', 'task_dependency', ['flow_config_id'], schema='theflows')
    op.create_index('idx_task_dependency_task', 'task_dependency', ['task_id'], schema='theflows')
    op.create_index('idx_task_dependency_depends_on', 'task_dependency', ['depends_on_task_id'], schema='theflows')
    print("Indexes created!")

    print("Upgrade completed successfully!")


def downgrade() -> None:
    print("Starting downgrade...")
    
    # Drop indexes
    print("Dropping indexes...")
    op.drop_index('idx_task_dependency_depends_on', table_name='task_dependency', schema='theflows')
    op.drop_index('idx_task_dependency_task', table_name='task_dependency', schema='theflows')
    op.drop_index('idx_task_dependency_flow_config', table_name='task_dependency', schema='theflows')
    
    # Drop tables
    print("Dropping tables...")
    op.drop_table('task_dependency', schema='theflows')
    op.drop_table('task_configuration', schema='theflows')
    op.drop_table('flow_configuration', schema='theflows')
    print("Tables dropped!")
    
    # Drop sequences
    print("Dropping sequences...")
    op.execute('DROP SEQUENCE IF EXISTS theflows.task_configuration_task_id_seq')
    op.execute('DROP SEQUENCE IF EXISTS theflows.flow_configuration_config_id_seq')
    print("Sequences dropped!")
    
    # Drop schema
    print("Dropping schema...")
    op.execute('DROP SCHEMA IF EXISTS theflows')
    print("Schema dropped!")
    
    print("Downgrade completed successfully!") 