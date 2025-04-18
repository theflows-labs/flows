from ..models.task import Task
from ..config.db import SessionLocal
import uuid
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

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
        }
    }

    @staticmethod
    def get_task_types():
        return TaskService.TASK_TYPES

    @staticmethod
    def get_all_tasks():
        db = SessionLocal()
        try:
            return [task.to_dict() for task in db.query(Task).all()]
        finally:
            db.close()

    @staticmethod
    def get_task(task_id):
        db = SessionLocal()
        try:
            return db.query(Task).filter(Task.id == task_id).first()
        finally:
            db.close()

    @staticmethod
    def get_tasks_by_dag(dag_id):
        db = SessionLocal()
        try:
            return [task.to_dict() for task in db.query(Task).filter(Task.dag_id == dag_id).all()]
        finally:
            db.close()

    @staticmethod
    def create_task(data):
        db = SessionLocal()
        try:
            task = Task(
                id=str(uuid.uuid4()),
                dag_id=data.get('dag_id'),
                type=data['type'],
                config=data.get('config', {})
            )
            
            db.add(task)
            db.commit()
            db.refresh(task)
            return task
        finally:
            db.close()

    @staticmethod
    def update_task(task_id, data):
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if not task:
                return None
                
            task.type = data['type']
            task.config = data.get('config', {})
            task.updated_at = datetime.utcnow()
            
            db.commit()
            db.refresh(task)
            return task
        finally:
            db.close()

    @staticmethod
    def delete_task(task_id):
        db = SessionLocal()
        try:
            task = db.query(Task).filter(Task.id == task_id).first()
            if task:
                db.delete(task)
                db.commit()
        finally:
            db.close()

    @staticmethod
    def delete_tasks_by_dag(dag_id):
        db = SessionLocal()
        try:
            tasks = db.query(Task).filter(Task.dag_id == dag_id).all()
            for task in tasks:
                db.delete(task)
            db.commit()
        finally:
            db.close()

    @staticmethod
    def _validate_config(config, schema):
        for field, rules in schema.items():
            if rules.get('required', False) and field not in config:
                raise ValueError(f"Missing required field: {field}")

            if field in config:
                value = config[field]
                expected_type = rules['type']

                if expected_type == 'string' and not isinstance(value, str):
                    raise ValueError(f"Field {field} must be a string")
                elif expected_type == 'array' and not isinstance(value, list):
                    raise ValueError(f"Field {field} must be an array")
                elif expected_type == 'object' and not isinstance(value, dict):
                    raise ValueError(f"Field {field} must be an object")

                if 'enum' in rules and value not in rules['enum']:
                    raise ValueError(f"Field {field} must be one of {rules['enum']}") 