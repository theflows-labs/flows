"""Create theflows schema and initial tables

Revision ID: 5f2621c13b39
Revises: 
Create Date: 2024-03-20 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '5f2621c13b39'
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
    op.execute('CREATE SEQUENCE IF NOT EXISTS theflows.dag_configuration_config_id_seq')
    op.execute('CREATE SEQUENCE IF NOT EXISTS theflows.task_configuration_task_id_seq')
    print("Sequences created!")

    # Create dag_configuration table
    print("Creating dag_configuration table...")
    op.create_table(
        'dag_configuration',
        sa.Column('config_id', sa.BigInteger(), server_default=sa.text("nextval('theflows.dag_configuration_config_id_seq')"), nullable=False),
        sa.Column('dag_id', sa.Text(), nullable=False),
        sa.Column('config_details', postgresql.JSON(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_dt', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_dt', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        schema='theflows',
        comment='Configuration for DAGs'
    )
    print("DAG configuration table created!")

    # Create task_configuration table
    print("Creating task_configuration table...")
    op.create_table(
        'task_configuration',
        sa.Column('task_id', sa.BigInteger(), server_default=sa.text("nextval('theflows.task_configuration_task_id_seq')"), nullable=False),
        sa.Column('task_type', sa.Text(), nullable=False),
        sa.Column('dag_config_id', sa.BigInteger(), nullable=False),
        sa.Column('task_sequence', sa.Integer(), nullable=False),
        sa.Column('config_details', postgresql.JSON(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_dt', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_dt', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=True),
        schema='theflows',
        comment='Configuration for tasks'
    )
    print("Task configuration table created!")

    # Create primary key constraints
    print("Creating primary key constraints...")
    op.create_primary_key('dag_configuration_pkey', 'dag_configuration', ['config_id'], schema='theflows')
    op.create_primary_key('task_configuration_pkey', 'task_configuration', ['task_id'], schema='theflows')
    print("Primary key constraints created!")

    # Create unique constraint for dag_id
    print("Creating unique constraint for dag_id...")
    op.create_unique_constraint('dag_configuration_dag_id_key', 'dag_configuration', ['dag_id'], schema='theflows')
    print("Unique constraint created!")

    # Create foreign key constraint for dag_config_id
    print("Creating foreign key constraint for dag_config_id...")
    op.execute('''
        ALTER TABLE theflows.task_configuration 
        ADD CONSTRAINT task_configuration_dag_config_id_fkey 
        FOREIGN KEY (dag_config_id) 
        REFERENCES theflows.dag_configuration(config_id) 
        ON DELETE CASCADE
    ''')
    print("Foreign key constraint created!")

    print("Upgrade completed successfully!")


def downgrade() -> None:
    print("Starting downgrade...")
    
    # Drop constraints first
    print("Dropping constraints...")
    op.execute('ALTER TABLE theflows.task_configuration DROP CONSTRAINT IF EXISTS task_configuration_dag_config_id_fkey')
    op.drop_constraint('dag_configuration_dag_id_key', 'dag_configuration', schema='theflows')
    
    # Drop tables
    print("Dropping tables...")
    op.drop_table('task_configuration', schema='theflows')
    op.drop_table('dag_configuration', schema='theflows')
    print("Tables dropped!")
    
    # Drop sequences
    print("Dropping sequences...")
    op.execute('DROP SEQUENCE IF EXISTS theflows.task_configuration_task_id_seq')
    op.execute('DROP SEQUENCE IF EXISTS theflows.dag_configuration_config_id_seq')
    print("Sequences dropped!")
    
    # Drop schema
    print("Dropping schema...")
    op.execute('DROP SCHEMA IF EXISTS theflows')
    print("Schema dropped!")
    
    print("Downgrade completed successfully!") 