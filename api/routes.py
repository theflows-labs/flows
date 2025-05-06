from flask import Blueprint, request, jsonify
from .services.flow_service import FlowService
from .services.task_service import TaskService
from .services.execution_service import ExecutionService
from .services.task_type_service import TaskTypeService
import logging

logger = logging.getLogger(__name__)

# Create blueprints
flow_bp = Blueprint('flow', __name__)
task_bp = Blueprint('task', __name__)
execution_bp = Blueprint('execution', __name__)
task_type_bp = Blueprint('task_type', __name__)

# Flow Routes
@flow_bp.route('/', methods=['GET'])
def get_flows():
    flows = FlowService.get_all_flows()
    return jsonify(flows)

@flow_bp.route('/<flow_id>', methods=['GET'])
def get_flow(flow_id):
    flow = FlowService.get_flow(flow_id)
    return jsonify(flow)

@flow_bp.route('/', methods=['POST'])
def create_flow():
    data = request.json
    flow = FlowService.create_flow(data)
    return jsonify(flow), 201

@flow_bp.route('/<flow_id>', methods=['PUT'])
def update_flow(flow_id):
    data = request.json
    flow = FlowService.update_flow(flow_id, data)
    return jsonify(flow)

@flow_bp.route('/<flow_id>', methods=['DELETE'])
def delete_flow(flow_id):
    FlowService.delete_flow(flow_id)
    return '', 204

@flow_bp.route('/<flow_id>/yaml', methods=['GET'])
def get_flow_yaml(flow_id):
    """Get the YAML representation of a flow."""
    yaml_content = FlowService.get_flow_yaml(flow_id)
    if yaml_content is None:
        return jsonify({'error': 'Flow not found'}), 404
    
    # Return YAML content directly with proper content type
    return yaml_content, 200, {
        'Content-Type': 'application/x-yaml',
        'Content-Disposition': f'attachment; filename=flow-{flow_id}.yaml'
    }

@flow_bp.route('/<flow_id>/activate', methods=['POST'])
def activate_flow(flow_id):
    try:
        logger.info(f"Attempting to activate flow: {flow_id}")
        flow = FlowService.activate_flow(flow_id)
        if not flow:
            logger.warning(f"Flow not found: {flow_id}")
            return jsonify({'error': 'Flow not found'}), 404
        logger.info(f"Successfully activated flow: {flow_id}")
        return jsonify(flow)
    except Exception as e:
        logger.error(f"Error activating flow {flow_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@flow_bp.route('/<flow_id>/deactivate', methods=['POST'])
def deactivate_flow(flow_id):
    try:
        logger.info(f"Attempting to deactivate flow: {flow_id}")
        flow = FlowService.deactivate_flow(flow_id)
        if not flow:
            logger.warning(f"Flow not found: {flow_id}")
            return jsonify({'error': 'Flow not found'}), 404
        logger.info(f"Successfully deactivated flow: {flow_id}")
        return jsonify(flow)
    except Exception as e:
        logger.error(f"Error deactivating flow {flow_id}: {str(e)}")
        return jsonify({'error': str(e)}), 500

@flow_bp.route('/statistics', methods=['GET'])
def get_flow_statistics():
    try:
        logger.info("Fetching flow statistics")
        stats = FlowService.get_flow_statistics()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error fetching flow statistics: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Task Routes
@task_bp.route('/types', methods=['GET'])
def get_task_types():
    """Get all task types."""
    task_types = TaskService.get_task_types()
    return jsonify(task_types)

@task_bp.route('/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = TaskService.get_task(task_id)
    return jsonify(task)

@task_bp.route('/', methods=['POST'])
def create_task():
    data = request.json
    task = TaskService.create_task(data)
    return jsonify(task), 201

@task_bp.route('/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json
    task = TaskService.update_task(task_id, data)
    return jsonify(task)

@task_bp.route('/dependencies', methods=['POST'])
def create_dependency():
    data = request.json
    dependency = TaskService.create_dependency(data)
    return jsonify(dependency), 201

@task_bp.route('/dependencies/<int:dependency_id>', methods=['PUT'])
def update_dependency(dependency_id):
    data = request.json
    dependency = TaskService.update_dependency(dependency_id, data)
    return jsonify(dependency)

@task_bp.route('/flow/<int:flow_config_id>', methods=['GET'])
def get_flow_tasks(flow_config_id):
    tasks = TaskService.get_tasks_by_flow_config(flow_config_id)
    return jsonify(tasks)

# Execution Routes
@execution_bp.route('/<flow_id>', methods=['POST'])
def trigger_execution(flow_id):
    execution = ExecutionService.trigger_execution(flow_id)
    return jsonify(execution), 201

@execution_bp.route('/<execution_id>', methods=['GET'])
def get_execution_status(execution_id):
    status = ExecutionService.get_execution_status(execution_id)
    return jsonify(status)

@execution_bp.route('/<execution_id>/logs', methods=['GET'])
def get_execution_logs(execution_id):
    logs = ExecutionService.get_execution_logs(execution_id)
    return jsonify(logs)

# Task Type Routes
@task_type_bp.route('/', methods=['GET'])
def get_task_types():
    """Get all task types."""
    try:
        task_types = TaskTypeService().get_task_types()
        return jsonify(task_types)
    except Exception as e:
        logger.error(f"Error getting task types: {str(e)}")
        return jsonify({'error': str(e)}), 500

@task_type_bp.route('/refresh', methods=['POST'])
def refresh_task_types():
    """Refresh task types by scanning plugins."""
    try:
        task_types = TaskTypeService().refresh_task_types()
        return jsonify(task_types)
    except Exception as e:
        logger.error(f"Error refreshing task types: {str(e)}")
        return jsonify({'error': str(e)}), 500

@task_type_bp.route('/', methods=['POST'])
def create_task_type():
    """Create a new task type."""
    try:
        data = request.json
        task_type = TaskTypeService().create_task_type(data)
        return jsonify(task_type), 201
    except Exception as e:
        logger.error(f"Error creating task type: {str(e)}")
        return jsonify({'error': str(e)}), 500

@task_type_bp.route('/<type_key>', methods=['PUT'])
def update_task_type(type_key):
    """Update a task type."""
    try:
        data = request.json
        task_type = TaskTypeService().update_task_type(type_key, data)
        return jsonify(task_type)
    except Exception as e:
        logger.error(f"Error updating task type: {str(e)}")
        return jsonify({'error': str(e)}), 500

@task_type_bp.route('/<type_key>', methods=['DELETE'])
def deactivate_task_type(type_key):
    """Deactivate a task type."""
    try:
        TaskTypeService().deactivate_task_type(type_key)
        return '', 204
    except Exception as e:
        logger.error(f"Error deactivating task type: {str(e)}")
        return jsonify({'error': str(e)}), 500

# Export all blueprints
__all__ = ['flow_bp', 'task_bp', 'execution_bp', 'task_type_bp'] 