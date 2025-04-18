import os
import json
from ..models.dag import DAG

class DAGStorage:
    BASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
    DAGS_DIR = os.path.join(BASE_DIR, 'dags')
    YAML_DIR = os.path.join(BASE_DIR, 'yaml')

    @staticmethod
    def _ensure_directories():
        os.makedirs(DAGStorage.DAGS_DIR, exist_ok=True)
        os.makedirs(DAGStorage.YAML_DIR, exist_ok=True)

    @staticmethod
    def get_all_dags():
        DAGStorage._ensure_directories()
        dags = []
        for filename in os.listdir(DAGStorage.DAGS_DIR):
            if filename.endswith('.json'):
                with open(os.path.join(DAGStorage.DAGS_DIR, filename), 'r') as f:
                    dag_data = json.load(f)
                    dags.append(DAG.from_dict(dag_data).to_dict())
        return dags

    @staticmethod
    def get_dag(dag_id):
        DAGStorage._ensure_directories()
        filepath = os.path.join(DAGStorage.DAGS_DIR, f'{dag_id}.json')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return DAG.from_dict(json.load(f))
        return None

    @staticmethod
    def save_dag(dag):
        DAGStorage._ensure_directories()
        filepath = os.path.join(DAGStorage.DAGS_DIR, f'{dag.id}.json')
        with open(filepath, 'w') as f:
            json.dump(dag.to_dict(), f, indent=2)

    @staticmethod
    def delete_dag(dag_id):
        DAGStorage._ensure_directories()
        filepath = os.path.join(DAGStorage.DAGS_DIR, f'{dag_id}.json')
        if os.path.exists(filepath):
            os.remove(filepath)

    @staticmethod
    def save_dag_yaml(dag_id, yaml_content):
        DAGStorage._ensure_directories()
        filepath = os.path.join(DAGStorage.YAML_DIR, f'{dag_id}.yaml')
        with open(filepath, 'w') as f:
            f.write(yaml_content)

    @staticmethod
    def get_dag_yaml(dag_id):
        DAGStorage._ensure_directories()
        filepath = os.path.join(DAGStorage.YAML_DIR, f'{dag_id}.yaml')
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return f.read()
        return None

    @staticmethod
    def delete_dag_yaml(dag_id):
        DAGStorage._ensure_directories()
        filepath = os.path.join(DAGStorage.YAML_DIR, f'{dag_id}.yaml')
        if os.path.exists(filepath):
            os.remove(filepath) 