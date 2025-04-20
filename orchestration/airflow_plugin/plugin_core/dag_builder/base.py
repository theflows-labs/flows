"""
Base classes for the DAG builder.
"""
from typing import Dict, List, Any, Optional, Callable, Type
from abc import ABC, abstractmethod
import logging
from datetime import datetime, timedelta
import json

from airflow import DAG
from airflow.models import BaseOperator
from airflow.utils.dates import days_ago

from core.repositories import FlowConfigurationRepository, TaskConfigurationRepository, TaskDependencyRepository
from core.models import FlowConfiguration, TaskConfiguration, TaskDependency

logger = logging.getLogger(__name__)

class OperatorFactory(ABC):
    """
    Abstract base class for operator factories.
    """
    
    @classmethod
    @abstractmethod
    def get_operator_class(cls, task_type: str) -> Type[BaseOperator]:
        """
        Get the operator class for a task type.
        
        Args:
            task_type: The task type identifier
            
        Returns:
            The operator class
        """
        pass
    
    @abstractmethod
    def create_operator(self, task_config: TaskConfiguration, dag: DAG) -> BaseOperator:
        """
        Create an operator from task configuration.
        
        Args:
            task_config: The task configuration
            dag: The DAG instance
            
        Returns:
            An operator instance
        """
        pass
    
    @classmethod
    def get_required_parameters(cls) -> List[str]:
        """
        Get the list of required parameters for this operator.
        
        Returns:
            A list of required parameter names
        """
        return []
    
    @classmethod
    def get_optional_parameters(cls) -> Dict[str, Any]:
        """
        Get the optional parameters and their default values for this operator.
        
        Returns:
            A dictionary of optional parameter names and their default values
        """
        return {}
    
    @classmethod
    def get_parameter_descriptions(cls) -> Dict[str, str]:
        """
        Get descriptions for all parameters of this operator.
        
        Returns:
            A dictionary of parameter names and their descriptions
        """
        return {}
    
    @classmethod
    def get_parameter_types(cls) -> Dict[str, Type]:
        """
        Get the types of all parameters for this operator.
        
        Returns:
            A dictionary of parameter names and their types
        """
        return {}
    
    @classmethod
    def get_parameter_examples(cls) -> Dict[str, Any]:
        """
        Get example values for all parameters of this operator.
        
        Returns:
            A dictionary of parameter names and example values
        """
        return {}
    
    @classmethod
    def get_parameter_documentation(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get complete documentation for all parameters of this operator.
        
        Returns:
            A dictionary containing complete parameter documentation:
            {
                "param_name": {
                    "required": bool,
                    "type": Type,
                    "default": Any,
                    "description": str,
                    "example": Any
                }
            }
        """
        required_params = cls.get_required_parameters()
        optional_params = cls.get_optional_parameters()
        descriptions = cls.get_parameter_descriptions()
        types = cls.get_parameter_types()
        examples = cls.get_parameter_examples()
        
        documentation = {}
        
        # Add required parameters
        for param in required_params:
            documentation[param] = {
                "required": True,
                "type": types.get(param, str),
                "description": descriptions.get(param, ""),
                "example": examples.get(param, None)
            }
        
        # Add optional parameters
        for param, default in optional_params.items():
            documentation[param] = {
                "required": False,
                "type": types.get(param, str),
                "default": default,
                "description": descriptions.get(param, ""),
                "example": examples.get(param, None)
            }
        
        return documentation
    
    def _parse_config_details(self, config_details: Any) -> Dict[str, Any]:
        """
        Parse configuration details from task configuration.
        
        Args:
            config_details: The configuration details
            
        Returns:
            A dictionary of parsed configuration details
        """
        if isinstance(config_details, str):
            try:
                return json.loads(config_details)
            except json.JSONDecodeError as e:
                logger.error(f"Error parsing configuration details: {str(e)}")
                raise ValueError(f"Invalid configuration details: {str(e)}")
        elif isinstance(config_details, dict):
            return config_details
        else:
            raise ValueError(f"Invalid configuration details type: {type(config_details)}")
    
    def _validate_parameters(self, config_details: Dict[str, Any]) -> None:
        """
        Validate that all required parameters are present and have correct types.
        
        Args:
            config_details: The configuration details to validate
            
        Raises:
            ValueError: If validation fails
        """
        required_params = self.get_required_parameters()
        param_types = self.get_parameter_types()
        
        # Check required parameters
        for param in required_params:
            if param not in config_details:
                raise ValueError(f"Missing required parameter: {param}")
            
            # Check parameter type if specified
            if param in param_types:
                expected_type = param_types[param]
                actual_value = config_details[param]
                if not isinstance(actual_value, expected_type):
                    raise ValueError(
                        f"Parameter {param} must be of type {expected_type.__name__}, "
                        f"got {type(actual_value).__name__}"
                    )
    
    def _apply_defaults(self, config_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply default values for optional parameters.
        
        Args:
            config_details: The configuration details
            
        Returns:
            Updated configuration details with defaults applied
        """
        optional_params = self.get_optional_parameters()
        result = config_details.copy()
        
        for param, default in optional_params.items():
            if param not in result:
                result[param] = default
        
        return result


class BaseDAGBuilder(ABC):
    """Abstract base class for DAG builders."""
    
    def __init__(self):
        self.operator_factories: Dict[str, OperatorFactory] = {}
    
    def register_operator_factory(self, task_type: str, factory: OperatorFactory) -> None:
        """Register an operator factory for a task type."""
        self.operator_factories[task_type] = factory
    
    @abstractmethod
    def build(self) -> Optional[DAG]:
        """Build and return a DAG."""
        pass
    
    def _create_task_operator(self, task_type: str, task_id: str, config: Dict[str, Any], dag: DAG) -> Optional[BaseOperator]:
        """Create an operator instance."""
        factory = self.operator_factories.get(task_type)
        if not factory:
            return None
        return factory.create_operator(task_id, config, dag)


class ConfigBasedDAGBuilder(BaseDAGBuilder):
    """Base class for configuration-based DAG builders."""
    
    @abstractmethod
    def _get_dag_config(self) -> Optional[Dict[str, Any]]:
        """Get the DAG configuration."""
        pass
    
    @abstractmethod
    def _get_task_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get task configurations."""
        pass
    
    @abstractmethod
    def _get_dependencies(self) -> List[Dict[str, Any]]:
        """Get task dependencies."""
        pass
    
    def build(self) -> Optional[DAG]:
        """Build DAG from configuration."""
        # Get configurations
        dag_config = self._get_dag_config()
        if not dag_config:
            return None
            
        # Create DAG
        dag = self._create_dag(dag_config)
        
        # Create tasks
        task_operators = {}
        task_configs = self._get_task_configs()
        
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
    
    def _setup_dependencies(self, operators: Dict[str, BaseOperator], dependencies: List[Dict[str, Any]]) -> None:
        """Set up task dependencies."""
        for dep in dependencies:
            upstream_id = dep['upstream_task_id']
            downstream_id = dep['downstream_task_id']
            
            if upstream_id in operators and downstream_id in operators:
                operators[upstream_id] >> operators[downstream_id]

class DAGBuilder(ConfigBasedDAGBuilder):
    """Concrete DAG builder for database-backed configurations."""
    
    def __init__(self, flow_id: str):
        super().__init__()
        self.flow_id = flow_id
        self.flow_repo = FlowConfigurationRepository()
        self.task_repo = TaskConfigurationRepository()
        self.dep_repo = TaskDependencyRepository()
    
    def _get_dag_config(self) -> Optional[Dict[str, Any]]:
        """Get DAG configuration from database."""
        flow_config = self.flow_repo.get_flow_config_by_id(self.flow_id)
        if not flow_config:
            return None
            
        return {
            'dag_id': flow_config.flow_id,
            'description': flow_config.description,
            'schedule_interval': flow_config.config_details.get('schedule_interval'),
            'default_args': flow_config.config_details.get('default_args', {}),
            'catchup': flow_config.config_details.get('catchup', False),
            'tags': flow_config.config_details.get('tags', []),
            'max_active_runs': flow_config.config_details.get('max_active_runs', 1)
        }
    
    def _get_task_configs(self) -> Dict[str, Dict[str, Any]]:
        """Get task configurations from database."""
        tasks = self.task_repo.get_task_configs_by_flow_id(self.flow_id)
        return {
            str(task.task_id): {
                'task_type': task.task_type,
                'config': task.config_details
            }
            for task in tasks
            if task.is_active
        }
    
    def _get_dependencies(self) -> List[Dict[str, Any]]:
        """Get task dependencies from database."""
        deps = self.dep_repo.get_dependencies_by_flow_id(self.flow_id)
        return [
            {
                'upstream_task_id': str(dep.task_id),
                'downstream_task_id': str(dep.depends_on_task_id)
            }
            for dep in deps
            if dep.is_active
        ] 