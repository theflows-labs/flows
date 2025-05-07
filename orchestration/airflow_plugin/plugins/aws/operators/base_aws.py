from typing import Dict, Any, Type
from abc import ABC, abstractmethod
from pydantic import Field
from airflow.models import BaseOperator
from airflow import DAG
from orchestration.airflow_plugin.plugin_core.dag_builder.base import OperatorFactory, OperatorParams
from core.models import TaskConfiguration

class BaseAWSParams(OperatorParams):
    """Base parameters for all AWS operators."""
    aws_conn_id: str = Field("aws_default", description="AWS connection ID")
    # region_name: str = Field(None, description="AWS region name") # s3 operator is failing with region_name
    verify: bool = Field(True, description="Whether to verify SSL certificates")

class BaseAWSOperatorFactory(OperatorFactory):
    """Base class for all AWS operator factories"""
    
    TASK_TYPE = "base"
    params_class = BaseAWSParams
    
    @classmethod
    def get_operator_class(cls, task_type: str) -> Type[BaseOperator]:
        """Get the operator class"""
        raise NotImplementedError("Subclasses must implement get_operator_class")

    def create_operator(self, task_id: str, params: BaseAWSParams, dag: DAG) -> BaseOperator:
        """Create the operator from parameters"""
        operator_class = self.get_operator_class(self.TASK_TYPE)
        return operator_class(
            task_id=task_id,
            dag=dag,
            **params
        )

    def get_icon(self) -> str:
        """Get operator icon"""
        return "aws"  # Default AWS icon 