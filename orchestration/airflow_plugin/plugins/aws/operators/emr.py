from typing import Dict, Any, List
from airflow.providers.amazon.aws.operators.emr import EmrCreateJobFlowOperator
from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

class EMROperatorFactory(BaseAWSOperatorFactory):
    """Factory for EMR operator"""
    TASK_TYPE = "emr"
    def get_operator_class(self):
        return EmrCreateJobFlowOperator

    def create_operator(self, task_id: str, config: Dict[str, Any]) -> EmrCreateJobFlowOperator:
        """Create EMR operator"""
        aws_args = self.get_common_aws_args(config)
        return EmrCreateJobFlowOperator(
            task_id=task_id,
            job_flow_overrides=config['job_flow_overrides'],
            **aws_args
        )

    def get_config_schema(self) -> Dict[str, Any]:
        """Get EMR configuration schema"""
        base_schema = super().get_config_schema()
        base_schema["properties"].update({
            "job_flow_overrides": {
                "type": "object",
                "description": "EMR cluster configuration",
                "properties": {
                    "Name": {
                        "type": "string",
                        "description": "Cluster name"
                    },
                    "LogUri": {
                        "type": "string",
                        "description": "S3 path for logs"
                    },
                    "ReleaseLabel": {
                        "type": "string",
                        "description": "EMR release version"
                    },
                    "Instances": {
                        "type": "object",
                        "description": "Instance configuration"
                    },
                    "Applications": {
                        "type": "array",
                        "items": {
                            "type": "object"
                        },
                        "description": "Applications to install"
                    },
                    "Steps": {
                        "type": "array",
                        "items": {
                            "type": "object"
                        },
                        "description": "Steps to execute"
                    }
                }
            },
            "wait_for_completion": {
                "type": "boolean",
                "description": "Whether to wait for cluster creation",
                "default": True
            }
        })
        base_schema["required"] = ["job_flow_overrides"]
        return base_schema

    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            "aws_conn_id": "aws_default",
            "job_flow_overrides": {
                "Name": "",
                "LogUri": "",
                "ReleaseLabel": "emr-6.0.0",
                "Instances": {},
                "Applications": [],
                "Steps": []
            },
            "wait_for_completion": True
        }

    def get_icon(self) -> str:
        """Get operator icon"""
        return "emr"

    def get_required_parameters(self) -> List[str]:
        """Get required parameters"""
        return ["job_flow_overrides"] 