from typing import Dict, Any, List
from airflow.providers.amazon.aws.operators.cloud_formation import CloudFormationCreateStackOperator
from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

class CloudFormationOperatorFactory(BaseAWSOperatorFactory):
    """Factory for CloudFormation operator"""
    
    TASK_TYPE = "cloud_formation"

    def get_operator_class(self):
        return CloudFormationCreateStackOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]) -> CloudFormationCreateStackOperator:
        """Create CloudFormation operator"""
        aws_args = self.get_common_aws_args(config)
        return CloudFormationCreateStackOperator(
            task_id=task_id,
            stack_name=config['stack_name'],
            template_body=config.get('template_body'),
            template_url=config.get('template_url'),
            parameters=config.get('parameters', {}),
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get CloudFormation configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "stack_name": {
                "type": "string",
                "description": "Name of the CloudFormation stack"
            },
            "template_body": {
                "type": "string",
                "description": "Template body in JSON or YAML format"
            },
            "template_url": {
                "type": "string",
                "description": "URL of the template file"
            },
            "parameters": {
                "type": "object",
                "description": "Stack parameters"
            },
            "capabilities": {
                "type": "array",
                "items": {
                    "type": "string"
                },
                "description": "Stack capabilities"
            }
        })
        base_schema["required"] = ["stack_name"]
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "aws_conn_id": "aws_default",
            "stack_name": "",
            "template_body": "",
            "template_url": "",
            "parameters": {},
            "capabilities": []
        }

    def get_icon(self) -> str:
        """Get operator icon"""
        return "cloudformation"

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ["stack_name"] 