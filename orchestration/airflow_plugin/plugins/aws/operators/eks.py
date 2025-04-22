from typing import Dict, Any, List
from airflow.providers.amazon.aws.operators.eks import EKSPodOperator
from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

class EKSOperatorFactory(BaseAWSOperatorFactory):
    """Factory for EKS operator"""
    TASK_TYPE = "eks"

    def get_operator_class(self):
        return EKSPodOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]) -> EKSPodOperator:
        """Create EKS operator"""
        aws_args = self.get_common_aws_args(config)
        return EKSPodOperator(
            task_id=task_id,
            cluster_name=config['cluster_name'],
            pod_name=config['pod_name'],
            image=config['image'],
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get EKS configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "cluster_name": {
                "type": "string",
                "description": "Name of the EKS cluster"
            },
            "pod_name": {
                "type": "string",
                "description": "Name of the pod"
            },
            "image": {
                "type": "string",
                "description": "Docker image to use"
            },
            "namespace": {
                "type": "string",
                "description": "Kubernetes namespace",
                "default": "default"
            },
            "cmds": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Command to run in the container"
            },
            "arguments": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Arguments to the command"
            },
            "env_vars": {
                "type": "object",
                "description": "Environment variables"
            }
        })
        base_schema["required"] = ["cluster_name", "pod_name", "image"]
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "aws_conn_id": "aws_default",
            "cluster_name": "",
            "pod_name": "",
            "image": "",
            "namespace": "default",
            "cmds": [],
            "arguments": [],
            "env_vars": {}
        }

    def get_icon(self) -> str:
        """Get operator icon"""
        return "eks"

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ["cluster_name", "pod_name", "image"] 