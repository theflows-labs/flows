from typing import Dict, Any, List
from airflow.providers.amazon.aws.operators.s3 import (
    S3ListOperator,
    S3DeleteObjectsOperator,
    S3CopyObjectOperator,
    S3CreateObjectOperator
)
#from airflow.providers.amazon.aws.transfers.s3_to_s3 import S3ToS3Operator
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from .base_aws import BaseAWSOperatorFactory

class BaseS3OperatorFactory(BaseAWSOperatorFactory):
    """Base factory for S3 operators"""
    
    TASK_TYPE = "s3"

    def get_icon(self) -> str:
        """Get operator icon"""
        return "s3"

    def get_config_schema(self) -> Dict[str, Any]:
        """Get base S3 configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "bucket": {
                "type": "string",
                "description": "S3 bucket name"
            }
        })
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "aws_conn_id": "aws_default",
            "bucket": ""
        }

class S3ListOperatorFactory(BaseS3OperatorFactory):
    """Factory for S3 list operation"""
    
    TASK_TYPE = "s3_list"

    def get_operator_class(self):
        """Get the operator class"""
        return S3ListOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]):
        """Create S3 list operator"""
        aws_args = self.get_common_aws_args(config)
        return S3ListOperator(
            task_id=task_id,
            bucket=config['bucket'],
            prefix=config.get('prefix'),
            delimiter=config.get('delimiter'),
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get list operation configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "prefix": {
                "type": "string",
                "description": "Prefix for list operation"
            },
            "delimiter": {
                "type": "string",
                "description": "Delimiter for list operation"
            }
        })
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        base_config = super().get_default_config()
        base_config.update({
            "prefix": "",
            "delimiter": ""
        })
        return base_config

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ['bucket']

class S3DeleteOperatorFactory(BaseS3OperatorFactory):
    """Factory for S3 delete operation"""
    
    TASK_TYPE = "s3_delete"

    def get_operator_class(self):
        """Get the operator class"""
        return S3DeleteObjectsOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]):
        """Create S3 delete operator"""
        aws_args = self.get_common_aws_args(config)
        return S3DeleteObjectsOperator(
            task_id=task_id,
            bucket=config['bucket'],
            keys=config['keys'],
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get delete operation configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "keys": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Keys to delete"
            }
        })
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        base_config = super().get_default_config()
        base_config.update({
            "keys": []
        })
        return base_config

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ['bucket', 'keys']

class S3CopyOperatorFactory(BaseS3OperatorFactory):
    """Factory for S3 copy operation"""
    
    TASK_TYPE = "s3_copy"

    def get_operator_class(self):
        """Get the operator class"""
        return S3CopyObjectOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]):
        """Create S3 copy operator"""
        aws_args = self.get_common_aws_args(config)
        return S3CopyObjectOperator(
            task_id=task_id,
            source_bucket_key=config['source_bucket_key'],
            dest_bucket_key=config['dest_bucket_key'],
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get copy operation configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "source_bucket_key": {
                "type": "string",
                "description": "Source bucket and key (format: bucket/key)"
            },
            "dest_bucket_key": {
                "type": "string",
                "description": "Destination bucket and key (format: bucket/key)"
            }
        })
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        base_config = super().get_default_config()
        base_config.update({
            "source_bucket_key": "",
            "dest_bucket_key": ""
        })
        return base_config

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ['source_bucket_key', 'dest_bucket_key']

class S3CreateOperatorFactory(BaseS3OperatorFactory):
    """Factory for S3 create operation"""
    
    TASK_TYPE = "s3_create"

    def get_operator_class(self):
        """Get the operator class"""
        return S3CreateObjectOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]):
        """Create S3 create operator"""
        aws_args = self.get_common_aws_args(config)
        return S3CreateObjectOperator(
            task_id=task_id,
            bucket=config['bucket'],
            key=config['key'],
            data=config.get('data', ''),
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get create operation configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "key": {
                "type": "string",
                "description": "Object key for create operation"
            },
            "data": {
                "type": "string",
                "description": "Data to create in the object"
            }
        })
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        base_config = super().get_default_config()
        base_config.update({
            "key": "",
            "data": ""
        })
        return base_config

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ['bucket', 'key']

    def get_icon(self) -> str:
        """Get operator icon"""
        return "s3"

    def get_required_parameters(self) -> List[str]:
        """Get required parameters based on operation type"""
        operation = self.config.get('operation', 'list')
        required_params = {
            'list': ['bucket'],
            'delete': ['bucket', 'keys'],
            'copy': ['source_bucket_key', 'dest_bucket_key'],
            'put': ['bucket', 'key']
        }
        return required_params.get(operation, ['bucket']) 