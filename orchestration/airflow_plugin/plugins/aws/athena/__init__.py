"""
AWS Athena Plugin for Airflow.

This plugin provides operators and hooks for interacting with Amazon Athena.

Available Operators:
    - AthenaQueryOperatorFactory: Execute SQL queries in Athena

Available Hooks:
    - AthenaHook: Base hook for Athena operations

Example Usage:
    ```python
    from plugins.aws.athena import AthenaQueryOperatorFactory
    
    # Create a task configuration
    task_config = {
        "task_id": "run_athena_query",
        "task_type": "athena_query",
        "config_details": {
            "query": "SELECT * FROM my_table LIMIT 10",
            "database": "my_database",
            "output_location": "s3://my-bucket/query-results/"
        }
    }
    ```

For detailed parameter documentation, see the individual operator factory classes.
"""

from orchestration.airflow_plugin.plugins.aws.athena.operators.athena_query import AthenaQueryOperatorFactory
#from flows.plugins.aws.athena.hooks.athena_hook import AthenaHook

# Export operators and hooks
__all__ = [
    'AthenaQueryOperatorFactory',
    'AthenaHook'
]

# Export task types
TASK_TYPES = {
    'athena_query': AthenaQueryOperatorFactory.TASK_TYPE
}

# Export operator factories
OPERATOR_FACTORIES = {
    AthenaQueryOperatorFactory.TASK_TYPE: AthenaQueryOperatorFactory
}
