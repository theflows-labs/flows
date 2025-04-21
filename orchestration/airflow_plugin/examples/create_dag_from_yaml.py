"""
Example script demonstrating how to create a DAG from YAML configuration.
"""
import os
import sys
from pathlib import Path

# Add debugging information
print(f"Current working directory: {os.getcwd()}")
print(f"Current PYTHONPATH: {os.environ.get('PYTHONPATH', '')}")

# Add the project root to Python path
project_root = str(Path(__file__).resolve().parents[3])
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    print(f"Added {project_root} to sys.path")

print(f"Updated sys.path: {sys.path}")

try:
    # Add a breakpoint here
    #breakpoint()  # or use debugger.set_trace() if you prefer
    from orchestration.airflow_plugin.plugin_core.dag_builder.registry import OperatorRegistry
    print("Successfully imported OperatorRegistry")
except ImportError as e:
    print(f"Error importing: {e}")
    print(f"Current sys.path: {sys.path}")
    print(f"Project root: {project_root}")
    print(f"Current directory: {os.getcwd()}")
    raise

# Now the imports should work in both cases
from orchestration.airflow_plugin.plugin_core.dag_builder.yaml_builder import YAMLDAGBuilder

# Get the path to the example YAML configuration
config_path = Path(__file__).parent / "dag_config.yaml"

def create_dag():
    """Create a DAG from YAML configuration."""
    print(str(config_path))
    # Initialize the YAML DAG builder
    builder = YAMLDAGBuilder(
        yaml_path=str(config_path)
    )
    
    # Build the DAG
    #OperatorRegistry.register_factories()
    dag = builder.build()
    
    if dag:
        print(f"Successfully created DAG: {dag.dag_id}")
        return dag
    else:
        print("Failed to create DAG")
        return None

def main():
    # Add another breakpoint here
    #breakpoint()
    # Your existing code here
    create_dag()

if __name__ == '__main__':
    main() 