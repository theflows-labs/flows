from typing import Dict, Any, List
from airflow.providers.amazon.aws.operators.sqs import SqsPublishOperator   
from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

class SQSOperatorFactory(BaseAWSOperatorFactory):
    """Factory for SQS operator"""
    TASK_TYPE = "sqs"
    def get_operator_class(self):
        return SqsPublishOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]) -> SqsPublishOperator:
        """Create SQS operator"""
        aws_args = self.get_common_aws_args(config)
        return SqsPublishOperator(
            task_id=task_id,
            queue_url=config['queue_url'],
            message_body=config['message_body'],
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get SQS configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "queue_url": {
                "type": "string",
                "description": "URL of the SQS queue"
            },
            "message_body": {
                "type": "string",
                "description": "Message body"
            },
            "message_attributes": {
                "type": "object",
                "description": "Message attributes"
            },
            "delay_seconds": {
                "type": "integer",
                "description": "Delay in seconds",
                "minimum": 0,
                "maximum": 900
            }
        })
        base_schema["required"] = ["queue_url", "message_body"]
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "aws_conn_id": "aws_default",
            "queue_url": "",
            "message_body": "",
            "message_attributes": {},
            "delay_seconds": 0
        }

    def get_icon(self) -> str:
        """Get operator icon"""
        return "sqs"

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ["queue_url", "message_body"] 