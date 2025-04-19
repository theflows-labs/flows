from typing import Dict, List, Optional, Any
from core.repositories.repository import FlowConfigurationRepository, TaskConfigurationRepository
from core.models.models import FlowConfiguration, TaskConfiguration
import yaml

class FlowService:
    def __init__(self):
        self.flow_repo = FlowConfigurationRepository()
        self.task_repo = TaskConfigurationRepository()

    @classmethod
    def get_all_flows(cls) -> List[Dict[str, Any]]:
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
        if flow:
            return flow.config_details_yaml
        return None

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