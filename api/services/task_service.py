from typing import Dict, List, Optional, Any
from core.repositories.repository import TaskConfigurationRepository
from core.models.models import TaskConfiguration
import yaml


class TaskService:
    # Define available task types and their configurations
    TASK_TYPES = {
        'python': {
            'name': 'Python Task',
            'description': 'Execute a Python function',
            'config_schema': {
                'type': 'object',
                'properties': {
                    'python_callable': {
                        'type': 'string',
                        'description': 'Python function to execute'
                    },
                    'op_args': {
                        'type': 'array',
                        'description': 'Positional arguments to pass to the function'
                    },
                    'op_kwargs': {
                        'type': 'object',
                        'description': 'Keyword arguments to pass to the function'
                    }
                },
                'required': ['python_callable']
            }
        },
        'bash': {
            'name': 'Bash Task',
            'description': 'Execute a bash command',
            'config_schema': {
                'type': 'object',
                'properties': {
                    'bash_command': {
                        'type': 'string',
                        'description': 'Bash command to execute'
                    }
                },
                'required': ['bash_command']
            }
        },
        'sql': {
            'name': 'SQL Task',
            'description': 'Execute a SQL query',
            'config_schema': {
                'type': 'object',
                'properties': {
                    'sql': {
                        'type': 'string',
                        'description': 'SQL query to execute'
                    },
                    'conn_id': {
                        'type': 'string',
                        'description': 'Connection ID to use'
                    }
                },
                'required': ['sql', 'conn_id']
            }
        },
        'http': {
            'name': 'HTTP Task',
            'description': 'Make an HTTP request',
            'config_schema': {
                'type': 'object',
                'properties': {
                    'url': {
                        'type': 'string',
                        'description': 'URL to make request to'
                    },
                    'method': {
                        'type': 'string',
                        'enum': ['GET', 'POST', 'PUT', 'DELETE'],
                        'description': 'HTTP method'
                    }
                },
                'required': ['url', 'method']
            }
        },
        'docker': {
            'name': 'Docker Task',
            'description': 'Run a Docker container',
            'config_schema': {
                'type': 'object',
                'properties': {
                    'image': {
                        'type': 'string',
                        'description': 'Docker image to run'
                    },
                    'command': {
                        'type': 'string',
                        'description': 'Command to run in container'
                    }
                },
                'required': ['image']
            }
        }
    }

    def __init__(self):
        self.task_repo = TaskConfigurationRepository()

    @classmethod
    def get_task(cls, task_id: int) -> Optional[Dict[str, Any]]:
        """Get a task by ID."""
        service = cls()
        task = service.task_repo.get_task_config(task_id)
        if task:
            return service._task_to_dict(task)
        return None

    @classmethod
    def update_task(cls, task_id: int, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a task."""
        service = cls()
        
        # Validate task configuration if provided
        if 'config_details' in data:
            task = service.task_repo.get_task_config(task_id)
            if task and task.task_type in cls.TASK_TYPES:
                cls._validate_config(
                    data['config_details'],
                    cls.TASK_TYPES[task.task_type]['config_schema']
                )

        # Convert to YAML if not provided
        yaml_content = data.get('config_details_yaml')
        if not yaml_content and data.get('config_details'):
            yaml_content = yaml.dump(data['config_details'], default_flow_style=False)

        task = service.task_repo.update_task_config(
            task_id=task_id,
            config_details=data.get('config_details'),
            config_details_yaml=yaml_content,
            description=data.get('description')
        )
        return service._task_to_dict(task) if task else None

    @classmethod
    def get_task_types(cls) -> List[Dict[str, Any]]:
        """Get available task types with their schemas."""
        return [
            {
                'type': task_type,
                'name': config['name'],
                'description': config['description'],
                'config_schema': config['config_schema']
            }
            for task_type, config in cls.TASK_TYPES.items()
        ]

    @staticmethod
    def _validate_config(config: Dict[str, Any], schema: Dict[str, Any]) -> None:
        """Validate task configuration against its schema."""
        properties = schema.get('properties', {})
        required = schema.get('required', [])

        # Check required fields
        for field in required:
            if field not in config:
                raise ValueError(f"Missing required field: {field}")

        # Validate field types and values
        for field, value in config.items():
            if field in properties:
                field_schema = properties[field]
                expected_type = field_schema['type']

                # Type validation
                if expected_type == 'string' and not isinstance(value, str):
                    raise ValueError(f"Field {field} must be a string")
                elif expected_type == 'array' and not isinstance(value, list):
                    raise ValueError(f"Field {field} must be an array")
                elif expected_type == 'object' and not isinstance(value, dict):
                    raise ValueError(f"Field {field} must be an object")

                # Enum validation
                if 'enum' in field_schema and value not in field_schema['enum']:
                    raise ValueError(f"Field {field} must be one of {field_schema['enum']}")

    @staticmethod
    def _task_to_dict(task: TaskConfiguration) -> Dict[str, Any]:
        """Convert a TaskConfiguration model to a dictionary."""
        return {
            'task_id': task.task_id,
            'task_type': task.task_type,
            'flow_config_id': task.flow_config_id,
            'task_sequence': task.task_sequence,
            'config_details': task.config_details,
            'config_details_yaml': task.config_details_yaml,
            'description': task.description,
            'created_dt': task.created_dt.isoformat() if task.created_dt else None,
            'updated_dt': task.updated_dt.isoformat() if task.updated_dt else None,
            'is_active': task.is_active
        }