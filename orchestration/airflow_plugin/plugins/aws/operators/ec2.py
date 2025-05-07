# from typing import Dict, Any, List
# from airflow.providers.amazon.aws.operators.ec2 import EC2StartInstanceOperator
# from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

# class EC2OperatorFactory(BaseAWSOperatorFactory):
#     """Factory for EC2 operator"""
#     TASK_TYPE = "ec2"

#     def get_operator_class(self):
#         return EC2StartInstanceOperator

#     def create_operator(self, task_id: str, config: Dict[str, Any]) -> EC2StartInstanceOperator:
#         """Create EC2 operator"""
#         aws_args = self.get_common_aws_args(config)
#         return EC2StartInstanceOperator(
#             task_id=task_id,
#             instance_id=config['instance_id'],
#             **aws_args
#         )

#     def get_config_schema(self) -> Dict[str, Any]:
#         """Get EC2 configuration schema"""
#         base_schema = super().get_config_schema()
#         base_schema["properties"].update({
#             "instance_id": {
#                 "type": "string",
#                 "description": "ID of the EC2 instance"
#             },
#             "action": {
#                 "type": "string",
#                 "description": "Action to perform on the instance",
#                 "enum": ["start", "stop", "terminate", "reboot"]
#             },
#             "wait_for_completion": {
#                 "type": "boolean",
#                 "description": "Whether to wait for action completion",
#                 "default": True
#             }
#         })
#         base_schema["required"] = ["instance_id", "action"]
#         return base_schema

#     def get_default_config(self) -> Dict[str, Any]:
#         """Get default configuration"""
#         return {
#             "aws_conn_id": "aws_default",
#             "instance_id": "",
#             "action": "start",
#             "wait_for_completion": True
#         }

#     def get_icon(self) -> str:
#         """Get operator icon"""
#         return "ec2"

#     def get_required_parameters(self) -> List[str]:
#         """Get required parameters"""
#         return ["instance_id", "action"] 