"""
DAG loader for dynamically loading DAGs from the database.
"""
import logging
from typing import Dict, List, Optional, Any
import importlib
import pkgutil
import inspect

from airflow import DAG
from airflow.models import BaseOperator

from flows.plugin_core.metadata import DAGConfigurationRepository
from flows.plugin_core.dag_builder.base import DAGBuilder
from flows.plugin_core.dag_builder.registry import OperatorRegistry

logger = logging.getLogger(__name__)

class DAGLoader:
    """Loader for dynamically loading DAGs from the database."""
    
    def __init__(self):
        """Initialize the DAG loader."""
        self.dag_repo = DAGConfigurationRepository()
        self.registry = OperatorRegistry()
        self._dag_builders: Dict[int, DAGBuilder] = {}
    
    def load_dags(self) -> Dict[str, DAG]:
        """
        Load all active DAGs from the database.
        
        Returns:
            A dictionary mapping DAG IDs to DAG instances
        """
        # Get all active DAG configurations
        dag_configs = self.dag_repo.get_all_active_dag_configs()
        
        # Load DAGs
        dags = {}
        for dag_config in dag_configs:
            try:
                dag = self.load_dag(dag_config.config_id)
                if dag:
                    dags[dag.dag_id] = dag
            except Exception as e:
                logger.error(f"Error loading DAG {dag_config.dag_id}: {str(e)}")
        
        return dags
    
    def load_dag(self, dag_config_id: int) -> Optional[DAG]:
        """
        Load a DAG from the database.
        
        Args:
            dag_config_id: The ID of the DAG configuration
            
        Returns:
            An Airflow DAG instance or None if not found
        """
        try:
            # Get DAG builder
            builder = self._get_dag_builder(dag_config_id)
            if not builder:
                return None
            
            # Build DAG
            return builder.build()
        except Exception as e:
            logger.error(f"Error loading DAG with config ID {dag_config_id}: {str(e)}")
            return None
    
    def _get_dag_builder(self, dag_config_id: int) -> Optional[DAGBuilder]:
        """
        Get a DAG builder for a DAG configuration.
        
        Args:
            dag_config_id: The ID of the DAG configuration
            
        Returns:
            A DAG builder instance or None if not found
        """
        # Check if builder already exists
        if dag_config_id in self._dag_builders:
            logger.info(f"DAG builder for {dag_config_id} already exists")
            return self._dag_builders[dag_config_id]
        
        # Create builder
        builder = DAGBuilder(dag_config_id)
        
        # Register operator factories
        self._register_operator_factories(builder)
        
        # Cache builder
        self._dag_builders[dag_config_id] = builder
        
        return builder
    
    def _register_operator_factories(self, builder: DAGBuilder) -> None:
        """
        Register operator factories with a DAG builder.
        
        Args:
            builder: The DAG builder
        """
        # Get all task types
        task_types = self.registry.get_all_task_types()
        
        # Register factories
        for task_type in task_types:
            factory = self.registry.create_factory(task_type)
            if factory:
                builder.register_operator_factory(task_type, factory)
    
    def discover_operator_factories(self, package_name: str) -> None:
        """
        Discover operator factories in a package.
        
        Args:
            package_name: The package name
        """
        self.registry.discover_factories(package_name)
    
    def register_operator_factory(self, task_type: str, factory_class: Any) -> None:
        """
        Register an operator factory for a task type.
        
        Args:
            task_type: The task type identifier
            factory_class: The operator factory class
        """
        self.registry.register(task_type, factory_class) 