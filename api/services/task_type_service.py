from typing import List, Dict, Optional, Any
from core.repositories.repository import TaskTypeRepository
from orchestration.airflow_plugin.plugin_core.dag_builder.registry import OperatorRegistry
import os
import logging

logger = logging.getLogger(__name__)

class TaskTypeService:
    def __init__(self):
        self.task_type_repo = TaskTypeRepository()

    def get_task_types(self) -> List[Dict[str, Any]]:
        """Get all active task types."""
        return self.task_type_repo.get_all_active_task_types()

    def create_task_type(self, task_type_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task type with validation."""
        self._validate_task_type(task_type_data)
        return self.task_type_repo.upsert_task_type(**task_type_data)

    def update_task_type(self, type_key: str, task_type_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing task type."""
        self._validate_task_type(task_type_data)
        task_type_data['type_key'] = type_key
        return self.task_type_repo.upsert_task_type(**task_type_data)

    def _validate_task_type(self, task_type_data: Dict[str, Any]) -> None:
        """Validate task type configuration."""
        required_fields = ['name', 'type_key', 'config_schema']
        missing_fields = [f for f in required_fields if f not in task_type_data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Validate config schema
        config_schema = task_type_data.get('config_schema', {})
        if not isinstance(config_schema, dict):
            raise ValueError("Config schema must be a dictionary")
        if 'type' not in config_schema:
            raise ValueError("Config schema must specify a type")
        if 'properties' not in config_schema:
            raise ValueError("Config schema must specify properties")

    def deactivate_task_type(self, type_key: str) -> bool:
        """Deactivate a task type."""
        return self.task_type_repo.deactivate_task_type(type_key)

    def get_task_type(self, type_key: str) -> Optional[Dict]:
        """Get a specific task type by key."""
        return self.task_type_repo.get_task_type_by_key(type_key)

    @staticmethod
    def _task_type_to_dict(task_type) -> Dict:
        """Convert TaskType model to dictionary."""
        return {
            'type_id': task_type.type_id,
            'name': task_type.name,
            'type_key': task_type.type_key,
            'description': task_type.description,
            'plugin_source': task_type.plugin_source,
            'config_schema': task_type.config_schema,
            'default_config': task_type.default_config,
            'icon': task_type.icon,
            'created_dt': task_type.created_dt.isoformat(),
            'updated_dt': task_type.updated_dt.isoformat(),
            'is_active': task_type.is_active
        }

    def refresh_task_types(self) -> List[Dict[str, Any]]:
        """
        Refresh task types by scanning plugins and updating the database.
        """
        try:
            # Create a new registry instance
            registry = OperatorRegistry.register_factories()
            
            # Get task types from the registry
            task_types_info = registry.discover_factories_from_directory(
                os.path.join(os.path.dirname(__file__), '..', '..', 'orchestration', 'airflow_plugin', 'plugins')
            )
            
            # Update task types in the database
            updated_types = []
            for task_type_info in task_types_info:
                try:
                    updated_type = self.task_type_repo.upsert_task_type(**{
                        'type_key': task_type_info['type_key'],
                        'name': task_type_info['name'],
                        'description': task_type_info['description'],
                        'plugin_source': task_type_info['plugin_source'],
                        'config_schema': task_type_info['config_schema'],
                        'default_config': task_type_info.get('default_config', {}),
                        'icon': task_type_info.get('icon', 'extension'),
                        'is_active': True
                    })
                    updated_types.append(updated_type)
                except Exception as e:
                    logger.error(f"Error updating task type {task_type_info['type_key']}: {str(e)}")
                    continue
            
            logger.info(f"Successfully refreshed {len(updated_types)} task types")
            return updated_types
        except Exception as e:
            logger.error(f"Error during task type refresh: {str(e)}")
            raise ValueError(f"Failed to refresh task types: {str(e)}") 