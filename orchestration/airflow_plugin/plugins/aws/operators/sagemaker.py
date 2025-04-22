from typing import Dict, Any, List
from airflow.providers.amazon.aws.operators.sagemaker import SageMakerTrainingOperator
from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

class SageMakerOperatorFactory(BaseAWSOperatorFactory):
    """Factory for SageMaker operator"""
    TASK_TYPE = "sagemaker"
    def get_operator_class(self):
        return SageMakerTrainingOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]) -> SageMakerTrainingOperator:
        """Create SageMaker operator"""
        aws_args = self.get_common_aws_args(config)
        return SageMakerTrainingOperator(
            task_id=task_id,
            config=config['config'],
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get SageMaker configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "config": {
                "type": "object",
                "description": "Training job configuration",
                "properties": {
                    "TrainingJobName": {
                        "type": "string",
                        "description": "Training job name"
                    },
                    "AlgorithmSpecification": {
                        "type": "object",
                        "description": "Algorithm specification"
                    },
                    "RoleArn": {
                        "type": "string",
                        "description": "IAM role ARN"
                    },
                    "InputDataConfig": {
                        "type": "array",
                        "items": {
                            "type": "object"
                        },
                        "description": "Input data configuration"
                    },
                    "OutputDataConfig": {
                        "type": "object",
                        "description": "Output data configuration"
                    },
                    "ResourceConfig": {
                        "type": "object",
                        "description": "Resource configuration"
                    },
                    "StoppingCondition": {
                        "type": "object",
                        "description": "Stopping condition"
                    }
                }
            },
            "wait_for_completion": {
                "type": "boolean",
                "description": "Whether to wait for job completion",
                "default": True
            }
        })
        base_schema["required"] = ["config"]
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "aws_conn_id": "aws_default",
            "config": {
                "TrainingJobName": "",
                "AlgorithmSpecification": {},
                "RoleArn": "",
                "InputDataConfig": [],
                "OutputDataConfig": {},
                "ResourceConfig": {},
                "StoppingCondition": {}
            },
            "wait_for_completion": True
        }

    def get_icon(self) -> str:
        """Get operator icon"""
        return "sagemaker"

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ["config"] 