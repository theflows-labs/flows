"""
Registry for operator factories.
"""
from typing import Dict, Type, Optional
import logging
import importlib
import pkgutil
import inspect
import os
import sys

from flows.plugin_core.dag_builder.base import OperatorFactory

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
    
    @classmethod
    def register_factories(cls):
        """
        Register all operator factories.
        This is a class method that can be called without instantiating the class.
        """
        registry = cls()
        
        # Get the absolute path to the plugins directory
        plugins_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'plugins'))

        logger.info(plugins_dir)
        
        # Add the plugins directory to the Python path if it's not already there
        if plugins_dir not in sys.path:
            sys.path.insert(0, os.path.dirname(plugins_dir))
        
        # Try to discover factories automatically
        registry.discover_factories_from_directory(plugins_dir)
        
        # If no factories were discovered, manually register the known factories
        if not registry._factories:
            logger.info("No factories discovered automatically. Manually registering known factories.")
            
            # Manually import and register the known operator factories
            try:
                # Import S3 operator factories
                from plugins.aws.s3.operators.s3_operations import (
                    S3CopyObjectOperatorFactory,
                    S3PutObjectOperatorFactory,
                    S3ListOperatorFactory,
                    S3DeleteObjectsOperatorFactory
                )
                
                # Import Athena operator factories
                from plugins.aws.athena.operators.athena_query import (
                    AthenaQueryOperatorFactory
                )
                
                # Register the factories
                registry.register(S3CopyObjectOperatorFactory.TASK_TYPE, S3CopyObjectOperatorFactory)
                registry.register(S3PutObjectOperatorFactory.TASK_TYPE, S3PutObjectOperatorFactory)
                registry.register(S3ListOperatorFactory.TASK_TYPE, S3ListOperatorFactory)
                registry.register(S3DeleteObjectsOperatorFactory.TASK_TYPE, S3DeleteObjectsOperatorFactory)
                registry.register(AthenaQueryOperatorFactory.TASK_TYPE, AthenaQueryOperatorFactory)
                
                logger.info("Successfully registered operator factories manually.")
            except ImportError as e:
                logger.error(f"Error importing operator factories: {str(e)}")
        
        # Log the discovered factories
        logger.info(f"Discovered {len(registry._factories)} operator factories: {list(registry._factories.keys())}")
        
        return registry
    
    def discover_factories_from_directory(self, directory: str) -> None:
        """
        Discover operator factories in a directory.
        
        Args:
            directory: The directory to search
        """
        try:
            # Walk through the directory
            for root, dirs, files in os.walk(directory):
                # Skip __pycache__ directories
                if '__pycache__' in root:
                    continue
                
                # Get the relative path from the plugins directory
                rel_path = os.path.relpath(root, os.path.dirname(directory))
                package_name = rel_path.replace(os.sep, '.')
                
                # Check for Python files in the current directory
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        # Get the module name (without .py extension)
                        module_name = file[:-3]
                        full_module_name = f"{package_name}.{module_name}" if package_name else module_name
                        
                        try:
                            # Import the module
                            module = importlib.import_module(full_module_name)
                            
                            # Look for operator factories in the module
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
                        except ImportError as e:
                            logger.warning(f"Could not import module {full_module_name}: {str(e)}")
                        except Exception as e:
                            logger.error(f"Error processing module {full_module_name}: {str(e)}")
                
                # Also check if this is a Python package for nested packages
                if '__init__.py' in files:
                    try:
                        self.discover_factories(package_name)
                    except ImportError as e:
                        logger.warning(f"Could not import package {package_name}: {str(e)}")
        except Exception as e:
            logger.error(f"Error discovering operator factories in directory {directory}: {str(e)}")
    
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