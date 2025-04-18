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
    """Factory for creating S3 copy object operators."""
    
    TASK_TYPE = "s3_copy"
    
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
            return S3CopyObjectOperator
        raise ValueError(f"Unknown task type: {task_type}")
    
    def create_operator(self, task_config: TaskConfiguration, dag) -> BaseOperator:
        """
        Create an S3 copy object operator from task configuration.
        
        Args:
            task_config: The task configuration
            dag: The DAG instance
            
        Returns:
            An S3 copy object operator instance
        """
        config_details = self._parse_config_details(task_config.config_details)
        self._validate_parameters(config_details)
        config_details = self._apply_defaults(config_details)
        
        return self.get_operator_class(task_config.task_type)(
            task_id=f"s3_copy_{task_config.task_id}",
            dag=dag,
            **config_details
        )
    
    @classmethod
    def get_required_parameters(cls) -> List[str]:
        """
        Get the list of required parameters for this operator.
        
        Returns:
            A list of required parameter names
        """
        return ["source_bucket_key", "dest_bucket_key"]
    
    @classmethod
    def get_optional_parameters(cls) -> Dict[str, Any]:
        """
        Get the optional parameters and their default values for this operator.
        
        Returns:
            A dictionary of optional parameter names and their default values
        """
        return {
            "source_bucket_name": None,
            "dest_bucket_name": None,
            "aws_conn_id": "aws_default",
            "verify": None
        }
    
    @classmethod
    def get_parameter_descriptions(cls) -> Dict[str, str]:
        """
        Get descriptions for all parameters of this operator.
        
        Returns:
            A dictionary of parameter names and their descriptions
        """
        return {
            "source_bucket_key": "The key of the source object to copy",
            "dest_bucket_key": "The key of the destination object",
            "source_bucket_name": "Name of the source bucket",
            "dest_bucket_name": "Name of the destination bucket",
            "aws_conn_id": "The Airflow connection ID for AWS credentials",
            "verify": "Whether to verify SSL certificates"
        }
    
    @classmethod
    def get_parameter_types(cls) -> Dict[str, Type]:
        """
        Get the types of all parameters for this operator.
        
        Returns:
            A dictionary of parameter names and their types
        """
        return {
            "source_bucket_key": str,
            "dest_bucket_key": str,
            "source_bucket_name": str,
            "dest_bucket_name": str,
            "aws_conn_id": str,
            "verify": bool
        }
    
    @classmethod
    def get_parameter_examples(cls) -> Dict[str, Any]:
        """
        Get example values for all parameters of this operator.
        
        Returns:
            A dictionary of parameter names and example values
        """
        return {
            "source_bucket_key": "path/to/source/file.txt",
            "dest_bucket_key": "path/to/destination/file.txt",
            "source_bucket_name": "my-source-bucket",
            "dest_bucket_name": "my-dest-bucket",
            "aws_conn_id": "aws_default",
            "verify": True
        }


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


class S3PutObjectOperatorFactory(OperatorFactory):
    """Factory for creating S3 put object operators."""
    
    TASK_TYPE = "s3_put"
    
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
            return S3PutObjectOperator
        raise ValueError(f"Unknown task type: {task_type}")
    
    def create_operator(self, task_config: TaskConfiguration, dag) -> BaseOperator:
        """
        Create an S3 put object operator from task configuration.
        
        Args:
            task_config: The task configuration
            dag: The DAG instance
            
        Returns:
            An S3 put object operator instance
        """
        # Parse task configuration
        config_details = task_config.config_details
        if isinstance(config_details, str):
            config_details = json.loads(config_details)
        
        # Extract parameters
        bucket = config_details.get("bucket")
        key = config_details.get("key")
        data = config_details.get("data", "")
        aws_conn_id = config_details.get("aws_conn_id", "aws_default")
        replace = config_details.get("replace", False)
        
        # Create operator
        return S3PutObjectOperator(
            task_id=f"s3_put_{task_config.task_id}",
            bucket=bucket,
            key=key,
            data=data,
            aws_conn_id=aws_conn_id,
            replace=replace,
            dag=dag
        )


class S3ListOperatorFactory(OperatorFactory):
    """Factory for creating S3 list operators."""
    
    TASK_TYPE = "s3_list"
    
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
            return S3ListOperator
        raise ValueError(f"Unknown task type: {task_type}")
    
    def create_operator(self, task_config: TaskConfiguration, dag) -> BaseOperator:
        """
        Create an S3 list operator from task configuration.
        
        Args:
            task_config: The task configuration
            dag: The DAG instance
            
        Returns:
            An S3 list operator instance
        """
        config_details = self._parse_config_details(task_config.config_details)
        self._validate_parameters(config_details)
        config_details = self._apply_defaults(config_details)
        
        return self.get_operator_class(task_config.task_type)(
            task_id=f"s3_list_{task_config.task_id}",
            dag=dag,
            **config_details
        )
    
    @classmethod
    def get_required_parameters(cls) -> List[str]:
        """
        Get the list of required parameters for this operator.
        
        Returns:
            A list of required parameter names
        """
        return ["bucket"]
    
    @classmethod
    def get_optional_parameters(cls) -> Dict[str, Any]:
        """
        Get the optional parameters and their default values for this operator.
        
        Returns:
            A dictionary of optional parameter names and their default values
        """
        return {
            "prefix": "",
            "delimiter": "",
            "aws_conn_id": "aws_default"
        }
    
    @classmethod
    def get_parameter_descriptions(cls) -> Dict[str, str]:
        """
        Get descriptions for all parameters of this operator.
        
        Returns:
            A dictionary of parameter names and their descriptions
        """
        return {
            "bucket": "Name of the S3 bucket to list",
            "prefix": "Prefix to filter objects",
            "delimiter": "Delimiter to use for object grouping",
            "aws_conn_id": "The Airflow connection ID for AWS credentials"
        }
    
    @classmethod
    def get_parameter_types(cls) -> Dict[str, Type]:
        """
        Get the types of all parameters for this operator.
        
        Returns:
            A dictionary of parameter names and their types
        """
        return {
            "bucket": str,
            "prefix": str,
            "delimiter": str,
            "aws_conn_id": str
        }
    
    @classmethod
    def get_parameter_examples(cls) -> Dict[str, Any]:
        """
        Get example values for all parameters of this operator.
        
        Returns:
            A dictionary of parameter names and example values
        """
        return {
            "bucket": "my-bucket",
            "prefix": "path/to/files/",
            "delimiter": "/",
            "aws_conn_id": "aws_default"
        } 