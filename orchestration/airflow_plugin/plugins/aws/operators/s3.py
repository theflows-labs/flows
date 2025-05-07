from typing import Dict, Any, Type
from pydantic import Field
from airflow.models import BaseOperator
from airflow import DAG
from airflow.providers.amazon.aws.operators.s3 import (
    S3CopyObjectOperator,
    S3DeleteObjectsOperator,
    S3CreateObjectOperator,
    S3ListOperator
)
from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory, BaseAWSParams

class S3CopyOperatorParams(BaseAWSParams):
    """Parameters for S3 operator."""
    source_bucket_key: str = Field(..., description="Source S3 key")
    dest_bucket_key: str = Field(..., description="Destination S3 key")
    source_bucket_name: str = Field(..., description="Source S3 bucket name")
    dest_bucket_name: str = Field(..., description="Destination S3 bucket name")

class S3CopyOperatorFactory(BaseAWSOperatorFactory):
    """Factory for creating S3 operators"""
    
    TASK_TYPE = "s3_copy"
    params_class = S3CopyOperatorParams
    
    @classmethod
    def get_operator_class(cls, task_type: str) -> Type[BaseOperator]:
        """Get the operator class"""
        return S3CopyObjectOperator 
    
    def create_operator(self, task_id: str, params: S3CopyOperatorParams, dag: DAG) -> BaseOperator:
        """Create an S3 copy operator from parameters"""
        return super().create_operator(task_id, params, dag)
    

class S3ListOperatorParams(BaseAWSParams):
    """Parameters for S3 operator."""
    bucket: str = Field(..., description="S3 bucket name")

class S3ListOperatorFactory(BaseAWSOperatorFactory):
    """Factory for creating S3 operators"""
    
    TASK_TYPE = "s3_list"
    params_class = S3ListOperatorParams
    
    @classmethod
    def get_operator_class(cls, task_type: str) -> Type[BaseOperator]:
        """Get the operator class"""
        return S3ListOperator 
    
    def create_operator(self, task_id: str, params: S3ListOperatorParams, dag: DAG) -> BaseOperator:
        """Create an S3 list operator from parameters"""
        return super().create_operator(task_id, params, dag)