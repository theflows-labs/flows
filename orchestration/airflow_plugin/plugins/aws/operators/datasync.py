from typing import Dict, Any, List
from airflow.providers.amazon.aws.operators.datasync import DataSyncOperator
from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

class DataSyncOperatorFactory(BaseAWSOperatorFactory):
    """Factory for AWS DataSync operator"""
    TASK_TYPE = "datasync"
    def get_operator_class(self):
        return DataSyncOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]) -> DataSyncOperator:
        """Create DataSync operator"""
        aws_args = self.get_common_aws_args(config)
        return DataSyncOperator(
            task_id=task_id,
            task_arn=config['task_arn'],
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get DataSync configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "task_arn": {
                "type": "string",
                "description": "ARN of the DataSync task"
            },
            "overrides": {
                "type": "object",
                "description": "Task execution overrides"
            },
            "wait_for_completion": {
                "type": "boolean",
                "description": "Whether to wait for task completion",
                "default": True
            }
        })
        base_schema["required"] = ["task_arn"]
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "aws_conn_id": "aws_default",
            "task_arn": "",
            "overrides": {},
            "wait_for_completion": True
        }

    def get_icon(self) -> str:
        """Get operator icon"""
        return "datasync"

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ["task_arn"] 