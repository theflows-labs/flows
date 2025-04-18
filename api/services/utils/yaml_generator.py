import yaml
from datetime import datetime
import tempfile
import os

def generate_yaml(dag_data):
    """
    Generate YAML content from DAG data.
    
    Args:
        dag_data (dict): Dictionary containing DAG information
        
    Returns:
        str: Path to temporary YAML file
    """
    yaml_data = {
        'name': dag_data['name'],
        'description': dag_data.get('description', ''),
        'schedule': dag_data.get('schedule', None),
        'start_date': dag_data.get('start_date', datetime.utcnow().isoformat()),
        'tasks': {}
    }
    
    # Process nodes as tasks
    for node in dag_data.get('nodes', []):
        task_id = node['id']
        yaml_data['tasks'][task_id] = {
            'operator': node['data']['type'],
            'params': node['data'].get('config', {}),
            'dependencies': []
        }
    
    # Process edges to set dependencies
    for edge in dag_data.get('edges', []):
        target_task = edge['target']
        source_task = edge['source']
        if target_task in yaml_data['tasks']:
            yaml_data['tasks'][target_task]['dependencies'].append(source_task)
    
    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.yaml', mode='w')
    try:
        yaml.dump(yaml_data, temp_file, default_flow_style=False, sort_keys=False)
        temp_file.close()
        return temp_file.name
    except Exception as e:
        # Clean up the temporary file if there's an error
        os.unlink(temp_file.name)
        raise e 