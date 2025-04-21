"""
YAML-based DAG builder implementation.
"""
import yaml
from typing import Dict, Any, Optional, List
from pathlib import Path
import logging
from datetime import datetime

from airflow import DAG
from airflow.models import BaseOperator

from orchestration.airflow_plugin.plugin_core.dag_builder.base import ConfigBasedDAGBuilder
from orchestration.airflow_plugin.plugin_core.dag_builder.registry import OperatorRegistry

logger = logging.getLogger(__name__)

class YAMLDAGBuilder(ConfigBasedDAGBuilder):
    """Builder for creating DAGs from YAML configuration files."""
    
    def __init__(self, yaml_path: str):
        super().__init__()
        self.yaml_path = Path(yaml_path)
        
        # Get factories from registry
        registry = OperatorRegistry.register_factories()
        for task_type, factory_class in registry._factories.items():
            self.register_operator_factory(task_type, factory_class())
        
        self._load_yaml()
    
    def _load_yaml(self) -> None:
        """Load YAML configuration."""
        if not self.yaml_path.exists():
            raise FileNotFoundError(f"YAML file not found: {self.yaml_path}")
            
        with open(self.yaml_path) as f:
            self.config = yaml.safe_load(f)
            
        # Validate YAML version
        version = self.config.get('version')
        if version != "1.0":
            logger.warning(f"Unexpected YAML version: {version}")
            
        # Validate required sections
        if 'flow' not in self.config:
            raise ValueError("Missing required 'flow' section in YAML")
            
        if 'metadata' not in self.config:
            raise ValueError("Missing required 'metadata' section in YAML")
    
    def _get_dag_config(self) -> Optional[Dict[str, Any]]:
        """Get DAG configuration from YAML."""
        if not self.config or 'flow' not in self.config:
            return None
            
        flow = self.config['flow']
        metadata = self.config.get('metadata', {})
        
        return {
            'dag_id': flow.get('id'),
            'description': flow.get('description', ''),
            'schedule_interval': None,  # Can be added as a flow parameter if needed
            'default_args': {
                'owner': 'airflow',
                'start_date': datetime.fromisoformat(metadata.get('created_at', '').replace('Z', '+00:00')),
                'depends_on_past': False,
                'email_on_failure': False,
                'email_on_retry': False,
                'retries': 1
            },
            'catchup': False,
            'tags': ['theflows'],
            'max_active_runs': 1
        }
    
    def _get_task_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get task configurations from YAML."""
        tasks = {}
        flow_tasks = self.config.get('flow', {}).get('tasks', [])
        
        for task in flow_tasks:
            task_id = str(task.get('id'))  # Convert ID to string for Airflow
            if task_id:
                tasks[task_id] = {
                    'task_type': task.get('type'),
                    'name': task.get('name'),
                    'description': task.get('description'),
                    'config': task.get('config', {}),
                    'sequence': task.get('sequence', 1)
                }
        return tasks
    
    def _get_dependencies(self) -> List[Dict[str, Any]]:
        """Get task dependencies from YAML."""
        deps = []
        flow_deps = self.config.get('flow', {}).get('dependencies', [])
        
        for dep in flow_deps:
            deps.append({
                'upstream_task_id': str(dep.get('from')),  # Convert ID to string
                'downstream_task_id': str(dep.get('to')),  # Convert ID to string
                'dependency_type': dep.get('type', 'success'),
                'condition': dep.get('condition')
            })
        return deps
    
    def build(self) -> Optional[DAG]:
        """
        Build an Airflow DAG from YAML configuration.
        
        Returns:
            An Airflow DAG instance or None if configuration not found
        """
        # Get DAG configuration
        dag_config = self._get_dag_config()
        if not dag_config:
            logger.error("Failed to get DAG configuration from YAML")
            return None
            
        # Create DAG
        dag = self._create_dag(dag_config)
        
        # Get tasks
        task_configs = self._get_task_configs()
        
        # Create task operators
        task_operators = {}
        for task_id, task_config in task_configs.items():
            try:
                operator = self._create_task_operator(
                    task_type=task_config['task_type'],
                    task_id=task_id,
                    config=task_config['config'],
                    dag=dag
                )
                if operator:
                    # Set task name and description if available
                    if task_config.get('name'):
                        operator.task_name = task_config['name']
                    if task_config.get('description'):
                        operator.doc_md = task_config['description']
                    task_operators[task_id] = operator
                else:
                    logger.warning(f"Failed to create operator for task {task_id}")
            except Exception as e:
                logger.error(f"Error creating operator for task {task_id}: {str(e)}")
        
        # Set up dependencies
        dependencies = self._get_dependencies()
        for dep in dependencies:
            try:
                upstream_id = dep['upstream_task_id']
                downstream_id = dep['downstream_task_id']
                dep_type = dep['dependency_type']
                
                if upstream_id in task_operators and downstream_id in task_operators:
                    if dep_type == 'success':
                        task_operators[upstream_id] >> task_operators[downstream_id]
                    # Add support for other dependency types if needed
                else:
                    logger.warning(f"Missing tasks for dependency: {upstream_id} -> {downstream_id}")
            except Exception as e:
                logger.error(f"Error setting up dependency: {str(e)}")
        
        return dag
        
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
            logger.error(f"No operator factory found for task type: {task_type}")
            return None
        logger.info(f"got operator factory: {factory}")
        return factory.create_operator(task_id, config, dag) 