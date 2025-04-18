"""
YAML-based configuration loader for DAGs.
"""
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging

from core.models import (
    DAGConfiguration,
    TaskConfiguration,
    TaskDependency
)

logger = logging.getLogger(__name__)

class YAMLConfigurationLoader:
    """Loader for DAG configurations from YAML files."""
    
    def __init__(self, config_path: str):
        """
        Initialize the YAML configuration loader.
        
        Args:
            config_path: Path to the YAML configuration file
        """
        self.config_path = Path(config_path)
        self._config_data = None
        
    def load_config(self) -> None:
        """Load the configuration from the YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self._config_data = yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading YAML configuration: {str(e)}")
            raise
            
    def get_dag_config(self, dag_id: str) -> Optional[DAGConfiguration]:
        """
        Get DAG configuration by ID.
        
        Args:
            dag_id: The DAG ID
            
        Returns:
            DAGConfiguration object or None if not found
        """
        if not self._config_data:
            self.load_config()
            
        dag_config = self._config_data.get('dags', {}).get(dag_id)
        if not dag_config:
            return None
            
        return DAGConfiguration(
            dag_id=dag_id,
            description=dag_config.get('description', ''),
            config_details=dag_config.get('config', {}),
            is_active=dag_config.get('is_active', True)
        )
        
    def get_task_configs_by_dag_config(self, dag_id: str) -> List[TaskConfiguration]:
        """
        Get all task configurations for a DAG.
        
        Args:
            dag_id: The DAG ID
            
        Returns:
            List of TaskConfiguration objects
        """
        if not self._config_data:
            self.load_config()
            
        tasks = []
        dag_config = self._config_data.get('dags', {}).get(dag_id, {})
        task_configs = dag_config.get('tasks', {})
        
        for task_id, task_config in task_configs.items():
            tasks.append(TaskConfiguration(
                task_id=task_id,
                dag_config_id=task_config.get('dag_config_id', 1),
                task_type=task_config.get('type', ''),
                config_details=task_config.get('config', {}),
                is_active=task_config.get('is_active', True)
            ))
            
        return tasks
        
    def get_dependencies_by_dag(self, dag_id: str) -> List[TaskDependency]:
        """
        Get all task dependencies for a DAG.
        
        Args:
            dag_id: The DAG ID
            
        Returns:
            List of TaskDependency objects
        """
        if not self._config_data:
            self.load_config()
            
        dependencies = []
        dag_config = self._config_data.get('dags', {}).get(dag_id, {})
        dep_configs = dag_config.get('dependencies', [])
        
        for dep_config in dep_configs:
            dependencies.append(TaskDependency(
                task_id=dep_config.get('task_id'),
                depends_on_task_id=dep_config.get('depends_on_task_id'),
                dependency_type=dep_config.get('type', 'success'),
                is_active=dep_config.get('is_active', True)
            ))
            
        return dependencies 