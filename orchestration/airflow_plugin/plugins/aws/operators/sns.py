from typing import Dict, Any, List
from airflow.providers.amazon.aws.operators.sns import SnsPublishOperator
from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

class SNSOperatorFactory(BaseAWSOperatorFactory):
    """Factory for SNS operator"""
    TASK_TYPE = "sns"
    def get_operator_class(self):
        return SnsPublishOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]) -> SnsPublishOperator:
        """Create SNS operator"""
        aws_args = self.get_common_aws_args(config)
        return SnsPublishOperator(
            task_id=task_id,
            target_arn=config['target_arn'],
            message=config['message'],
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get SNS configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "target_arn": {
                "type": "string",
                "description": "ARN of the SNS topic"
            },
            "message": {
                "type": "string",
                "description": "Message to publish"
            },
            "subject": {
                "type": "string",
                "description": "Message subject"
            },
            "message_attributes": {
                "type": "object",
                "description": "Message attributes"
            }
        })
        base_schema["required"] = ["target_arn", "message"]
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "aws_conn_id": "aws_default",
            "target_arn": "",
            "message": "",
            "subject": "",
            "message_attributes": {}
        }

    def get_icon(self) -> str:
        """Get operator icon"""
        return "sns"

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ["target_arn", "message"] 