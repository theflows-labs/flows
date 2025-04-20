from typing import List, Dict, Optional
from core.repositories.repository import TaskTypeRepository
from orchestration.airflow_plugin.plugin_core.dag_builder.registry import OperatorRegistry
import os
import logging

logger = logging.getLogger(__name__)

class TaskTypeService:
    def __init__(self):
        self.task_type_repo = TaskTypeRepository()
        self.registry = OperatorRegistry()

    def refresh_task_types(self) -> List[Dict]:
        """Scan plugins and refresh task types in the database."""
        # Get the plugins directory path
        plugins_dir = os.path.abspath(os.path.join(
            os.path.dirname(__file__), 
            '..', '..',  
            'orchestration',
            'airflow_plugin',
            'plugins'
        ))
        
        logger.info(f"Starting task type refresh from directory: {plugins_dir}")
        logger.info(f"Directory exists: {os.path.exists(plugins_dir)}")
        logger.info(f"Directory contents: {os.listdir(plugins_dir)}")

        # Use registry to discover all task types
        registry = OperatorRegistry.register_factories()
        task_types = registry.discover_factories_from_directory(plugins_dir)
        
        logger.info(f"Discovered {len(task_types)} task types")
        for tt in task_types:
            logger.info(f"Task Type found: {tt.get('name')} ({tt.get('type_key')})")

        # Update database
        updated_types = []
        for task_type in task_types:
            try:
                updated = self.task_type_repo.upsert_task_type(**task_type)
                updated_types.append(updated)
                logger.info(f"Successfully updated task type: {task_type.get('type_key')}")
            except Exception as e:
                logger.error(f"Error upserting task type {task_type.get('type_key')}: {str(e)}")
        
        logger.info(f"Total task types updated in database: {len(updated_types)}")
        return updated_types

    def get_task_types(self) -> List[Dict]:
        """Get all active task types."""
        return self.task_type_repo.get_all_active_task_types()

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