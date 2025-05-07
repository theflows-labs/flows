"""
Base classes for the DAG builder.
"""
from typing import Dict, List, Any, Optional, Callable, Type
from abc import ABC, abstractmethod
import logging
from datetime import datetime, timedelta
import json
from dataclasses import dataclass, field
from pydantic import BaseModel, Field

from airflow import DAG
from airflow.models import BaseOperator
from airflow.utils.dates import days_ago

from core.repositories import FlowConfigurationRepository, TaskConfigurationRepository, TaskDependencyRepository
from core.models import FlowConfiguration, TaskConfiguration, TaskDependency

logger = logging.getLogger(__name__)

class OperatorParams(BaseModel):
    """Base class for operator parameters using Pydantic for validation."""
    task_id: str = Field(..., description="Task ID")
    class Config:
        arbitrary_types_allowed = True

    @classmethod
    def get_parameter_documentation(cls) -> Dict[str, Dict[str, Any]]:
        """Get complete documentation for all parameters."""
        schema = cls.schema()
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        documentation = {}
        for param_name, param_info in properties.items():
            documentation[param_name] = {
                "required": param_name in required,
                "type": param_info.get('type', 'string'),
                "default": param_info.get('default'),
                "description": param_info.get('description', ''),
                "example": param_info.get('example')
            }
        return documentation

class OperatorFactory(ABC):
    """
    Abstract base class for operator factories.
    """
    TASK_TYPE = "base"
    params_class = OperatorParams
    
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
        raise NotImplementedError("Subclasses must implement get_operator_class")
    
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
    def get_parameter_documentation(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get complete documentation for all parameters of this operator.
        
        Returns:
            A dictionary containing complete parameter documentation
        """
        return cls.params_class.get_parameter_documentation()
    
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
    
    def _validate_and_parse_params(self, config_details: Dict[str, Any]) -> OperatorParams:
        """
        Validate and parse configuration details into operator parameters.
        
        Args:
            config_details: The configuration details to validate
            
        Returns:
            An instance of the operator's params class
            
        Raises:
            ValueError: If validation fails
        """
        try:
            return self.params_class(**config_details)
        except Exception as e:
            logger.error(f"Error validating parameters: {str(e)}")
            raise ValueError(f"Invalid parameters: {str(e)}")
    
    def _create_operator(self, task_config: TaskConfiguration, dag: DAG, **kwargs) -> BaseOperator:
        """
        Create an operator instance with validated parameters.
        
        Args:
            task_config: The task configuration
            dag: The DAG instance
            **kwargs: Additional arguments for the operator
            
        Returns:
            An operator instance
        """
        config_details = self._parse_config_details(task_config.config_details)
        params = self._validate_and_parse_params(config_details)
        
        operator_class = self.get_operator_class(task_config.task_type)
        return operator_class(
            task_id=task_config.task_id,
            dag=dag,
            **params.dict(),
            **kwargs
        )

    @classmethod
    def get_config_schema(cls) -> Dict[str, Any]:
        """Get the configuration schema for the task type"""
        # Get the schema from the Pydantic model
        schema = cls.params_class.schema()
        
        # Remove task_id from schema as it's handled separately
        if 'properties' in schema:
            schema['properties'].pop('task_id', None)
        if 'required' in schema:
            schema['required'] = [f for f in schema['required'] if f != 'task_id']
            
        # Add title and description from class docstring
        schema['title'] = cls.__name__.replace('Factory', '')
        schema['description'] = cls.__doc__ or ''
        
        # Ensure proper JSON Schema format
        schema['type'] = 'object'
        if 'properties' not in schema:
            schema['properties'] = {}
            
        return schema

    @classmethod
    def get_default_config(cls) -> Dict[str, Any]:
        """Get the default configuration values for the task type"""
        # Create an instance with default values, excluding task_id
        schema = cls.params_class.schema()
        properties = schema.get('properties', {})
        required = schema.get('required', [])
        
        # Build default config with only non-required fields
        default_config = {}
        for field_name, field_info in properties.items():
            if field_name != 'task_id':  # Skip task_id as it's handled separately
                if field_name not in required:
                    default_value = field_info.get('default')
                    if default_value is not None:
                        default_config[field_name] = default_value
                    elif field_info.get('type') == 'object':
                        default_config[field_name] = {}
                    elif field_info.get('type') == 'array':
                        default_config[field_name] = []
        
        return default_config

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