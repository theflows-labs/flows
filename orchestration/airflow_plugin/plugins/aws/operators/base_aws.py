from typing import Dict, Any, List
from abc import ABC, abstractmethod
from orchestration.airflow_plugin.plugin_core.dag_builder.base import OperatorFactory

class BaseAWSOperatorFactory(OperatorFactory):
    """Base class for all AWS operator factories"""

    TASK_TYPE = "aws"
    
    def get_operator_class(self):
        """Get the operator class"""
        raise NotImplementedError("Subclasses must implement get_operator_class")

    def create_operator(self, task_id: str, config: Dict[str, Any]):
        """Create the operator"""
        raise NotImplementedError("Subclasses must implement create_operator")

    def get_icon(self) -> str:
        """Get operator icon"""
        pass #raise NotImplementedError("Subclasses must implement get_icon")

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        raise NotImplementedError("Subclasses must implement get_required_parameters")

    def get_common_aws_args(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Get common AWS arguments from config"""
        return {
            'aws_conn_id': config.get('aws_conn_id', 'aws_default'),
            'region_name': config.get('region_name'),
            'verify': config.get('verify', True)
        }

    def get_config_schema(self) -> Dict[str, Any]:
        """Get base AWS configuration schema"""
        return {
            "type": "object",
            "properties": {
                "aws_conn_id": {
                    "type": "string",
                    "description": "AWS connection ID",
                    "default": "aws_default"
                },
                "region_name": {
                    "type": "string",
                    "description": "AWS region name"
                },
                "verify": {
                    "type": "boolean",
                    "description": "Whether to verify SSL certificates",
                    "default": True
                }
            }
        } 