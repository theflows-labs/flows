from flask import Blueprint, request, jsonify
from ..services.task_service import TaskService

bp = Blueprint('tasks', __name__)

@bp.route('/', methods=['GET'])
def get_tasks():
    tasks = TaskService.get_all_tasks()
    return jsonify(tasks)

@bp.route('/<task_id>', methods=['GET'])
def get_task(task_id):
    task = TaskService.get_task(task_id)
    if task:
        return jsonify(task.to_dict())
    return jsonify({'error': 'Task not found'}), 404

@bp.route('/', methods=['POST'])
def create_task():
    data = request.get_json()
    if not data or 'type' not in data:
        return jsonify({'error': 'Type is required'}), 400
    
    try:
        task = TaskService.create_task(data)
        return jsonify(task.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.get_json()
    if not data or 'type' not in data:
        return jsonify({'error': 'Type is required'}), 400
    
    try:
        task = TaskService.update_task(task_id, data)
        if task:
            return jsonify(task.to_dict())
        return jsonify({'error': 'Task not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    try:
        TaskService.delete_task(task_id)
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500 