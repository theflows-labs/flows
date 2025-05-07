# from typing import Dict, Any, List
# from airflow.providers.amazon.aws.operators.glue import GlueJobOperator
# from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

# class GlueOperatorFactory(BaseAWSOperatorFactory):
#     """Factory for Glue operator"""
#     TASK_TYPE = "glue"
#     def get_operator_class(self):
#         return GlueJobOperator

#     def create_operator(self, task_id: str, config: Dict[str, Any]) -> GlueJobOperator:
#         """Create Glue operator"""
#         aws_args = self.get_common_aws_args(config)
#         return GlueJobOperator(
#             task_id=task_id,
#             job_name=config['job_name'],
#             script_location=config.get('script_location'),
#             script_args=config.get('script_args', {}),
#             **aws_args
#         )

#     def get_config_schema(self) -> Dict[str, Any]:
#         """Get Glue configuration schema"""
#         base_schema = super().get_config_schema()
#         base_schema["properties"].update({
#             "job_name": {
#                 "type": "string",
#                 "description": "Name of the Glue job"
#             },
#             "script_location": {
#                 "type": "string",
#                 "description": "S3 path to the script"
#             },
#             "script_args": {
#                 "type": "object",
#                 "description": "Arguments to pass to the script"
#             },
#             "job_bookmark_option": {
#                 "type": "string",
#                 "description": "Job bookmark option",
#                 "enum": ["job-bookmark-enable", "job-bookmark-disable", "job-bookmark-pause"]
#             },
#             "wait_for_completion": {
#                 "type": "boolean",
#                 "description": "Whether to wait for job completion",
#                 "default": True
#             }
#         })
#         base_schema["required"] = ["job_name"]
#         return base_schema

#     def get_default_config(self) -> Dict[str, Any]:
#         """Get default configuration"""
#         return {
#             "aws_conn_id": "aws_default",
#             "job_name": "",
#             "script_location": "",
#             "script_args": {},
#             "job_bookmark_option": "job-bookmark-enable",
#             "wait_for_completion": True
#         }

#     def get_icon(self) -> str:
#         """Get operator icon"""
#         return "glue"

#     def get_required_parameters(self) -> List[str]:
#         """Get required parameters"""
#         return ["job_name"] 