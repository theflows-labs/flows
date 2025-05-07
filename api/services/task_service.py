from typing import Dict, List, Optional, Any
from core.repositories.repository import TaskConfigurationRepository, TaskDependencyRepository, FlowConfigurationRepository
from core.models.models import TaskConfiguration, TaskDependency
from .task_type_service import TaskTypeService
import yaml


class TaskService:
    def __init__(self):
        self.task_repo = TaskConfigurationRepository()
        self.dependency_repo = TaskDependencyRepository()
        self.flow_repo = FlowConfigurationRepository()
        self.task_type_service = TaskTypeService()

    @classmethod
    def get_task(cls, task_id: int) -> Optional[Dict[str, Any]]:
        """Get a task by ID."""
        service = cls()
        task = service.task_repo.get_task_config(task_id)
        if task:
            return service._task_to_dict(task)
        return None

    @classmethod
    def create_task(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task configuration."""
        service = cls()
        
        # Convert to YAML if not provided
        yaml_content = data.get('config_details_yaml')
        if not yaml_content and data.get('config_details'):
            yaml_content = yaml.dump(data['config_details'], default_flow_style=False)

        task = service.task_repo.create_task_config(
            flow_config_id=data['flow_config_id'],
            task_type=data['task_type'],
            task_sequence=data['task_sequence'],
            config_details=data['config_details'],
            config_details_yaml=yaml_content,
            description=data.get('description')
        )
        return service._task_to_dict(task)

    @classmethod
    def update_task(cls, task_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a task configuration."""
        service = cls()
        
        # Convert to YAML if not provided
        yaml_content = data.get('config_details_yaml')
        if not yaml_content and data.get('config_details'):
            yaml_content = yaml.dump(data['config_details'], default_flow_style=False)

        task = service.task_repo.update_task_config(
            task_id=task_id,
            config_details=data.get('config_details'),
            config_details_yaml=yaml_content,
            description=data.get('description')
        )
        return service._task_to_dict(task) if task else None

    @classmethod
    def create_dependency(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task dependency."""
        service = cls()
        dependency = service.dependency_repo.create_dependency(
            flow_config_id=data['flow_config_id'],
            task_id=data['task_id'],
            depends_on_task_id=data['depends_on_task_id'],
            dependency_type=data.get('dependency_type', 'success')
        )
        return service._dependency_to_dict(dependency)

    @classmethod
    def update_dependency(cls, dependency_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a task dependency."""
        service = cls()
        dependency = service.dependency_repo.update_dependency(
            dependency_id=dependency_id,
            dependency_type=data.get('dependency_type'),
            condition=data.get('condition')
        )
        return service._dependency_to_dict(dependency) if dependency else None

    @classmethod
    def get_tasks_by_flow_config(cls, flow_config_id: int) -> List[Dict[str, Any]]:
        """Get all tasks for a flow configuration."""
        service = cls()
        tasks = service.task_repo.get_task_configs_by_flow_config(flow_config_id)
        return [service._task_to_dict(task) for task in tasks]

    @classmethod
    def get_dependencies_by_flow(cls, flow_config_id: int) -> List[Dict[str, Any]]:
        """Get all dependencies for a flow configuration."""
        service = cls()
        dependencies = service.dependency_repo.get_dependencies_by_flow(flow_config_id)
        return [service._dependency_to_dict(dep) for dep in dependencies]

    @classmethod
    def get_tasks_by_flow_id(cls, flow_id: str) -> List[Dict[str, Any]]:
        """Get all tasks for a flow by its flow_id."""
        service = cls()
        flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
        if not flow:
            return []
        tasks = service.task_repo.get_task_configs_by_flow_config(flow.config_id)
        return [service._task_to_dict(task) for task in tasks]

    @classmethod
    def get_task_types(cls) -> List[Dict[str, Any]]:
        """Get available task types with their schemas."""
        service = cls()
        return service.task_type_service.get_task_types()

    @staticmethod
    def _validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Validate task configuration against its schema."""
        properties = schema.get('properties', {})
        required = schema.get('required', [])

        # Check required fields
        for field in required:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")

        # Validate field types and values
        for field, value in config.items():
            if field in properties:
                field_schema = properties[field]
                expected_type = field_schema['type']

                # Type validation
                if expected_type == 'string' and not isinstance(value, str):
                    raise ValueError(f"Field {field} must be a string")
                elif expected_type == 'array' and not isinstance(value, list):
                    raise ValueError(f"Field {field} must be an array")
                elif expected_type == 'object' and not isinstance(value, dict):
                    raise ValueError(f"Field {field} must be an object")

                # Enum validation
                if 'enum' in field_schema and value not in field_schema['enum']:
                    raise ValueError(f"Field {field} must be one of {field_schema['enum']}")

    @staticmethod
    def _task_to_dict(task: TaskConfiguration) -> Dict[str, Any]:
        """Convert a TaskConfiguration model to a dictionary."""
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

    @staticmethod
    def _dependency_to_dict(dependency: TaskDependency) -> Dict[str, Any]:
        """Convert a TaskDependency model to a dictionary."""
        return {
            'dependency_id': dependency.dependency_id,
            'flow_config_id': dependency.flow_config_id,
            'task_id': dependency.task_id,
            'depends_on_task_id': dependency.depends_on_task_id,
            'dependency_type': dependency.dependency_type,
            'condition': dependency.condition,
            'created_dt': dependency.created_dt.isoformat() if dependency.created_dt else None,
            'updated_dt': dependency.updated_dt.isoformat() if dependency.updated_dt else None,
            'is_active': dependency.is_active
        }