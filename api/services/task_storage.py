import os
import json
from ..models.task import Task

class TaskStorage:
    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    TASKS_DIR = os.path.join(BASE_DIR, 'tasks')

    @staticmethod
    def _ensure_directories():
        os.makedirs(TaskStorage.TASKS_DIR, exist_ok=True)

    @staticmethod
    def get_task(task_id):
        TaskStorage._ensure_directories()
        filepath = os.path.join(TaskStorage.TASKS_DIR, f'{task_id}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return Task.from_dict(json.load(f))
        return None

    @staticmethod
    def get_tasks_by_dag(dag_id):
        TaskStorage._ensure_directories()
        tasks = []
        for filename in os.listdir(TaskStorage.TASKS_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(TaskStorage.TASKS_DIR, filename), 'r') as f:
                    task_data = json.load(f)
                    if task_data['dag_id'] == dag_id:
                        tasks.append(Task.from_dict(task_data))
        return tasks

    @staticmethod
    def save_task(task):
        TaskStorage._ensure_directories()
        filepath = os.path.join(TaskStorage.TASKS_DIR, f'{task.id}.json')
        with open(filepath, 'w') as f:
            json.dump(task.to_dict(), f, indent=2)

    @staticmethod
    def delete_task(task_id):
        TaskStorage._ensure_directories()
        filepath = os.path.join(TaskStorage.TASKS_DIR, f'{task_id}.json')
        if os.path.exists(filepath):
            os.remove(filepath)

    @staticmethod
    def delete_tasks_by_dag(dag_id):
        TaskStorage._ensure_directories()
        for filename in os.listdir(TaskStorage.TASKS_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(TaskStorage.TASKS_DIR, filename)
                with open(filepath, 'r') as f:
                    task_data = json.load(f)
                    if task_data['dag_id'] == dag_id:
                        os.remove(filepath) 