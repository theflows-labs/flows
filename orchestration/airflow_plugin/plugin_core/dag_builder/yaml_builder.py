"""
YAML-based DAG builder implementation.
"""
from typing import Dict, Optional
from pathlib import Path

from airflow import DAG
from airflow.models import BaseOperator

from orchestration.airflow_plugin.plugin_core.dag_builder.base import DAGBuilder, OperatorFactory
from orchestration.airflow_plugin.plugin_core.dag_builder.yaml_loader import YAMLConfigurationLoader
from orchestration.airflow_plugin.plugin_core.dag_builder.registry import OperatorRegistry

class YAMLDAGBuilder(DAGBuilder):
    """Builder for creating Airflow DAGs from YAML configuration."""
    
    def __init__(self, config_path: str, dag_id: str):
        """
        Initialize the YAML DAG builder.
        
        Args:
            config_path: Path to the YAML configuration file
            dag_id: The ID of the DAG to build
        """
        self.config_path = Path(config_path)
        self.dag_id = dag_id
        self.loader = YAMLConfigurationLoader(config_path)
        
        # Initialize the base DAGBuilder with a dummy ID since we're using YAML
        super().__init__(dag_id)
        
        # Register operator factories
        self._register_operator_factories()
        
    def _register_operator_factories(self) -> None:
        """Register operator factories with the builder."""
        # Get the operator registry
        registry = OperatorRegistry.register_factories()
        
        # Register all discovered factories
        for task_type in registry.get_all_task_types():
            factory = registry.create_factory(task_type)
            if factory:
                self.register_operator_factory(task_type, factory)
        
    def build(self) -> Optional[DAG]:
        """
        Build an Airflow DAG from YAML configuration.
        
        Returns:
            An Airflow DAG instance or None if configuration not found
        """
        # Get DAG configuration
        dag_config = self.loader.get_dag_config(self.dag_id)
        if not dag_config:
            return None
            
        # Create DAG
        dag = self._create_dag(dag_config, dag_config.config_details)
        
        # Get tasks
        tasks = self.loader.get_task_configs_by_dag_config(self.dag_id)
        
        # Create task operators
        task_operators = {}
        for task in tasks:
            if not task.is_active:
                continue
                
            operator = self._create_task_operator(task, dag)
            if operator:
                task_operators[task.task_id] = operator
        
        # Set up dependencies
        self._setup_dependencies(task_operators)
        
        return dag
        
    def _setup_dependencies(self, task_operators: Dict[str, BaseOperator]) -> None:
        """
        Set up task dependencies from YAML configuration.
        
        Args:
            task_operators: Dictionary mapping task IDs to operators
        """
        # Get dependencies
        dependencies = self.loader.get_dependencies_by_dag(self.dag_id)
        
        # Set up dependencies
        for dep in dependencies:
            if not dep.is_active:
                continue
                
            # Get operators
            task_operator = task_operators.get(dep.task_id)
            depends_on_operator = task_operators.get(dep.depends_on_task_id)
            
            if task_operator and depends_on_operator:
                # Set up dependency based on type
                if dep.dependency_type == 'success':
                    task_operator.set_upstream(depends_on_operator)
                elif dep.dependency_type == 'failure':
                    task_operator.set_upstream(depends_on_operator, trigger_rule='all_failed')
                elif dep.dependency_type == 'skip':
                    task_operator.set_upstream(depends_on_operator, trigger_rule='all_done')
                elif dep.dependency_type == 'all_done':
                    task_operator.set_upstream(depends_on_operator, trigger_rule='all_done')
                else:
                    # Default to success
                    task_operator.set_upstream(depends_on_operator) 