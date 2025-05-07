# from typing import Dict, Any, List
# from airflow.providers.amazon.aws.operators.batch import BatchOperator
# from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

# class BatchOperatorFactory(BaseAWSOperatorFactory):
#     """Factory for AWS Batch operator"""
    
#     def get_operator_class(self):
#         return BatchOperator

#     def create_operator(self, task_id: str, config: Dict[str, Any]) -> BatchOperator:
#         """Create Batch operator"""
#         aws_args = self.get_common_aws_args(config)
#         return BatchOperator(
#             task_id=task_id,
#             job_name=config['job_name'],
#             job_definition=config['job_definition'],
#             job_queue=config['job_queue'],
#             **aws_args
#         )

#     def get_config_schema(self) -> Dict[str, Any]:
#         """Get Batch configuration schema"""
#         base_schema = super().get_config_schema()
#         base_schema["properties"].update({
#             "job_name": {
#                 "type": "string",
#                 "description": "Name of the job"
#             },
#             "job_definition": {
#                 "type": "string",
#                 "description": "ARN of the job definition"
#             },
#             "job_queue": {
#                 "type": "string",
#                 "description": "ARN of the job queue"
#             },
#             "overrides": {
#                 "type": "object",
#                 "description": "Job overrides"
#             },
#             "array_properties": {
#                 "type": "object",
#                 "description": "Array properties for array jobs"
#             }
#         })
#         base_schema["required"] = ["job_name", "job_definition", "job_queue"]
#         return base_schema

#     def get_default_config(self) -> Dict[str, Any]:
#         """Get default configuration"""
#         return {
#             "aws_conn_id": "aws_default",
#             "job_name": "",
#             "job_definition": "",
#             "job_queue": "",
#             "overrides": {},
#             "array_properties": {}
#         }

#     def get_icon(self) -> str:
#         """Get operator icon"""
#         return "batch"

#     def get_required_parameters(self) -> List[str]:
#         """Get required parameters"""
#         return ["job_name", "job_definition", "job_queue"] 