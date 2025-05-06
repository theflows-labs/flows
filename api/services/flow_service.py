from typing import Dict, List, Optional, Any
from core.repositories.repository import FlowConfigurationRepository, TaskConfigurationRepository
from core.models.models import FlowConfiguration, TaskConfiguration
import yaml
import logging

logger = logging.getLogger(__name__)

class FlowService:
    def __init__(self):
        self.flow_repo = FlowConfigurationRepository()
        self.task_repo = TaskConfigurationRepository()

    @classmethod
    def get_all_flows(cls) -> List[Dict[str, Any]]:
        """Get all active flows."""
        service = cls()
        flows = service.flow_repo.get_all_flow_configs()
        return [service._flow_to_dict(flow) for flow in flows]    

    @classmethod
    def get_all_activeflows(cls) -> List[Dict[str, Any]]:
        """Get all active flows."""
        service = cls()
        flows = service.flow_repo.get_all_active_flow_configs()
        return [service._flow_to_dict(flow) for flow in flows]

    @classmethod
    def get_flow(cls, flow_id: str) -> Optional[Dict[str, Any]]:
        """Get a flow by ID."""
        service = cls()
        flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
        if flow:
            return service._flow_to_dict(flow)
        return None

    @classmethod
    def create_flow(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new flow."""
        service = cls()
        
        # Convert to YAML if not provided
        yaml_content = data.get('config_details_yaml')
        if not yaml_content and data.get('config_details'):
            yaml_content = yaml.dump(data['config_details'], default_flow_style=False)

        flow = service.flow_repo.create_flow_config(
            flow_id=data['flow_id'],
            config_details=data['config_details'],
            config_details_yaml=yaml_content,
            description=data.get('description')
        )
        return service._flow_to_dict(flow)

    @classmethod
    def update_flow(cls, flow_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a flow."""
        service = cls()
        flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
        if not flow:
            return None

        # Convert to YAML if not provided
        yaml_content = data.get('config_details_yaml')
        if not yaml_content and data.get('config_details'):
            yaml_content = yaml.dump(data['config_details'], default_flow_style=False)

        updated_flow = service.flow_repo.update_flow_config(
            config_id=flow.config_id,
            config_details=data.get('config_details', flow.config_details),
            config_details_yaml=yaml_content,
            description=data.get('description', flow.description)
        )
        return service._flow_to_dict(updated_flow) if updated_flow else None

    @classmethod
    def delete_flow(cls, flow_id: str) -> bool:
        """Delete a flow."""
        service = cls()
        flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
        if flow:
            return service.flow_repo.delete_flow_config(flow.config_id)
        return False

    @classmethod
    def get_flow_yaml(cls, flow_id: str) -> Optional[str]:
        """Get the YAML representation of a flow."""
        service = cls()
        flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
        if not flow:
            return None

        # Get tasks with dependencies eagerly loaded
        tasks = service.task_repo.get_task_configs_by_flow_config_with_dependencies(flow.config_id)
        
        # Build task dependencies
        task_dependencies = []
        for task in tasks:
            # Dependencies are now eagerly loaded
            for dep in task.dependencies:
                task_dependencies.append({
                    'from': dep.task_id,
                    'to': dep.depends_on_task_id,
                    'type': dep.dependency_type,
                    'condition': dep.condition
                })

        # Build YAML structure
        yaml_structure = {
            'version': '1.0',
            'flow': {
                'id': flow.flow_id,
                'description': flow.description or '',
                'tasks': [{
                    'id': task.task_id,
                    'type': task.task_type,
                    'name': task.description or f'Task {task.task_sequence}',
                    'description': task.description or '',
                    'config': task.config_details or {},
                    'sequence': task.task_sequence
                } for task in tasks],
                'dependencies': task_dependencies
            },
            'metadata': {
                'created_at': flow.created_dt.isoformat() if flow.created_dt else None,
                'updated_at': flow.updated_dt.isoformat() if flow.updated_dt else None,
                'version': '1.0',
                'engine': 'airflow'
            }
        }

        # Convert to YAML with proper formatting
        return yaml.dump(
            yaml_structure,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            width=120,
            allow_unicode=True
        )

    @staticmethod
    def _flow_to_dict(flow: FlowConfiguration) -> Dict[str, Any]:
        """Convert a FlowConfiguration model to a dictionary."""
        return {
            'config_id': flow.config_id,
            'flow_id': flow.flow_id,
            'config_details': flow.config_details,
            'config_details_yaml': flow.config_details_yaml,
            'description': flow.description,
            'created_dt': flow.created_dt.isoformat() if flow.created_dt else None,
            'updated_dt': flow.updated_dt.isoformat() if flow.updated_dt else None,
            'is_active': flow.is_active
        }

    @classmethod
    def activate_flow(cls, flow_id: str):
        """Activate a flow by setting its is_active flag to True."""
        logger.info(f"Activating flow: {flow_id}")
        try:
            service = cls()
            # Get the flow configuration
            flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
            if not flow:
                logger.warning(f"Flow not found: {flow_id}")
                return None

            # Update the flow configuration using the repository
            updated_flow = service.flow_repo.update_flow_status(
                config_id=flow.config_id,
                is_active=True
            )
            
            if not updated_flow:
                logger.error(f"Failed to activate flow: {flow_id}")
                return None
            
            logger.info(f"Successfully activated flow: {flow_id}")
            return service._flow_to_dict(updated_flow)
        except Exception as e:
            logger.error(f"Error activating flow {flow_id}: {str(e)}")
            raise

    @classmethod
    def deactivate_flow(cls, flow_id: str):
        """Deactivate a flow by setting its is_active flag to False."""
        logger.info(f"Deactivating flow: {flow_id}")
        try:
            service = cls()
            # Get the flow configuration
            flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
            if not flow:
                logger.warning(f"Flow not found: {flow_id}")
                return None

            # Update the flow configuration using the repository
            updated_flow = service.flow_repo.update_flow_status(
                config_id=flow.config_id,
                is_active=False
            )
            
            if not updated_flow:
                logger.error(f"Failed to deactivate flow: {flow_id}")
                return None
            
            logger.info(f"Successfully deactivated flow: {flow_id}")
            return service._flow_to_dict(updated_flow)
        except Exception as e:
            logger.error(f"Error deactivating flow {flow_id}: {str(e)}")
            raise

    @classmethod
    def get_flow_statistics(cls):
        """Get statistics about flows and tasks."""
        logger.info("Getting flow statistics")
        try:
            service = cls()
            flows = service.flow_repo.get_all_flow_configs()
            
            # Calculate flow statistics
            total_flows = len(flows)
            active_flows = sum(1 for flow in flows if flow.is_active)
            inactive_flows = total_flows - active_flows
            
            # Calculate task statistics
            task_types = {}
            for flow in flows:
                if flow.config_details and 'nodes' in flow.config_details:
                    for node in flow.config_details['nodes']:
                        task_type = node.get('data', {}).get('type', 'unknown')
                        task_types[task_type] = task_types.get(task_type, 0) + 1
            
            return {
                'flows': {
                    'total': total_flows,
                    'active': active_flows,
                    'inactive': inactive_flows
                },
                'tasks': {
                    'by_type': task_types
                }
            }
        except Exception as e:
            logger.error(f"Error getting flow statistics: {str(e)}")
            raise 