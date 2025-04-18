"""
Example script demonstrating how to create a DAG from YAML configuration.
"""
import os
from pathlib import Path
from flows.plugin_core.dag_builder.registry import OperatorRegistry
from flows.plugin_core.dag_builder.yaml_builder import YAMLDAGBuilder

# Get the path to the example YAML configuration
config_path = Path(__file__).parent / "dag_config.yaml"

def create_dag():
    """Create a DAG from YAML configuration."""
    # Initialize the YAML DAG builder
    builder = YAMLDAGBuilder(
        config_path=str(config_path),
        dag_id="example_dag"
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

# Create the DAG when this script is run directly
if __name__ == "__main__":
    create_dag() 