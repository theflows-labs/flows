"""
Operator factories for S3 operations.
"""
from typing import Dict, Any, Type, List
import json
import logging

from airflow.models import BaseOperator
from airflow.providers.amazon.aws.operators.s3 import (
    S3CopyObjectOperator,
    S3DeleteObjectsOperator,
    S3CreateObjectOperator,
    S3ListOperator
)

from orchestration.airflow_plugin.plugin_core.dag_builder.base import OperatorFactory
from core.models import TaskConfiguration

logger = logging.getLogger(__name__)

class S3CopyObjectOperatorFactory(OperatorFactory):
    """Factory for S3 copy operations."""
    
    TASK_TYPE = "s3_copy"
    
    @classmethod
    def get_operator_class(cls, task_type: str) -> Type[BaseOperator]:
        if task_type == cls.TASK_TYPE:
            return S3CopyObjectOperator
        raise ValueError(f"Unknown task type: {task_type}")
    
    def create_operator(self, task_id: str, config: Dict[str, Any], dag: Any) -> BaseOperator:
        return S3CopyObjectOperator(
            task_id=task_id,
            dag=dag,
            **config
        )

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "source_bucket_key": {
                    "type": "string",
                    "description": "Source S3 key"
                },
                "dest_bucket_key": {
                    "type": "string",
                    "description": "Destination S3 key"
                },
                "source_bucket_name": {
                    "type": "string",
                    "description": "Source bucket name"
                },
                "dest_bucket_name": {
                    "type": "string",
                    "description": "Destination bucket name"
                },
                "aws_conn_id": {
                    "type": "string",
                    "description": "AWS connection ID",
                    "default": "aws_default"
                }
            },
            "required": cls.get_required_parameters()
        }

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        return {
            "aws_conn_id": "aws_default"
        }

    @classmethod
    def get_icon(cls) -> str:
        return 's3'

    @classmethod
    def get_required_parameters(cls) -> List[str]:
        return [
            "source_bucket_key",
            "dest_bucket_key",
            "source_bucket_name",
            "dest_bucket_name"
        ]


class S3DeleteObjectsOperatorFactory(OperatorFactory):
    """Factory for creating S3 delete objects operators."""
    
    TASK_TYPE = "s3_delete"
    
    @classmethod
    def get_operator_class(cls, task_type: str) -> Type[BaseOperator]:
        """
        Get the operator class for a task type.
        
        Args:
            task_type: The task type identifier
            
        Returns:
            The operator class
        """
        if task_type == cls.TASK_TYPE:
            return S3DeleteObjectsOperator
        raise ValueError(f"Unknown task type: {task_type}")
    
    def create_operator(self, task_config: TaskConfiguration, dag) -> BaseOperator:
        """
        Create an S3 delete objects operator from task configuration.
        
        Args:
            task_config: The task configuration
            dag: The DAG instance
            
        Returns:
            An S3 delete objects operator instance
        """
        # Parse task configuration
        config_details = task_config.config_details
        if isinstance(config_details, str):
            config_details = json.loads(config_details)
        
        # Extract parameters
        bucket = config_details.get("bucket")
        keys = config_details.get("keys", [])
        aws_conn_id = config_details.get("aws_conn_id", "aws_default")
        
        # Create operator
        return S3DeleteObjectsOperator(
            task_id=f"s3_delete_{task_config.task_id}",
            bucket=bucket,
            keys=keys,
            aws_conn_id=aws_conn_id,
            dag=dag
        )

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "bucket": {
                    "type": "string",
                    "description": "S3 bucket name"
                },
                "keys": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of S3 keys to delete"
                },
                "aws_conn_id": {
                    "type": "string",
                    "description": "AWS connection ID",
                    "default": "aws_default"
                }
            },
            "required": cls.get_required_parameters()
        }

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        return {
            "aws_conn_id": "aws_default"
        }

    @classmethod
    def get_icon(cls) -> str:
        return 's3'

    @classmethod
    def get_required_parameters(cls) -> List[str]:
        return ["bucket", "keys"]


class S3PutObjectOperatorFactory(OperatorFactory):
    """Factory for S3 put object operations."""
    
    TASK_TYPE = "s3_put"
    
    @classmethod
    def get_operator_class(cls, task_type: str) -> Type[BaseOperator]:
        return S3CreateObjectOperator

    def create_operator(self, task_id: str, config: Dict[str, Any], dag: Any) -> BaseOperator:
        return self.get_operator_class(self.TASK_TYPE)(
            task_id=task_id,
            dag=dag,
            **config
        )

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "bucket_name": {
                    "type": "string",
                    "description": "S3 bucket name"
                },
                "key": {
                    "type": "string",
                    "description": "S3 object key"
                },
                "data": {
                    "type": "string",
                    "description": "Data to upload"
                },
                "encoding": {
                    "type": "string",
                    "description": "Data encoding",
                    "default": "utf-8"
                },
                "acl_policy": {
                    "type": "string",
                    "description": "S3 ACL policy",
                    "enum": [
                        "private", 
                        "public-read", 
                        "public-read-write", 
                        "authenticated-read",
                        "aws-exec-read",
                        "bucket-owner-read",
                        "bucket-owner-full-control"
                    ]
                },
                "aws_conn_id": {
                    "type": "string",
                    "description": "AWS connection ID",
                    "default": "aws_default"
                },
                "replace": {
                    "type": "boolean",
                    "description": "Whether to replace existing object",
                    "default": False
                }
            },
            "required": cls.get_required_parameters()
        }

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        return {
            "aws_conn_id": "aws_default",
            "encoding": "utf-8",
            "replace": False
        }

    @classmethod
    def get_icon(cls) -> str:
        return 's3'

    @classmethod
    def get_required_parameters(cls) -> List[str]:
        return ["bucket_name", "key", "data"]


class S3ListOperatorFactory(OperatorFactory):
    """Factory for S3 list operations."""
    
    TASK_TYPE = "s3_list"
    
    @classmethod
    def get_operator_class(cls, task_type: str) -> Type[BaseOperator]:
        return S3ListOperator

    def create_operator(self, task_id: str, config: Dict[str, Any], dag: Any) -> BaseOperator:
        return self.get_operator_class(self.TASK_TYPE)(
            task_id=task_id,
            dag=dag,
            **config
        )

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "bucket": {
                    "type": "string",
                    "description": "S3 bucket name"
                },
                "prefix": {
                    "type": "string",
                    "description": "Prefix for listing objects",
                    "default": ""
                },
                "delimiter": {
                    "type": "string",
                    "description": "Delimiter for listing objects",
                    "default": "/"
                },
                "aws_conn_id": {
                    "type": "string",
                    "description": "AWS connection ID",
                    "default": "aws_default"
                },
                "max_items": {
                    "type": "integer",
                    "description": "Maximum number of items to list",
                    "minimum": 1,
                    "default": 1000
                }
            },
            "required": cls.get_required_parameters()
        }

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        return {
            "aws_conn_id": "aws_default",
            "prefix": "",
            "delimiter": "/",
            "max_items": 1000
        }

    @classmethod
    def get_icon(cls) -> str:
        return 's3'

    @classmethod
    def get_required_parameters(cls) -> List[str]:
        return ["bucket"] 