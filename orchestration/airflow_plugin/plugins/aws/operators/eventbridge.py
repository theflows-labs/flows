# from typing import Dict, Any, List
# from airflow.providers.amazon.aws.operators.eventbridge import EventBridgePutEventsOperator
# from orchestration.airflow_plugin.plugins.aws.operators.base_aws import BaseAWSOperatorFactory

# class EventBridgeOperatorFactory(BaseAWSOperatorFactory):
#     """Factory for EventBridge operator"""
#     TASK_TYPE = "eventbridge"
#     def get_operator_class(self):
#         return EventBridgePutEventsOperator

#     def create_operator(self, task_id: str, config: Dict[str, Any]) -> EventBridgePutEventsOperator:
#         """Create EventBridge operator"""
#         aws_args = self.get_common_aws_args(config)
#         return EventBridgePutEventsOperator(
#             task_id=task_id,
#             entries=config['entries'],
#             **aws_args
#         )

#     def get_config_schema(self) -> Dict[str, Any]:
#         """Get EventBridge configuration schema"""
#         base_schema = super().get_config_schema()
#         base_schema["properties"].update({
#             "entries": {
#                 "type": "array",
#                 "items": {
#                     "type": "object",
#                     "properties": {
#                         "Source": {
#                             "type": "string",
#                             "description": "Source of the event"
#                         },
#                         "DetailType": {
#                             "type": "string",
#                             "description": "Type of the event"
#                         },
#                         "Detail": {
#                             "type": "string",
#                             "description": "Event details in JSON format"
#                         },
#                         "EventBusName": {
#                             "type": "string",
#                             "description": "Event bus name"
#                         }
#                     }
#                 },
#                 "description": "Events to put"
#             }
#         })
#         base_schema["required"] = ["entries"]
#         return base_schema

#     def get_default_config(self) -> Dict[str, Any]:
#         """Get default configuration"""
#         return {
#             "aws_conn_id": "aws_default",
#             "entries": []
#         }

#     def get_icon(self) -> str:
#         """Get operator icon"""
#         return "eventbridge"

#     def get_required_parameters(self) -> List[str]:
#         """Get required parameters"""
#         return ["entries"] 