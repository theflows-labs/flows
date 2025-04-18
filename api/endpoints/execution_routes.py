from flask import Blueprint, request, jsonify
from ..services.execution_service import ExecutionService

bp = Blueprint('executions', __name__)

@bp.route('/', methods=['GET'])
def get_executions():
    executions = ExecutionService.get_all_executions()
    return jsonify(executions)

@bp.route('/<execution_id>', methods=['GET'])
def get_execution(execution_id):
    execution = ExecutionService.get_execution(execution_id)
    if execution:
        return jsonify(execution.to_dict())
    return jsonify({'error': 'Execution not found'}), 404

@bp.route('/', methods=['POST'])
def create_execution():
    data = request.get_json()
    if not data or 'dag_id' not in data:
        return jsonify({'error': 'DAG ID is required'}), 400
    
    try:
        execution = ExecutionService.create_execution(data)
        return jsonify(execution.to_dict()), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<execution_id>', methods=['PUT'])
def update_execution(execution_id):
    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Status is required'}), 400
    
    try:
        execution = ExecutionService.update_execution(execution_id, data)
        if execution:
            return jsonify(execution.to_dict())
        return jsonify({'error': 'Execution not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<execution_id>', methods=['DELETE'])
def delete_execution(execution_id):
    try:
        ExecutionService.delete_execution(execution_id)
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500 