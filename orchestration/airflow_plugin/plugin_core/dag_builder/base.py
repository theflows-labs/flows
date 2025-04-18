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

from flows.plugin_core.metadata import DAGConfigurationRepository, TaskConfigurationRepository, TaskDependencyRepository
from flows.plugin_core.metadata.models import DAGConfiguration, TaskConfiguration, TaskDependency

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


class DAGBuilder:
    """Builder for creating Airflow DAGs from configuration."""
    
    def __init__(self, dag_config_id: int):
        """
        Initialize the DAG builder.
        
        Args:
            dag_config_id: The ID of the DAG configuration
        """
        self.dag_config_id = dag_config_id
        self.dag_repo = DAGConfigurationRepository()
        self.task_repo = TaskConfigurationRepository()
        self.dep_repo = TaskDependencyRepository()
        self.operator_factories: Dict[str, OperatorFactory] = {}
        
    def register_operator_factory(self, task_type: str, factory: OperatorFactory) -> None:
        """
        Register an operator factory for a task type.
        
        Args:
            task_type: The task type identifier
            factory: The operator factory
        """
        self.operator_factories[task_type] = factory
        
    def build(self) -> DAG:
        """
        Build an Airflow DAG from configuration.
        
        Returns:
            An Airflow DAG instance
        """
        # Get DAG configuration
        dag_config = self.dag_repo.get_dag_config(self.dag_config_id)
        if not dag_config:
            raise ValueError(f"DAG configuration with ID {self.dag_config_id} not found")
        
        # Parse DAG configuration
        config_details = dag_config.config_details
        if isinstance(config_details, str):
            config_details = json.loads(config_details)
        
        # Create DAG
        dag = self._create_dag(dag_config, config_details)
        
        # Get tasks
        tasks = self.task_repo.get_task_configs_by_dag_config(self.dag_config_id)
        
        # Create task operators
        task_operators = {}
        for task in tasks:
            if not task.is_active:
                continue
                
            operator = self._create_task_operator(task, dag)
            if operator:
                task_operators[int(task.task_id)] = operator  # Convert to int
        
        # Set up dependencies
        self._setup_dependencies(task_operators)
        
        return dag
    
    def _create_dag(self, dag_config: DAGConfiguration, config_details: Dict[str, Any]) -> DAG:
        """
        Create an Airflow DAG from configuration.
        
        Args:
            dag_config: The DAG configuration
            config_details: The DAG configuration details
            
        Returns:
            An Airflow DAG instance
        """
        # Default DAG arguments
        default_args = {
            'owner': 'airflow',
            'depends_on_past': False,
            'email_on_failure': False,
            'email_on_retry': False,
            'retries': 1,
            'retry_delay': timedelta(minutes=5),
        }
        
        # Override with configuration
        if 'default_args' in config_details:
            # Create a copy of default_args to avoid modifying the original
            default_args_copy = default_args.copy()
            
            # Update with configuration default_args
            for key, value in config_details['default_args'].items():
                # Special handling for start_date
                if key == 'start_date' and isinstance(value, str):
                    try:
                        # Try to parse as ISO format
                        value = datetime.fromisoformat(value)
                    except ValueError:
                        # If not ISO format, try days_ago format
                        if value.startswith('days_ago:'):
                            days = int(value.split(':')[1])
                            value = days_ago(days)
                        else:
                            # If not a recognized format, use days_ago(1)
                            value = days_ago(1)
                
                default_args_copy[key] = value
            
            default_args = default_args_copy
        
        # Get schedule interval
        schedule_interval = config_details.get('schedule_interval', '0 0 * * *')
        
        # Get start date from default_args
        start_date = default_args.get('start_date', days_ago(1))
        
        # Create DAG
        return DAG(
            dag_id=dag_config.dag_id,
            default_args=default_args,
            description=dag_config.description,
            schedule_interval=schedule_interval,
            start_date=start_date,
            catchup=config_details.get('catchup', False),
            tags=config_details.get('tags', []),
            max_active_runs=config_details.get('max_active_runs', 1),
        )
    
    def _create_task_operator(self, task_config: TaskConfiguration, dag: DAG) -> Optional[BaseOperator]:
        """
        Create an Airflow operator from task configuration.
        
        Args:
            task_config: The task configuration
            dag: The DAG instance
            
        Returns:
            An Airflow operator instance or None if no factory is registered
        """
        # Get operator factory
        factory = self.operator_factories.get(task_config.task_type)
        if not factory:
            logger.warning(f"No operator factory registered for task type: {task_config.task_type}")
            return None
        
        # Create operator
        try:
            return factory.create_operator(task_config, dag)
        except Exception as e:
            logger.error(f"Error creating operator for task {task_config.task_id}: {str(e)}")
            return None
    
    def _setup_dependencies(self, task_operators: Dict[int, BaseOperator]) -> None:
        """
        Set up task dependencies.
        
        Args:
            task_operators: Dictionary mapping task IDs to operators
        """
        # Get dependencies
        dependencies = self.dep_repo.get_dependencies_by_dag(self.dag_config_id)
        
        # Set up dependencies
        for dep in dependencies:
            if not dep.is_active:
                continue
                
            # Get operators
            task_operator = task_operators.get(int(dep.task_id))  # Convert to int
            depends_on_operator = task_operators.get(int(dep.depends_on_task_id))  # Convert to int
            
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