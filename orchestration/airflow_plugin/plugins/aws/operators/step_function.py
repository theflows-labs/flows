from typing import Dict, Any, List
from airflow.providers.amazon.aws.operators.step_function import StepFunctionStartExecutionOperator
from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

class StepFunctionOperatorFactory(BaseAWSOperatorFactory):
    """Factory for Step Functions operator"""
    TASK_TYPE = "step_function"
    def get_operator_class(self):
        return StepFunctionStartExecutionOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]) -> StepFunctionStartExecutionOperator:
        """Create Step Functions operator"""
        aws_args = self.get_common_aws_args(config)
        return StepFunctionStartExecutionOperator(
            task_id=task_id,
            state_machine_arn=config['state_machine_arn'],
            input=config.get('input'),
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get Step Functions configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "state_machine_arn": {
                "type": "string",
                "description": "ARN of the state machine"
            },
            "input": {
                "type": "string",
                "description": "Input to the state machine in JSON format"
            },
            "name": {
                "type": "string",
                "description": "Name of the execution"
            },
            "wait_for_completion": {
                "type": "boolean",
                "description": "Whether to wait for execution completion",
                "default": True
            }
        })
        base_schema["required"] = ["state_machine_arn"]
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "aws_conn_id": "aws_default",
            "state_machine_arn": "",
            "input": "",
            "name": "",
            "wait_for_completion": True
        }

    def get_icon(self) -> str:
        """Get operator icon"""
        return "step_function"

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ["state_machine_arn"] 