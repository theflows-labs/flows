from typing import Dict, Any, List
from airflow.providers.amazon.aws.operators.lambda_function import LambdaInvokeFunctionOperator
from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

class LambdaOperatorFactory(BaseAWSOperatorFactory):
    """Factory for Lambda operator"""
    TASK_TYPE = "lambda"
    def get_operator_class(self):
        return LambdaInvokeFunctionOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]) -> LambdaInvokeFunctionOperator:
        """Create Lambda operator"""
        aws_args = self.get_common_aws_args(config)
        return LambdaInvokeFunctionOperator(
            task_id=task_id,
            function_name=config['function_name'],
            payload=config.get('payload'),
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get Lambda configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "function_name": {
                "type": "string",
                "description": "Name of the Lambda function"
            },
            "payload": {
                "type": "string",
                "description": "JSON payload to pass to the function"
            },
            "qualifier": {
                "type": "string",
                "description": "Function version or alias"
            },
            "invocation_type": {
                "type": "string",
                "description": "Invocation type",
                "enum": ["RequestResponse", "Event", "DryRun"]
            },
            "log_type": {
                "type": "string",
                "description": "Log type",
                "enum": ["None", "Tail"]
            }
        })
        base_schema["required"] = ["function_name"]
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "aws_conn_id": "aws_default",
            "function_name": "",
            "payload": "",
            "qualifier": "",
            "invocation_type": "RequestResponse",
            "log_type": "None"
        }

    def get_icon(self) -> str:
        """Get operator icon"""
        return "lambda"

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ["function_name"] 