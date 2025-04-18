from flask import Blueprint, request, jsonify
from .services.dag_service import DAGService
from .services.task_service import TaskService
from .services.execution_service import ExecutionService

dag_bp = Blueprint('dag', __name__)
task_bp = Blueprint('task', __name__)
execution_bp = Blueprint('execution', __name__)

# DAG Routes
@dag_bp.route('/', methods=['GET'])
def get_dags():
    dags = DAGService.get_all_dags()
    return jsonify(dags)

@dag_bp.route('/<dag_id>', methods=['GET'])
def get_dag(dag_id):
    dag = DAGService.get_dag(dag_id)
    return jsonify(dag)

@dag_bp.route('/', methods=['POST'])
def create_dag():
    data = request.json
    dag = DAGService.create_dag(data)
    return jsonify(dag), 201

@dag_bp.route('/<dag_id>', methods=['PUT'])
def update_dag(dag_id):
    data = request.json
    dag = DAGService.update_dag(dag_id, data)
    return jsonify(dag)

@dag_bp.route('/<dag_id>', methods=['DELETE'])
def delete_dag(dag_id):
    DAGService.delete_dag(dag_id)
    return '', 204

@dag_bp.route('/<dag_id>/yaml', methods=['GET'])
def get_dag_yaml(dag_id):
    yaml_content = DAGService.get_dag_yaml(dag_id)
    return jsonify({'content': yaml_content})

# Task Routes
@task_bp.route('/types', methods=['GET'])
def get_task_types():
    types = TaskService.get_task_types()
    return jsonify(types)

@task_bp.route('/<task_id>', methods=['GET'])
def get_task(task_id):
    task = TaskService.get_task(task_id)
    return jsonify(task)

@task_bp.route('/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    task = TaskService.update_task(task_id, data)
    return jsonify(task)

# Execution Routes
@execution_bp.route('/<dag_id>', methods=['POST'])
def trigger_execution(dag_id):
    execution = ExecutionService.trigger_execution(dag_id)
    return jsonify(execution), 201

@execution_bp.route('/<execution_id>', methods=['GET'])
def get_execution_status(execution_id):
    status = ExecutionService.get_execution_status(execution_id)
    return jsonify(status)

@execution_bp.route('/<execution_id>/logs', methods=['GET'])
def get_execution_logs(execution_id):
    logs = ExecutionService.get_execution_logs(execution_id)
    return jsonify(logs) 