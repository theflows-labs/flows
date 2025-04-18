from flask import Blueprint, request, jsonify, send_file
from ..services.dag_service import DAGService

bp = Blueprint('dags', __name__)

@bp.route('/', methods=['GET'])
def get_dags():
    try:
        dags = DAGService.get_all_dags()
        return jsonify(dags)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<dag_id>', methods=['GET'])
def get_dag(dag_id):
    try:
        dag = DAGService.get_dag(dag_id)
        if dag:
            return jsonify(dag.to_dict())
        return jsonify({'error': 'DAG not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/', methods=['POST'])
def create_dag():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        dag = DAGService.create_dag(data)
        return jsonify(dag.to_dict()), 201
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<dag_id>', methods=['PUT'])
def update_dag(dag_id):
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        dag = DAGService.update_dag(dag_id, data)
        if dag:
            return jsonify(dag.to_dict())
        return jsonify({'error': 'DAG not found'}), 404
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<dag_id>', methods=['DELETE'])
def delete_dag(dag_id):
    try:
        DAGService.delete_dag(dag_id)
        return '', 204
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<dag_id>/yaml', methods=['GET'])
def get_dag_yaml(dag_id):
    try:
        yaml_content = DAGService.get_dag_yaml(dag_id)
        if yaml_content:
            return send_file(
                yaml_content,
                mimetype='text/yaml',
                as_attachment=True,
                download_name=f'dag_{dag_id}.yaml'
            )
        return jsonify({'error': 'DAG not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500 