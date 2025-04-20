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
        # if not registry._factories:
        #     logger.info("No factories discovered automatically. Manually registering known factories.")
            
        #     # Manually import and register the known operator factories
        #     try:
        #         # Import S3 operator factories
        #         from plugins.aws.s3.operators.s3_operations import (
        #             S3CopyObjectOperatorFactory,
        #             S3PutObjectOperatorFactory,
        #             S3ListOperatorFactory,
        #             S3DeleteObjectsOperatorFactory
        #         )
                
        #         # Import Athena operator factories
        #         from plugins.aws.athena.operators.athena_query import (
        #             AthenaQueryOperatorFactory
        #         )
                
        #         # Register the factories
        #         registry.register(S3CopyObjectOperatorFactory.TASK_TYPE, S3CopyObjectOperatorFactory)
        #         registry.register(S3PutObjectOperatorFactory.TASK_TYPE, S3PutObjectOperatorFactory)
        #         registry.register(S3ListOperatorFactory.TASK_TYPE, S3ListOperatorFactory)
        #         registry.register(S3DeleteObjectsOperatorFactory.TASK_TYPE, S3DeleteObjectsOperatorFactory)
        #         registry.register(AthenaQueryOperatorFactory.TASK_TYPE, AthenaQueryOperatorFactory)
                
        #         logger.info("Successfully registered operator factories manually.")
        #     except ImportError as e:
        #         logger.error(f"Error importing operator factories: {str(e)}")
        
        # Log the discovered factories
        logger.info(f"Discovered {len(registry._factories)} operator factories: {list(registry._factories.keys())}")
        
        return registry
    
    def discover_factories_from_directory(self, directory: str) -> List[Dict[str, Any]]:
        """
        Discover operator factories and return task type information.
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

                logger.info(f"Scanning directory: {root}")
                logger.info(f"Found directories: {dirs}")
                logger.info(f"Found files: {files}")

                # Get the module path relative to the plugins directory
                rel_path = os.path.relpath(root, parent_dir)
                package_name = rel_path.replace(os.sep, '.')
                
                logger.info(f"Processing package: {package_name}")

                # Process Python files
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        module_name = file[:-3]
                        full_module_name = f"{package_name}.{module_name}"
                        
                        logger.info(f"Attempting to import module: {full_module_name}")
                        
                        try:
                            module = importlib.import_module(full_module_name)
                            logger.info(f"Successfully imported module: {full_module_name}")
                            
                            # Look for operator factory classes
                            for name, obj in inspect.getmembers(module):
                                logger.debug(f"Inspecting member: {name}")
                                
                                try:
                                    if (inspect.isclass(obj) and 
                                        issubclass(obj, OperatorFactory) and 
                                        obj != OperatorFactory):
                                        
                                        logger.info(f"Found operator factory class: {name}")
                                        
                                        task_type = getattr(obj, 'TASK_TYPE', None)
                                        if task_type:
                                            logger.info(f"Found task type: {task_type}")
                                            
                                            # Create an instance to get task type info
                                            factory = obj()
                                            task_type_info = {
                                                'type_key': task_type,
                                                'name': obj.__name__,
                                                'description': obj.__doc__ or '',
                                                'plugin_source': full_module_name,
                                                'config_schema': factory.get_config_schema(),
                                                'default_config': factory.get_default_config(),
                                                'icon': factory.get_icon() if hasattr(factory, 'get_icon') else 'airflow'
                                            }
                                            
                                            # Register the factory and collect task type info
                                            self.register(task_type, obj)
                                            task_types.append(task_type_info)
                                            
                                            logger.info(f"Successfully registered task type: {task_type}")
                                        else:
                                            logger.warning(f"Class {name} has no TASK_TYPE attribute")
                                except Exception as e:
                                    logger.error(f"Error processing class {name}: {str(e)}")
                        
                        except ImportError as e:
                            logger.error(f"ImportError for module {full_module_name}: {str(e)}")
                            logger.error(f"Current sys.path: {sys.path}")
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