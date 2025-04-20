"""
YAML-based DAG builder implementation.
"""
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path

from airflow import DAG
from airflow.models import BaseOperator

from orchestration.airflow_plugin.plugin_core.dag_builder.base import ConfigBasedDAGBuilder
from orchestration.airflow_plugin.plugin_core.dag_builder.yaml_loader import YAMLConfigurationLoader
from orchestration.airflow_plugin.plugin_core.dag_builder.registry import OperatorRegistry

class YAMLDAGBuilder(ConfigBasedDAGBuilder):
    """Builder for creating DAGs from YAML configuration files."""
    
    def __init__(self, yaml_path: str):
        super().__init__()
        self.yaml_path = Path(yaml_path)
        self._load_yaml()
    
    def _load_yaml(self) -> None:
        """Load YAML configuration."""
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {self.yaml_path}")
            
        with open(self.yaml_path) as f:
            self.config = yaml.safe_load(f)
    
    def _get_dag_config(self) -> Optional[Dict[str, Any]]:
        """Get DAG configuration from YAML."""
        return self.config.get('dag')
    
    def _get_task_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get task configurations from YAML."""
        return self.config.get('tasks', {})
    
    def _get_dependencies(self) -> List[Dict[str, Any]]:
        """Get task dependencies from YAML."""
        return self.config.get('dependencies', [])
    
    def build(self) -> Optional[DAG]:
        """
        Build an Airflow DAG from YAML configuration.
        
        Returns:
            An Airflow DAG instance or None if configuration not found
        """
        # Get DAG configuration
        dag_config = self._get_dag_config()
        if not dag_config:
            return None
            
        # Create DAG
        dag = self._create_dag(dag_config)
        
        # Get tasks
        task_configs = self._get_task_configs()
        
        # Create task operators
        task_operators = {}
        for task_id, task_config in task_configs.items():
            operator = self._create_task_operator(
                task_type=task_config['task_type'],
                task_id=task_id,
                config=task_config['config'],
                dag=dag
            )
            if operator:
                task_operators[task_id] = operator
        
        # Set up dependencies
        dependencies = self._get_dependencies()
        self._setup_dependencies(task_operators, dependencies)
        
        return dag
        
    def _setup_dependencies(self, operators: Dict[str, BaseOperator], dependencies: List[Dict[str, Any]]) -> None:
        """
        Set up task dependencies from YAML configuration.
        
        Args:
            operators: Dictionary mapping task IDs to operators
            dependencies: List of task dependencies
        """
        for dep in dependencies:
            upstream_id = dep['upstream_task_id']
            downstream_id = dep['downstream_task_id']
            
            if upstream_id in operators and downstream_id in operators:
                operators[upstream_id] >> operators[downstream_id]
        
    def _create_dag(self, config: Dict[str, Any]) -> DAG:
        """Create DAG instance from configuration."""
        return DAG(
            dag_id=config['dag_id'],
            description=config.get('description', ''),
            schedule_interval=config.get('schedule_interval'),
            default_args=config.get('default_args', {}),
            catchup=config.get('catchup', False),
            tags=config.get('tags', []),
            max_active_runs=config.get('max_active_runs', 1)
        )
        
    def _create_task_operator(self, task_type: str, task_id: str, config: Dict[str, Any], dag: DAG) -> Optional[BaseOperator]:
        """Create an operator instance."""
        factory = self.operator_factories.get(task_type)
        if not factory:
            return None
        return factory.create_operator(task_id, config, dag) 