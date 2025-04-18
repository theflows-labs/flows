import os
import json
from ..models.execution import Execution

class ExecutionStorage:
    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    EXECUTIONS_DIR = os.path.join(BASE_DIR, 'executions')

    @staticmethod
    def _ensure_directories():
        os.makedirs(ExecutionStorage.EXECUTIONS_DIR, exist_ok=True)

    @staticmethod
    def get_execution(execution_id):
        ExecutionStorage._ensure_directories()
        filepath = os.path.join(ExecutionStorage.EXECUTIONS_DIR, f'{execution_id}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return Execution.from_dict(json.load(f))
        return None

    @staticmethod
    def get_executions_by_dag(dag_id):
        ExecutionStorage._ensure_directories()
        executions = []
        for filename in os.listdir(ExecutionStorage.EXECUTIONS_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(ExecutionStorage.EXECUTIONS_DIR, filename), 'r') as f:
                    execution_data = json.load(f)
                    if execution_data['dag_id'] == dag_id:
                        executions.append(Execution.from_dict(execution_data))
        return executions

    @staticmethod
    def save_execution(execution):
        ExecutionStorage._ensure_directories()
        filepath = os.path.join(ExecutionStorage.EXECUTIONS_DIR, f'{execution.id}.json')
        with open(filepath, 'w') as f:
            json.dump(execution.to_dict(), f, indent=2)

    @staticmethod
    def delete_execution(execution_id):
        ExecutionStorage._ensure_directories()
        filepath = os.path.join(ExecutionStorage.EXECUTIONS_DIR, f'{execution_id}.json')
        if os.path.exists(filepath):
            os.remove(filepath)

    @staticmethod
    def delete_executions_by_dag(dag_id):
        ExecutionStorage._ensure_directories()
        for filename in os.listdir(ExecutionStorage.EXECUTIONS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(ExecutionStorage.EXECUTIONS_DIR, filename)
                with open(filepath, 'r') as f:
                    execution_data = json.load(f)
                    if execution_data['dag_id'] == dag_id:
                        os.remove(filepath) 