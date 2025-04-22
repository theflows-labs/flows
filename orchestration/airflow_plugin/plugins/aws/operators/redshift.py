from typing import Dict, Any, List
from airflow.providers.amazon.aws.operators.redshift_cluster import RedshiftCreateClusterOperator
from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

class RedshiftOperatorFactory(BaseAWSOperatorFactory):
    """Factory for Redshift operator"""
    TASK_TYPE = "redshift"
    def get_operator_class(self):
        return RedshiftCreateClusterOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]) -> RedshiftCreateClusterOperator:
        """Create Redshift operator"""
        aws_args = self.get_common_aws_args(config)
        return RedshiftCreateClusterOperator(
            task_id=task_id,
            cluster_identifier=config['cluster_identifier'],
            node_type=config['node_type'],
            master_username=config['master_username'],
            master_user_password=config['master_user_password'],
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get Redshift configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "cluster_identifier": {
                "type": "string",
                "description": "Cluster identifier"
            },
            "node_type": {
                "type": "string",
                "description": "Node type"
            },
            "master_username": {
                "type": "string",
                "description": "Master username"
            },
            "master_user_password": {
                "type": "string",
                "description": "Master user password"
            },
            "cluster_type": {
                "type": "string",
                "description": "Cluster type",
                "enum": ["single-node", "multi-node"]
            },
            "number_of_nodes": {
                "type": "integer",
                "description": "Number of nodes",
                "minimum": 1
            },
            "db_name": {
                "type": "string",
                "description": "Database name"
            },
            "wait_for_completion": {
                "type": "boolean",
                "description": "Whether to wait for cluster creation",
                "default": True
            }
        })
        base_schema["required"] = ["cluster_identifier", "node_type", "master_username", "master_user_password"]
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "aws_conn_id": "aws_default",
            "cluster_identifier": "",
            "node_type": "",
            "master_username": "",
            "master_user_password": "",
            "cluster_type": "single-node",
            "number_of_nodes": 1,
            "db_name": "dev",
            "wait_for_completion": True
        }

    def get_icon(self) -> str:
        """Get operator icon"""
        return "redshift"

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ["cluster_identifier", "node_type", "master_username", "master_user_password"] 