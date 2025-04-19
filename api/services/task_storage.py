from typing import Dict, List, Optional, Any
import yaml
from pathlib import Path
from core.repositories.repository import TaskConfigurationRepository, FlowConfigurationRepository
from core.models.models import TaskConfiguration

class TaskStorage:
    def __init__(self, base_dir: str = "tasks"):
        """Initialize task storage with base directory for YAML files."""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.task_repo = TaskConfigurationRepository()
        self.flow_repo = FlowConfigurationRepository()

    def save_task_yaml(self, flow_id: str, task_id: int, yaml_content: str) -> Dict[str, Any]:
        """Save task configuration as YAML file and store in database."""
        # Create flow directory if it doesn't exist
        flow_dir = self.base_dir / flow_id
        flow_dir.mkdir(parents=True, exist_ok=True)

        # Save to YAML file
        task_path = flow_dir / f"task_{task_id}.yaml"
        task_path.write_text(yaml_content)

        # Parse YAML content
        task_config = yaml.safe_load(yaml_content)

        # Get flow configuration
        flow = self.flow_repo.get_flow_config_by_flow_id(flow_id)
        if not flow:
            raise ValueError(f"Flow {flow_id} not found")

        # Update task in database
        task = self.task_repo.get_task_config(task_id)
        if task:
            updated_task = self.task_repo.update_task_config(
                task_id=task_id,
                config_details=task_config,
                config_details_yaml=yaml_content,
                description=task_config.get('description')
            )
            return self._task_to_dict(updated_task)
        else:
            raise ValueError(f"Task {task_id} not found")

    def load_task_yaml(self, flow_id: str, task_id: int) -> Optional[str]:
        """Load task configuration from YAML file."""
        task_path = self.base_dir / flow_id / f"task_{task_id}.yaml"
        if task_path.exists():
            return task_path.read_text()
        return None

    def delete_task_yaml(self, flow_id: str, task_id: int) -> bool:
        """Delete task YAML file."""
        task_path = self.base_dir / flow_id / f"task_{task_id}.yaml"
        if task_path.exists():
            task_path.unlink()
            return True
        return False

    def list_tasks(self, flow_id: str) -> List[int]:
        """List all task YAML files for a flow."""
        flow_dir = self.base_dir / flow_id
        if not flow_dir.exists():
            return []
        return [int(f.stem.split('_')[1]) for f in flow_dir.glob("task_*.yaml")]

    def sync_tasks(self, flow_id: str) -> Dict[str, List[int]]:
        """Synchronize task YAML files with database for a flow."""
        flow = self.flow_repo.get_flow_config_by_flow_id(flow_id)
        if not flow:
            raise ValueError(f"Flow {flow_id} not found")

        yaml_tasks = set(self.list_tasks(flow_id))
        db_tasks = set(task.task_id for task in self.task_repo.get_task_configs_by_flow_config(flow.config_id))

        # Tasks to update in DB (exist in YAML)
        updated = []
        for task_id in yaml_tasks:
            yaml_content = self.load_task_yaml(flow_id, task_id)
            if yaml_content and task_id in db_tasks:
                self.save_task_yaml(flow_id, task_id, yaml_content)
                updated.append(task_id)

        return {
            'updated': updated
        }

    @staticmethod
    def _task_to_dict(task: TaskConfiguration) -> Dict[str, Any]:
        """Convert task configuration to dictionary."""
        return {
            'task_id': task.task_id,
            'task_type': task.task_type,
            'flow_config_id': task.flow_config_id,
            'task_sequence': task.task_sequence,
            'config_details': task.config_details,
            'config_details_yaml': task.config_details_yaml,
            'description': task.description,
            'created_dt': task.created_dt.isoformat() if task.created_dt else None,
            'updated_dt': task.updated_dt.isoformat() if task.updated_dt else None,
            'is_active': task.is_active
        } 