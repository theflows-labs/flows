"""
Operator factory for Athena query tasks.

This factory creates operators for executing SQL queries in Amazon Athena.
It handles query execution, result storage, and provides comprehensive parameter validation.
"""
from typing import Dict, Any, Type, List
import json
import logging

from airflow.models import BaseOperator
from airflow.providers.amazon.aws.operators.athena import AthenaOperator

from orchestration.airflow_plugin.plugin_core.dag_builder.base import OperatorFactory
from core.models import TaskConfiguration

logger = logging.getLogger(__name__)

class AthenaQueryOperatorFactory(OperatorFactory):
    """Factory for creating Athena query operators."""
    
    TASK_TYPE = "athena_query"
    
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
            return AthenaOperator
        raise ValueError(f"Unknown task type: {task_type}")
    
    @classmethod
    def get_required_parameters(cls) -> List[str]:
        """
        Get the list of required parameters for this operator.
        
        Returns:
            List of required parameter names
        """
        return [
            "query",
            "database",
            "output_location"
        ]
    
    @classmethod
    def get_optional_parameters(cls) -> Dict[str, Any]:
        """
        Get the optional parameters and their default values.
        
        Returns:
            Dictionary of parameter names and their default values
        """
        return {
            "aws_conn_id": "aws_default",
            "region_name": "us-east-1",
            "workgroup": "primary",
            "query_execution_context": None,
            "result_configuration": None,
            "client_request_token": None,
            "sleep_time": 30,
            "max_tries": None,
            "check_interval": 30
        }
    
    @classmethod
    def get_parameter_descriptions(cls) -> Dict[str, str]:
        """
        Get descriptions for all parameters.
        
        Returns:
            Dictionary of parameter names and their descriptions
        """
        return {
            "query": "The SQL query to execute in Athena",
            "database": "The name of the database to execute the query in",
            "output_location": "The S3 path where query results will be stored",
            "aws_conn_id": "The Airflow connection ID for AWS credentials",
            "region_name": "The AWS region where Athena is running",
            "workgroup": "The Athena workgroup to use for query execution",
            "query_execution_context": "Additional context for query execution",
            "result_configuration": "Configuration for query results",
            "client_request_token": "Unique token to ensure idempotency",
            "sleep_time": "Time to wait between polling for query completion",
            "max_tries": "Maximum number of attempts to check query status",
            "check_interval": "Interval between status checks in seconds"
        }
    
    @classmethod
    def get_parameter_types(cls) -> Dict[str, Type]:
        """
        Get the types for all parameters.
        
        Returns:
            Dictionary of parameter names and their types
        """
        return {
            "query": str,
            "database": str,
            "output_location": str,
            "aws_conn_id": str,
            "region_name": str,
            "workgroup": str,
            "query_execution_context": dict,
            "result_configuration": dict,
            "client_request_token": str,
            "sleep_time": int,
            "max_tries": int,
            "check_interval": int
        }
    
    @classmethod
    def get_parameter_examples(cls) -> Dict[str, Any]:
        """
        Get example values for all parameters.
        
        Returns:
            Dictionary of parameter names and example values
        """
        return {
            "query": "SELECT * FROM my_table LIMIT 10",
            "database": "my_database",
            "output_location": "s3://my-bucket/query-results/",
            "aws_conn_id": "aws_default",
            "region_name": "us-east-1",
            "workgroup": "primary",
            "query_execution_context": {
                "Database": "my_database",
                "Catalog": "AwsDataCatalog"
            },
            "result_configuration": {
                "OutputLocation": "s3://my-bucket/query-results/"
            },
            "client_request_token": "unique-token-123",
            "sleep_time": 30,
            "max_tries": 3,
            "check_interval": 30
        }
    
    def create_operator(self, task_id: str, config: Dict[str, Any], dag: Any) -> BaseOperator:
        """Create an operator instance."""
        return self.get_operator_class(self.TASK_TYPE)(
            task_id=task_id,
            dag=dag,
            **config
        )

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Get JSON schema for operator configuration."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "SQL query to execute"
                },
                "database": {
                    "type": "string",
                    "description": "Athena database name"
                },
                "output_location": {
                    "type": "string",
                    "description": "S3 location for query results"
                },
                "aws_conn_id": {
                    "type": "string",
                    "description": "AWS connection ID",
                    "default": "aws_default"
                },
                "workgroup": {
                    "type": "string",
                    "description": "Athena workgroup to use",
                    "default": "primary"
                },
                "query_execution_context": {
                    "type": "object",
                    "description": "Query execution context",
                    "properties": {
                        "database": {"type": "string"},
                        "catalog": {"type": "string"}
                    }
                },
                "result_configuration": {
                    "type": "object",
                    "description": "Result configuration",
                    "properties": {
                        "output_location": {"type": "string"},
                        "encryption_configuration": {
                            "type": "object",
                            "properties": {
                                "encryption_option": {"type": "string"},
                                "kms_key": {"type": "string"}
                            }
                        }
                    }
                }
            },
            "required": ["query", "database", "output_location"]
        }

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """Get default configuration values."""
        return {
            "aws_conn_id": "aws_default",
            "workgroup": "primary",
            "query_execution_context": {},
            "result_configuration": {}
        }

    @classmethod
    def get_icon(cls) -> str:
        """Get icon identifier for the UI."""
        return 'athena'

    def _validate_parameters(self, config_details: Dict[str, Any]) -> None:
        """
        Validate the parameters for the operator.
        
        Args:
            config_details: The configuration details
            
        Raises:
            ValueError: If required parameters are missing or invalid
        """
        for param in self.get_required_parameters():
            if param not in config_details:
                raise ValueError(f"Missing required parameter: {param}")

    def _apply_defaults(self, config_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply default values to the configuration.
        
        Args:
            config_details: The configuration details
            
        Returns:
            The updated configuration
        """
        params = config_details.copy()
        for param, default_value in self.get_optional_parameters().items():
            if param not in params:
                params[param] = default_value
        return params 