"""create task type table

Revision ID: 20240324
Revises: 20240323
Create Date: 2024-03-24 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '20240324'
down_revision = '20240323'  # Points to the previous migration
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'task_type',
        sa.Column('type_id', sa.BigInteger, primary_key=True),
        sa.Column('name', sa.Text, nullable=False),
        sa.Column('type_key', sa.Text, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('plugin_source', sa.Text, nullable=False),
        sa.Column('config_schema', JSONB, nullable=False),
        sa.Column('default_config', JSONB),
        sa.Column('icon', sa.Text),
        sa.Column('created_dt', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_dt', sa.DateTime, nullable=False, server_default=sa.text('now()')),
        sa.Column('is_active', sa.Boolean, nullable=False, server_default='true'),
        
        # Constraints
        sa.UniqueConstraint('type_key', name='uq_task_type_type_key'),
        
        # Schema
        schema='theflows'
    )
    
    # Add indexes
    op.create_index(
        'idx_task_type_type_key',
        'task_type',
        ['type_key'],
        unique=True,
        schema='theflows'
    )
    
    op.create_index(
        'idx_task_type_plugin_source',
        'task_type',
        ['plugin_source'],
        schema='theflows'
    )
    
    op.create_index(
        'idx_task_type_is_active',
        'task_type',
        ['is_active'],
        schema='theflows'
    )
    
    # Add initial task types
    op.execute("""
    INSERT INTO theflows.task_type (
        name, 
        type_key, 
        description, 
        plugin_source, 
        config_schema, 
        default_config, 
        icon
    ) VALUES 
    (
        'PythonOperator',
        'python',
        'Execute a Python callable',
        'airflow',
        '{
            "type": "object",
            "properties": {
                "python_callable": {
                    "type": "string",
                    "description": "Python callable to execute"
                },
                "op_args": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Positional arguments for the callable"
                },
                "op_kwargs": {
                    "type": "object",
                    "description": "Keyword arguments for the callable"
                }
            },
            "required": ["python_callable"]
        }',
        '{"op_args": [], "op_kwargs": {}}',
        'python'
    ),
    (
        'BashOperator',
        'bash',
        'Execute a Bash command',
        'airflow',
        '{
            "type": "object",
            "properties": {
                "bash_command": {
                    "type": "string",
                    "description": "Bash command to execute"
                },
                "env": {
                    "type": "object",
                    "description": "Environment variables"
                }
            },
            "required": ["bash_command"]
        }',
        '{"env": {}}',
        'terminal'
    ),
    (
        'SQLOperator',
        'sql',
        'Execute a SQL query',
        'airflow',
        '{
            "type": "object",
            "properties": {
                "sql": {
                    "type": "string",
                    "description": "SQL query to execute"
                },
                "conn_id": {
                    "type": "string",
                    "description": "Connection ID to use"
                },
                "parameters": {
                    "type": "object",
                    "description": "Query parameters"
                }
            },
            "required": ["sql", "conn_id"]
        }',
        '{"parameters": {}}',
        'database'
    ),
    (
        'HTTPOperator',
        'http',
        'Execute an HTTP request',
        'airflow',
        '{
            "type": "object",
            "properties": {
                "endpoint": {
                    "type": "string",
                    "description": "URL endpoint"
                },
                "method": {
                    "type": "string",
                    "enum": ["GET", "POST", "PUT", "DELETE", "PATCH"],
                    "description": "HTTP method"
                },
                "headers": {
                    "type": "object",
                    "description": "Request headers"
                },
                "data": {
                    "type": "object",
                    "description": "Request data"
                }
            },
            "required": ["endpoint"]
        }',
        '{"method": "GET", "headers": {}, "data": {}}',
        'http'
    )
    """)


def downgrade():
    op.drop_table('task_type', schema='theflows') 