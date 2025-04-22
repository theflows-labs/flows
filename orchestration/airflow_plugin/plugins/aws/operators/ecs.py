from typing import Dict, Any, List
from airflow.providers.amazon.aws.operators.ecs import EcsBaseOperator
from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

class EcsBaseOperatorFactory(BaseAWSOperatorFactory):
    """Factory for ECS operator"""
    TASK_TYPE = "ecs"
    def get_operator_class(self):
        return EcsBaseOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]) -> EcsBaseOperator:
        """Create ECS operator"""
        aws_args = self.get_common_aws_args(config)
        return EcsBaseOperator(
            task_id=task_id,
            task_definition=config['task_definition'],
            cluster=config['cluster'],
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get ECS configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "task_definition": {
                "type": "string",
                "description": "ARN of the task definition"
            },
            "cluster": {
                "type": "string",
                "description": "Name of the ECS cluster"
            },
            "launch_type": {
                "type": "string",
                "description": "Launch type for the task",
                "enum": ["EC2", "FARGATE"]
            },
            "network_configuration": {
                "type": "object",
                "description": "Network configuration for the task"
            },
            "overrides": {
                "type": "object",
                "description": "Task overrides"
            },
            "wait_for_completion": {
                "type": "boolean",
                "description": "Whether to wait for task completion",
                "default": True
            }
        })
        base_schema["required"] = ["task_definition", "cluster"]
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "aws_conn_id": "aws_default",
            "task_definition": "",
            "cluster": "",
            "launch_type": "EC2",
            "network_configuration": {},
            "overrides": {},
            "wait_for_completion": True
        }

    def get_icon(self) -> str:
        """Get operator icon"""
        return "ecs"

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ["task_definition", "cluster"] 