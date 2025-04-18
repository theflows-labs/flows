"""create task dependencies table

Revision ID: 20240321
Revises: 5f2621c13b39
Create Date: 2024-03-21 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240321'
down_revision = '5f2621c13b39'
branch_labels = None
depends_on = None

def upgrade():
    # Create task_dependency table
    op.execute("""
        CREATE TABLE IF NOT EXISTS theflows.task_dependency (
            dependency_id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            dag_config_id BIGINT NOT NULL REFERENCES theflows.dag_configuration(config_id) ON DELETE CASCADE,
            task_id BIGINT NOT NULL REFERENCES theflows.task_configuration(task_id) ON DELETE CASCADE,
            depends_on_task_id BIGINT NOT NULL REFERENCES theflows.task_configuration(task_id) ON DELETE CASCADE,
            dependency_type TEXT NOT NULL,  -- e.g., 'success', 'failure', 'skip', 'all_done'
            condition TEXT,  -- Optional condition for the dependency
            created_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_dt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            UNIQUE(dag_config_id, task_id, depends_on_task_id)
        )
    """)

    # Create index for faster lookups
    op.execute("""
        CREATE INDEX idx_task_dependency_dag_config 
        ON theflows.task_dependency(dag_config_id)
    """)

    op.execute("""
        CREATE INDEX idx_task_dependency_task 
        ON theflows.task_dependency(task_id)
    """)

    op.execute("""
        CREATE INDEX idx_task_dependency_depends_on 
        ON theflows.task_dependency(depends_on_task_id)
    """)

def downgrade():
    # Drop indexes first
    op.execute("DROP INDEX IF EXISTS theflows.idx_task_dependency_depends_on")
    op.execute("DROP INDEX IF EXISTS theflows.idx_task_dependency_task")
    op.execute("DROP INDEX IF EXISTS theflows.idx_task_dependency_dag_config")
    
    # Drop the table
    op.execute("DROP TABLE IF EXISTS theflows.task_dependency") 