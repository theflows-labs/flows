"""
Registry for operator factories.
"""
from typing import Dict, Type, Optional, List, Any
import logging
import importlib
import pkgutil
import inspect
import os
import sys

from orchestration.airflow_plugin.plugin_core.dag_builder.base import OperatorFactory

logger = logging.getLogger(__name__)

class OperatorRegistry:
    """Registry for operator factories."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OperatorRegistry, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self._factories: Dict[str, Type[OperatorFactory]] = {}
        self._initialized = True
        logger.info("Initialized new OperatorRegistry instance")
    
    @classmethod
    def register_factories(cls):
        """
        Register all operator factories by discovering them from the airflow_plugin/plugins directory.
        This is a class method that can be called without instantiating the class.
        """
        registry = cls()
        logger.info("Starting operator factory registration")
        
        try:
            # Get the absolute path to the plugins directory
            plugins_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'plugins'))
            logger.info(f"Plugin directory to scan: {plugins_dir}")
            
            # Add parent directory to Python path if not already there
            parent_dir = os.path.dirname(os.path.dirname(plugins_dir))
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
                logger.info(f"Added {parent_dir} to Python path")
            
            # Discover factories from the plugins directory
            if os.path.exists(plugins_dir):
                task_types = registry.discover_factories_from_directory(plugins_dir)
                logger.info(f"Found {len(task_types)} task types")
                
                # Log discovered task types
                for task_type in task_types:
                    logger.info(f"Discovered task type: {task_type['type_key']} from {task_type['plugin_source']}")
            else:
                logger.error(f"Plugins directory not found: {plugins_dir}")
                return registry
            
            # Add built-in operators (like BashOperator)
            registry.register_builtin_operators()
            
            # Log all registered factories
            registered_types = list(registry._factories.keys())
            logger.info(f"Total registered operator factories: {len(registered_types)}")
            logger.info(f"Registered task types: {registered_types}")
            
        except Exception as e:
            logger.error(f"Error during factory registration: {str(e)}", exc_info=True)
        
        return registry
    
    def register_builtin_operators(self):
        """Register built-in Airflow operators that don't need discovery."""
        try:
            # Import required classes
            from airflow.models import BaseOperator
            from airflow.operators.bash import BashOperator
            from typing import Dict, Any, Type
            
            # Create factory for BashOperator
            class BashOperatorFactory(OperatorFactory):
                TASK_TYPE = "bash"
                
                @classmethod
                def get_operator_class(cls, task_type: str) -> Type[BaseOperator]:
                    return BashOperator
                    
                def create_operator(self, task_id: str, config: Dict[str, Any], dag: Any) -> BaseOperator:
                    return BashOperator(
                        task_id=task_id,
                        dag=dag,
                        **config
                    )
                    
                @classmethod
                def get_config_schema(cls) -> Dict[str, Any]:
                    return {
                        "type": "object",
                        "properties": {
                            "bash_command": {
                                "type": "string",
                                "description": "The command to execute"
                            },
                            "env": {
                                "type": "object",
                                "description": "Environment variables",
                                "additionalProperties": {"type": "string"},
                                "default": {}
                            }
                        },
                        "required": ["bash_command"]
                    }
            
            # Register the BashOperator factory
            self.register("bash", BashOperatorFactory)
            logger.info("Registered built-in BashOperator factory")
            
        except Exception as e:
            logger.error(f"Error registering built-in operators: {str(e)}", exc_info=True)
    
    def discover_factories_from_directory(self, directory: str) -> List[Dict[str, Any]]:
        """
        Discover operator factories from a directory.
        
        Args:
            directory: The directory to scan for operator factories
            
        Returns:
            List of discovered task type information
        """
        task_types = []
        logger.info(f"Starting factory discovery in directory: {directory}")
        
        try:
            # Add the parent directory to Python path for proper imports
            parent_dir = os.path.dirname(directory)
            if parent_dir not in sys.path:
                sys.path.insert(0, parent_dir)
                logger.info(f"Added to Python path: {parent_dir}")
            
            # Walk through the directory
            for root, dirs, files in os.walk(directory):
                if '__pycache__' in root:
                    continue
                    
                logger.debug(f"Scanning directory: {root}")
                
                # Get the module path relative to the plugins directory
                rel_path = os.path.relpath(root, parent_dir)
                package_name = rel_path.replace(os.sep, '.')
                
                # Process Python files
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        module_name = file[:-3]
                        full_module_name = f"{package_name}.{module_name}"
                        
                        try:
                            logger.debug(f"Importing module: {full_module_name}")
                            module = importlib.import_module(full_module_name)
                            
                            # Look for operator factory classes
                            for name, obj in inspect.getmembers(module):
                                if (inspect.isclass(obj) and 
                                    issubclass(obj, OperatorFactory) and 
                                    obj != OperatorFactory):
                                    
                                    task_type = getattr(obj, 'TASK_TYPE', None)
                                    if task_type:
                                        logger.info(f"Found operator factory: {name} with task type: {task_type}")
                                        
                                        # Create factory instance
                                        factory = obj()
                                        
                                        # Get task type information
                                        task_type_info = {
                                            'type_key': task_type,
                                            'name': obj.__name__,
                                            'description': obj.__doc__ or '',
                                            'plugin_source': full_module_name,
                                            'config_schema': factory.get_config_schema() if hasattr(factory, 'get_config_schema') else {},
                                            'default_config': factory.get_default_config() if hasattr(factory, 'get_default_config') else {},
                                            'icon': factory.get_icon() if hasattr(factory, 'get_icon') else None
                                        }
                                        
                                        # Register the factory
                                        self.register(task_type, obj)
                                        task_types.append(task_type_info)
                                        
                                        logger.info(f"Successfully registered task type: {task_type}")
                                    else:
                                        logger.warning(f"Class {name} has no TASK_TYPE attribute")
                                        
                        except ImportError as e:
                            logger.error(f"ImportError for module {full_module_name}: {str(e)}")
                        except Exception as e:
                            logger.error(f"Error processing module {full_module_name}: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error during factory discovery: {str(e)}", exc_info=True)
        
        logger.info(f"Discovery complete. Found {len(task_types)} task types")
        return task_types
    
    def register(self, task_type: str, factory_class: Type[OperatorFactory]) -> None:
        """
        Register an operator factory for a task type.
        
        Args:
            task_type: The task type identifier
            factory_class: The operator factory class
        """
        self._factories[task_type] = factory_class
        logger.info(f"Registered operator factory for task type: {task_type}")
    
    def get_factory(self, task_type: str) -> Optional[Type[OperatorFactory]]:
        """
        Get an operator factory for a task type.
        
        Args:
            task_type: The task type identifier
            
        Returns:
            The operator factory class or None if not found
        """
        return self._factories.get(task_type)
    
    def create_factory(self, task_type: str) -> Optional[OperatorFactory]:
        """
        Create an operator factory instance for a task type.
        
        Args:
            task_type: The task type identifier
            
        Returns:
            An operator factory instance or None if not found
        """
        factory_class = self.get_factory(task_type)
        if factory_class:
            return factory_class()
        return None
    
    def discover_factories(self, package_name: str) -> None:
        """
        Discover operator factories in a package.
        
        Args:
            package_name: The package name
        """
        try:
            package = importlib.import_module(package_name)
            
            # Handle both package and module cases
            if hasattr(package, '__path__'):
                # This is a package
                for _, name, is_pkg in pkgutil.iter_modules(package.__path__, package.__name__ + '.'):
                    if is_pkg:
                        self.discover_factories(name)
                    else:
                        try:
                            module = importlib.import_module(name)
                            self._process_module(module)
                        except ImportError as e:
                            logger.warning(f"Could not import module {name}: {str(e)}")
            else:
                # This is a module
                self._process_module(package)
        except ImportError as e:
            logger.error(f"Error discovering operator factories in package {package_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Error discovering operator factories: {str(e)}")
    
    def _process_module(self, module) -> None:
        """
        Process a module to find operator factories.
        
        Args:
            module: The module to process
        """
        for _, obj in inspect.getmembers(module):
            if (inspect.isclass(obj) and 
                issubclass(obj, OperatorFactory) and 
                obj != OperatorFactory):
                
                # Get task type from class
                task_type = getattr(obj, 'TASK_TYPE', None)
                if task_type:
                    self.register(task_type, obj)
                    logger.info(f"Discovered operator factory {obj.__name__} with task type {task_type}")
                else:
                    logger.warning(f"Operator factory {obj.__name__} has no TASK_TYPE attribute")
    
    def get_all_task_types(self) -> list:
        """
        Get all registered task types.
        
        Returns:
            A list of task type identifiers
        """
        return list(self._factories.keys()) 