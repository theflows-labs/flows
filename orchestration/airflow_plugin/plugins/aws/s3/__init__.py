"""
AWS S3 Plugin for Airflow.

This plugin provides operators and hooks for interacting with Amazon S3.

Available Operators:
    - S3CopyObjectOperatorFactory: Copy objects between S3 buckets
    - S3DeleteObjectsOperatorFactory: Delete multiple objects from S3
    - S3PutObjectOperatorFactory: Upload objects to S3
    - S3ListOperatorFactory: List objects in an S3 bucket

Available Hooks:
    - S3Hook: Base hook for S3 operations

Example Usage:
    ```python
    from plugins.aws.s3 import S3CopyObjectOperatorFactory
    
    # Create a task configuration
    task_config = {
        "task_id": "copy_s3_file",
        "task_type": "s3_copy",
        "config_details": {
            "source_bucket_key": "path/to/source/file.txt",
            "dest_bucket_key": "path/to/destination/file.txt",
            "source_bucket_name": "my-source-bucket",
            "dest_bucket_name": "my-dest-bucket"
        }
    }
    ```

For detailed parameter documentation, see the individual operator factory classes.
"""

from flows.plugins.aws.s3.operators.s3_operations import (
    S3CopyObjectOperatorFactory,
    S3DeleteObjectsOperatorFactory,
    S3PutObjectOperatorFactory,
    S3ListOperatorFactory
)
#from plugins.aws.s3.hooks.s3_hook import S3Hook

# Export operators and hooks
__all__ = [
    'S3CopyObjectOperatorFactory',
    'S3DeleteObjectsOperatorFactory',
    'S3PutObjectOperatorFactory',
    'S3ListOperatorFactory',
    'S3Hook'
]

# Export task types
TASK_TYPES = {
    's3_copy': S3CopyObjectOperatorFactory.TASK_TYPE,
    's3_delete': S3DeleteObjectsOperatorFactory.TASK_TYPE,
    's3_put': S3PutObjectOperatorFactory.TASK_TYPE,
    's3_list': S3ListOperatorFactory.TASK_TYPE
}

# Export operator factories
OPERATOR_FACTORIES = {
    S3CopyObjectOperatorFactory.TASK_TYPE: S3CopyObjectOperatorFactory,
    S3DeleteObjectsOperatorFactory.TASK_TYPE: S3DeleteObjectsOperatorFactory,
    S3PutObjectOperatorFactory.TASK_TYPE: S3PutObjectOperatorFactory,
    S3ListOperatorFactory.TASK_TYPE: S3ListOperatorFactory
}
