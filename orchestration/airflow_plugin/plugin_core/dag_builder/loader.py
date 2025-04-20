"""
DAG loader for dynamically loading DAGs from the database.
"""
import logging
from typing import Dict, List, Optional, Any, Union
import importlib
import pkgutil
import inspect
from pathlib import Path

from airflow import DAG
from airflow.models import BaseOperator

from core.repositories import FlowConfigurationRepository
from orchestration.airflow_plugin.plugin_core.dag_builder.base import DAGBuilder
from orchestration.airflow_plugin.plugin_core.dag_builder.registry import OperatorRegistry
from .base import BaseDAGBuilder
from .yaml_builder import YAMLDAGBuilder

logger = logging.getLogger(__name__)

class DAGLoader:
    """Loader for dynamically loading DAGs from the database."""
    
    def __init__(self):
        """Initialize the DAG loader."""
        self.registry = OperatorRegistry()
        self._dag_builders: Dict[str, DAGBuilder] = {}
    
    def load_dags(self) -> Dict[str, DAG]:
        """
        Load all active DAGs from the database.
        
        Returns:
            A dictionary mapping DAG IDs to DAG instances
        """
        # Get all active DAG configurations from the repository
        flow_repo = FlowConfigurationRepository()
        flow_configs = flow_repo.get_all_active_flow_configs()
        
        # Load DAGs
        dags = {}
        for flow_config in flow_configs:
            try:
                dag = self.load_dag(flow_config.flow_id)
                if dag:
                    dags[dag.dag_id] = dag
            except Exception as e:
                logger.error(f"Error loading DAG {flow_config.flow_id}: {str(e)}")
        
        return dags
    
    def load_dag(self, flow_id: str) -> Optional[DAG]:
        """
        Load a DAG from the database.
        
        Args:
            flow_id: The ID of the flow configuration
            
        Returns:
            An Airflow DAG instance or None if not found
        """
        try:
            # Get DAG builder
            builder = self._get_dag_builder(flow_id)
            if not builder:
                return None
            
            # Build DAG
            return builder.build()
        except Exception as e:
            logger.error(f"Error loading DAG with flow ID {flow_id}: {str(e)}")
            return None
    
    def _get_dag_builder(self, flow_id: str) -> Optional[DAGBuilder]:
        """
        Get a DAG builder for a flow configuration.
        
        Args:
            flow_id: The ID of the flow configuration
            
        Returns:
            A DAG builder instance or None if not found
        """
        # Check if builder already exists
        if flow_id in self._dag_builders:
            return self._dag_builders[flow_id]
        
        # Create builder
        builder = DAGBuilder(flow_id)
        
        # Register operator factories
        self._register_operator_factories(builder)
        
        # Cache builder
        self._dag_builders[flow_id] = builder
        
        return builder
    
    def _register_operator_factories(self, builder: DAGBuilder) -> None:
        """
        Register operator factories with a DAG builder.
        
        Args:
            builder: The DAG builder
        """
        # Register factories using the registry
        registry = OperatorRegistry.register_factories()
        
        # Get all task types
        task_types = registry.get_all_task_types()
        
        # Register factories with the builder
        for task_type in task_types:
            factory = registry.create_factory(task_type)
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
    
    def load_from_yaml(self, yaml_path: Union[str, Path]) -> Optional[DAG]:
        """Load DAG from YAML configuration."""
        try:
            builder = YAMLDAGBuilder(str(yaml_path))
            self._register_operator_factories(builder)
            return builder.build()
        except Exception as e:
            logger.error(f"Error loading DAG from YAML {yaml_path}: {str(e)}")
            return None
    
    def load_from_database(self, flow_id: str) -> Optional[DAG]:
        """Load DAG from database configuration."""
        try:
            builder = DatabaseDAGBuilder(flow_id)
            self._register_operator_factories(builder)
            return builder.build()
        except Exception as e:
            logger.error(f"Error loading DAG from database for flow {flow_id}: {str(e)}")
            return None 