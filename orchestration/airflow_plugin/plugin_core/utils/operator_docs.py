"""
Utility for exporting operator documentation.
"""
import os
# Set Airflow configuration before importing Airflow modules
os.environ['AIRFLOW_HOME'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ['AIRFLOW__CORE__SQL_ALCHEMY_CONN'] = 'postgresql://postgress:postgress@localhost:5433/postgress'

import json
import logging
from typing import Dict, Any
from pathlib import Path

from flows.plugin_core.dag_builder.registry import OperatorRegistry

logger = logging.getLogger(__name__)

def export_operator_documentation(output_dir: str = "docs") -> None:
    """
    Export documentation for all registered operators.
    
    Args:
        output_dir: Directory to save documentation files
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get the registry
    registry = OperatorRegistry.register_factories()
    
    # Get all task types
    task_types = registry.get_all_task_types()
    
    # Export documentation for each operator
    for task_type in task_types:
        factory_class = registry.get_factory(task_type)
        if factory_class:
            try:
                # Get documentation
                docs = factory_class.get_parameter_documentation()
                
                # Create documentation structure
                operator_docs = {
                    "task_type": task_type,
                    "factory_class": factory_class.__name__,
                    "description": factory_class.__doc__ or "",
                    "parameters": docs
                }
                
                # Save to file
                output_file = output_path / f"{task_type}.json"
                with open(output_file, "w") as f:
                    json.dump(operator_docs, f, indent=2, default=str)
                
                logger.info(f"Exported documentation for {task_type} to {output_file}")
            except Exception as e:
                logger.error(f"Error exporting documentation for {task_type}: {str(e)}")
    
    # Create index file
    index = {
        "operators": [
            {
                "task_type": task_type,
                "factory_class": registry.get_factory(task_type).__name__,
                "description": registry.get_factory(task_type).__doc__ or ""
            }
            for task_type in task_types
        ]
    }
    
    # Save index
    index_file = output_path / "index.json"
    with open(index_file, "w") as f:
        json.dump(index, f, indent=2, default=str)
    
    logger.info(f"Exported operator index to {index_file}")

def generate_markdown_docs(output_dir: str = "docs") -> None:
    """
    Generate markdown documentation for all operators.
    
    Args:
        output_dir: Directory to save markdown files
    """
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Get the registry
    registry = OperatorRegistry.register_factories()
    
    # Get all task types
    task_types = registry.get_all_task_types()
    
    # Generate markdown for each operator
    for task_type in task_types:
        factory_class = registry.get_factory(task_type)
        if factory_class:
            try:
                # Get documentation
                docs = factory_class.get_parameter_documentation()
                
                # Generate markdown
                markdown = [
                    f"# {task_type}",
                    "",
                    f"**Factory Class**: `{factory_class.__name__}`",
                    "",
                    factory_class.__doc__ or "",
                    "",
                    "## Parameters",
                    "",
                    "| Parameter | Required | Type | Default | Description | Example |",
                    "|-----------|----------|------|---------|-------------|---------|"
                ]
                
                for param, info in docs.items():
                    markdown.append(
                        f"| {param} | {info['required']} | {info['type'].__name__} | "
                        f"{info.get('default', 'N/A')} | {info['description']} | "
                        f"{info.get('example', 'N/A')} |"
                    )
                
                # Save to file
                output_file = output_path / f"{task_type}.md"
                with open(output_file, "w") as f:
                    f.write("\n".join(markdown))
                
                logger.info(f"Generated markdown documentation for {task_type} to {output_file}")
            except Exception as e:
                logger.error(f"Error generating markdown for {task_type}: {str(e)}")
    
    # Generate index
    index = [
        "# Operator Documentation",
        "",
        "## Available Operators",
        "",
        "| Task Type | Factory Class | Description |",
        "|-----------|---------------|-------------|"
    ]
    
    for task_type in task_types:
        factory_class = registry.get_factory(task_type)
        if factory_class:
            index.append(
                f"| [{task_type}]({task_type}.md) | `{factory_class.__name__}` | "
                f"{factory_class.__doc__ or ''} |"
            )
    
    # Save index
    index_file = output_path / "index.md"
    with open(index_file, "w") as f:
        f.write("\n".join(index))
    
    logger.info(f"Generated operator index to {index_file}")

if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Export documentation
    export_operator_documentation()
    generate_markdown_docs() 