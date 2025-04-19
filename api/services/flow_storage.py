from typing import Dict, List, Optional, Any
import yaml
import os
from pathlib import Path
from datetime import datetime
from core.repositories.repository import FlowConfigurationRepository, TaskConfigurationRepository
from core.models.models import FlowConfiguration, TaskConfiguration

class FlowStorage:
    def __init__(self, base_dir: str = "flows"):
        """Initialize flow storage with base directory for YAML files."""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.flow_repo = FlowConfigurationRepository()
        self.task_repo = TaskConfigurationRepository()

    def save_flow_yaml(self, flow_id: str, yaml_content: str) -> Dict[str, Any]:
        """Save flow configuration as YAML file and store in database."""
        # Save to YAML file
        flow_path = self.base_dir / f"{flow_id}.yaml"
        flow_path.write_text(yaml_content)

        # Parse YAML content
        flow_config = yaml.safe_load(yaml_content)

        # Store in database
        db_flow = self.flow_repo.get_flow_config_by_flow_id(flow_id)
        if db_flow:
            # Update existing flow
            updated_flow = self.flow_repo.update_flow_config(
                config_id=db_flow.config_id,
                config_details=flow_config,
                config_details_yaml=yaml_content,
                description=flow_config.get('description')
            )
            return self._flow_to_dict(updated_flow)
        else:
            # Create new flow
            new_flow = self.flow_repo.create_flow_config(
                flow_id=flow_id,
                config_details=flow_config,
                config_details_yaml=yaml_content,
                description=flow_config.get('description')
            )
            return self._flow_to_dict(new_flow)

    def load_flow_yaml(self, flow_id: str) -> Optional[str]:
        """Load flow configuration from YAML file."""
        flow_path = self.base_dir / f"{flow_id}.yaml"
        if flow_path.exists():
            return flow_path.read_text()
        return None

    def delete_flow_yaml(self, flow_id: str) -> bool:
        """Delete flow YAML file and database entry."""
        # Delete YAML file
        flow_path = self.base_dir / f"{flow_id}.yaml"
        if flow_path.exists():
            flow_path.unlink()

        # Delete from database
        flow = self.flow_repo.get_flow_config_by_flow_id(flow_id)
        if flow:
            return self.flow_repo.delete_flow_config(flow.config_id)
        return True

    def list_flows(self) -> List[str]:
        """List all flow YAML files."""
        return [f.stem for f in self.base_dir.glob("*.yaml")]

    def sync_flows(self) -> Dict[str, List[str]]:
        """Synchronize YAML files with database."""
        yaml_flows = set(self.list_flows())
        db_flows = set(flow.flow_id for flow in self.flow_repo.get_all_active_flow_configs())

        # Flows to add to DB (exist in YAML but not in DB)
        to_add = yaml_flows - db_flows
        added = []
        for flow_id in to_add:
            yaml_content = self.load_flow_yaml(flow_id)
            if yaml_content:
                self.save_flow_yaml(flow_id, yaml_content)
                added.append(flow_id)

        # Flows to remove from DB (exist in DB but not in YAML)
        to_remove = db_flows - yaml_flows
        removed = []
        for flow_id in to_remove:
            flow = self.flow_repo.get_flow_config_by_flow_id(flow_id)
            if flow:
                self.flow_repo.delete_flow_config(flow.config_id)
                removed.append(flow_id)

        return {
            'added': added,
            'removed': removed
        }

    @staticmethod
    def _flow_to_dict(flow: FlowConfiguration) -> Dict[str, Any]:
        """Convert flow configuration to dictionary."""
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