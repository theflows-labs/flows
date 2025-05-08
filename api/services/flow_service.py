from typing import Dict, List, Optional, Any
from core.repositories.repository import FlowConfigurationRepository, TaskConfigurationRepository
from core.models.models import FlowConfiguration, TaskConfiguration
from orchestration.airflow_plugin.plugin_core.dag_builder.yaml_builder import YAMLDAGBuilder
import yaml
import logging
import tempfile
import os

logger = logging.getLogger(__name__)

class FlowService:
    def __init__(self):
        self.flow_repo = FlowConfigurationRepository()
        self.task_repo = TaskConfigurationRepository()

    @classmethod
    def get_all_flows(cls) -> List[Dict[str, Any]]:
        """Get all active flows."""
        service = cls()
        flows = service.flow_repo.get_all_flow_configs()
        return [service._flow_to_dict(flow) for flow in flows]    

    @classmethod
    def get_all_activeflows(cls) -> List[Dict[str, Any]]:
        """Get all active flows."""
        service = cls()
        flows = service.flow_repo.get_all_active_flow_configs()
        return [service._flow_to_dict(flow) for flow in flows]

    @classmethod
    def get_flow(cls, flow_id: str) -> Optional[Dict[str, Any]]:
        """Get a flow by ID."""
        service = cls()
        flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
        if flow:
            return service._flow_to_dict(flow)
        return None

    @classmethod
    def create_flow(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new flow."""
        service = cls()
        
        # Convert to YAML if not provided
        yaml_content = data.get('config_details_yaml')
        if not yaml_content and data.get('config_details'):
            yaml_content = yaml.dump(data['config_details'], default_flow_style=False)

        flow = service.flow_repo.create_flow_config(
            flow_id=data['flow_id'],
            config_details=data['config_details'],
            config_details_yaml=yaml_content,
            description=data.get('description')
        )
        return service._flow_to_dict(flow)

    @classmethod
    def update_flow(cls, flow_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update a flow."""
        service = cls()
        flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
        if not flow:
            return None

        # Convert to YAML if not provided
        yaml_content = data.get('config_details_yaml')
        if not yaml_content and data.get('config_details'):
            yaml_content = yaml.dump(data['config_details'], default_flow_style=False)

        updated_flow = service.flow_repo.update_flow_config(
            config_id=flow.config_id,
            config_details=data.get('config_details', flow.config_details),
            config_details_yaml=yaml_content,
            description=data.get('description', flow.description)
        )
        return service._flow_to_dict(updated_flow) if updated_flow else None

    @classmethod
    def delete_flow(cls, flow_id: str) -> bool:
        """Delete a flow."""
        service = cls()
        flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
        if flow:
            return service.flow_repo.delete_flow_config(flow.config_id)
        return False

    @classmethod
    def get_flow_yaml(cls, flow_id: str) -> Optional[str]:
        """Get the YAML representation of a flow."""
        service = cls()
        flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
        if not flow:
            return None

        # Get tasks with dependencies eagerly loaded
        tasks = service.task_repo.get_task_configs_by_flow_config_with_dependencies(flow.config_id)
        
        # Build task dependencies
        task_dependencies = []
        for task in tasks:
            # Dependencies are now eagerly loaded
            for dep in task.dependencies:
                task_dependencies.append({
                    'from': dep.task_id,
                    'to': dep.depends_on_task_id,
                    'type': dep.dependency_type,
                    'condition': dep.condition
                })

        # Build YAML structure
        yaml_structure = {
            'version': '1.0',
            'flow': {
                'id': flow.flow_id,
                'description': flow.description or '',
                'tasks': [{
                    'id': task.task_id,
                    'type': task.task_type,
                    'name': task.description or f'Task {task.task_sequence}',
                    'description': task.description or '',
                    'config': task.config_details or {},
                    'sequence': task.task_sequence
                } for task in tasks],
                'dependencies': task_dependencies
            },
            'metadata': {
                'created_at': flow.created_dt.isoformat() if flow.created_dt else None,
                'updated_at': flow.updated_dt.isoformat() if flow.updated_dt else None,
                'version': '1.0',
                'engine': 'airflow'
            }
        }

        # Convert to YAML with proper formatting
        return yaml.dump(
            yaml_structure,
            default_flow_style=False,
            sort_keys=False,
            indent=2,
            width=120,
            allow_unicode=True
        )

    @staticmethod
    def _flow_to_dict(flow: FlowConfiguration) -> Dict[str, Any]:
        """Convert a FlowConfiguration model to a dictionary."""
        return {
            'config_id': flow.config_id,
            'flow_id': flow.flow_id,
            'config_details': flow.config_details,
            'config_details_yaml': flow.config_details_yaml,
            'description': flow.description,
            'created_dt': flow.created_dt.isoformat() if flow.created_dt else None,
            'updated_dt': flow.updated_dt.isoformat() if flow.updated_dt else None,
            'is_active': flow.is_active
        }

    @classmethod
    def activate_flow(cls, flow_id: str):
        """Activate a flow by setting its is_active flag to True."""
        logger.info(f"Activating flow: {flow_id}")
        try:
            service = cls()
            # Get the flow configuration
            flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
            if not flow:
                logger.warning(f"Flow not found: {flow_id}")
                return None

            # Update the flow configuration using the repository
            updated_flow = service.flow_repo.update_flow_status(
                config_id=flow.config_id,
                is_active=True
            )
            
            if not updated_flow:
                logger.error(f"Failed to activate flow: {flow_id}")
                return None
            
            logger.info(f"Successfully activated flow: {flow_id}")
            return service._flow_to_dict(updated_flow)
        except Exception as e:
            logger.error(f"Error activating flow {flow_id}: {str(e)}")
            raise

    @classmethod
    def deactivate_flow(cls, flow_id: str):
        """Deactivate a flow by setting its is_active flag to False."""
        logger.info(f"Deactivating flow: {flow_id}")
        try:
            service = cls()
            # Get the flow configuration
            flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
            if not flow:
                logger.warning(f"Flow not found: {flow_id}")
                return None

            # Update the flow configuration using the repository
            updated_flow = service.flow_repo.update_flow_status(
                config_id=flow.config_id,
                is_active=False
            )
            
            if not updated_flow:
                logger.error(f"Failed to deactivate flow: {flow_id}")
                return None
            
            logger.info(f"Successfully deactivated flow: {flow_id}")
            return service._flow_to_dict(updated_flow)
        except Exception as e:
            logger.error(f"Error deactivating flow {flow_id}: {str(e)}")
            raise

    @classmethod
    def get_flow_statistics(cls):
        """Get statistics about flows and tasks."""
        logger.info("Getting flow statistics")
        try:
            service = cls()
            flows = service.flow_repo.get_all_flow_configs()
            
            # Calculate flow statistics
            total_flows = len(flows)
            active_flows = sum(1 for flow in flows if flow.is_active)
            inactive_flows = total_flows - active_flows
            
            # Calculate task statistics
            task_types = {}
            for flow in flows:
                if flow.config_details and 'nodes' in flow.config_details:
                    for node in flow.config_details['nodes']:
                        task_type = node.get('data', {}).get('type', 'unknown')
                        task_types[task_type] = task_types.get(task_type, 0) + 1
            
            return {
                'flows': {
                    'total': total_flows,
                    'active': active_flows,
                    'inactive': inactive_flows
                },
                'tasks': {
                    'by_type': task_types
                }
            }
        except Exception as e:
            logger.error(f"Error getting flow statistics: {str(e)}")
            raise

    @classmethod
    def analyze_flow(cls, flow_id: str) -> Dict[str, Any]:
        """Analyze a flow and generate YAML with detailed logs."""
        # Set up log capture
        log_capture = []
        class LogCaptureHandler(logging.Handler):
            def emit(self, record):
                log_capture.append(self.format(record))

        # Configure the logger
        dag_logger = logging.getLogger('yaml_dag_builder')
        handler = LogCaptureHandler()
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        dag_logger.addHandler(handler)
        dag_logger.setLevel(logging.INFO)

        try:
            dag_logger.info(f"Starting flow analysis for flow_id: {flow_id}")
            service = cls()
            
            # Get flow configuration
            flow = service.flow_repo.get_flow_config_by_flow_id(flow_id)
            if not flow:
                dag_logger.error(f"Flow not found: {flow_id}")
                raise ValueError(f"Flow not found: {flow_id}")

            dag_logger.info(f"Found flow configuration for {flow_id}, fetching tasks...")
            # Get tasks with dependencies
            tasks = service.task_repo.get_task_configs_by_flow_config_with_dependencies(flow.config_id)
            if not tasks:
                dag_logger.warning(f"No tasks found for flow: {flow_id}")
            
            # Build task dependencies
            task_dependencies = []
            for task in tasks:
                for dep in task.dependencies:
                    task_dependencies.append({
                        'from': dep.task_id,
                        'to': dep.depends_on_task_id,
                        'type': dep.dependency_type,
                        'condition': dep.condition
                    })

            dag_logger.info(f"Building YAML structure for flow: {flow_id}")
            # Build YAML structure
            yaml_structure = {
                'version': '1.0',
                'flow': {
                    'id': flow.flow_id,
                    'description': flow.description or '',
                    'tasks': [{
                        'id': task.task_id,
                        'type': task.task_type,
                        'name': task.description or f'Task {task.task_sequence}',
                        'description': task.description or '',
                        'config': task.config_details or {},
                        'sequence': task.task_sequence
                    } for task in tasks],
                    'dependencies': task_dependencies
                },
                'metadata': {
                    'created_at': flow.created_dt.isoformat() if flow.created_dt else None,
                    'updated_at': flow.updated_dt.isoformat() if flow.updated_dt else None,
                    'version': '1.0',
                    'engine': 'airflow'
                }
            }

            # Convert to YAML
            yaml_content = yaml.dump(yaml_structure, default_flow_style=False)
            dag_logger.info(f"Generated YAML for flow: {flow_id}")

            # Create a temporary YAML file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
                temp_file.write(yaml_content)
                temp_file_path = temp_file.name

            try:
                # Initialize YAML DAG Builder with the temporary file path
                dag_logger.info(f"Initializing DAG builder for flow: {flow_id}")
                dag_builder = YAMLDAGBuilder(yaml_path=temp_file_path)
                
                try:
                    dag_logger.info(f"Building DAG for flow: {flow_id}")
                    
                    # Validate tasks by attempting to build the DAG
                    dag_logger.info("Starting DAG validation...")
                    try:
                        dag = dag_builder.build()
                        dag_logger.info("Successfully validated and built DAG")

                        # Additional task validation after DAG build
                        dag_logger.info("\n=== Task Validation Metrics ===")
                        task_metrics = []
                        
                        # Get all tasks from the DAG
                        dag_tasks = dag.tasks
                        dag_logger.info(f"Found {len(dag_tasks)} tasks in the DAG")
                        
                        # Build a mapping from task_id to original config
                        task_config_map = {str(t.task_id): t for t in tasks}
                        dag_task_ids = {str(getattr(t, 'task_id', None) or getattr(t, 'task_id', None)) for t in dag_tasks}
                        
                        # First, check for tasks that failed to be created in the DAG
                        missing_tasks = set(task_config_map.keys()) - dag_task_ids
                        if missing_tasks:
                            dag_logger.error(f"Found {len(missing_tasks)} tasks that failed to be created in the DAG:")
                            for task_id in missing_tasks:
                                orig_task = task_config_map[task_id]
                                error_msg = f"Task {task_id} ({orig_task.task_type}) failed to be created in the DAG"
                                dag_logger.error(error_msg)
                                task_metrics.append({
                                    'task_id': task_id,
                                    'type': orig_task.task_type,
                                    'status': 'error',
                                    'issues': [error_msg]
                                })

                        # Then validate the tasks that were successfully created
                        for dag_task in dag_tasks:
                            dag_task_id = str(getattr(dag_task, 'task_id', None) or getattr(dag_task, 'task_id', None))
                            orig_task = task_config_map.get(dag_task_id)
                            config_details = orig_task.config_details if orig_task else {}

                            task_metric = {
                                'task_id': dag_task_id,
                                'type': getattr(dag_task, 'task_type', None) or (orig_task.task_type if orig_task else None),
                                'status': 'valid',
                                'issues': []
                            }

                            if not config_details:
                                task_metric['issues'].append("Missing configuration details")
                                task_metric['status'] = 'warning'

                            # Example: s3_list required fields
                            if task_metric['type'] == 's3_list':
                                required_fields = ['bucket', 'prefix']
                                for field in required_fields:
                                    if field not in config_details:
                                        task_metric['issues'].append(f"Missing required field: {field}")
                                        task_metric['status'] = 'error'

                            # Add task metric to list
                            task_metrics.append(task_metric)
                            
                            # Log task validation results
                            if task_metric['status'] == 'valid':
                                dag_logger.info(f"Task {task_metric['task_id']} ({task_metric['type']}): Valid")
                            elif task_metric['status'] == 'warning':
                                dag_logger.warning(f"Task {task_metric['task_id']} ({task_metric['type']}): {', '.join(task_metric['issues'])}")
                            else:
                                dag_logger.error(f"Task {task_metric['task_id']} ({task_metric['type']}): {', '.join(task_metric['issues'])}")
                        
                        # Add summary to logs
                        valid_tasks = sum(1 for m in task_metrics if m['status'] == 'valid')
                        warning_tasks = sum(1 for m in task_metrics if m['status'] == 'warning')
                        error_tasks = sum(1 for m in task_metrics if m['status'] == 'error')
                        
                        dag_logger.info("\n=== Validation Summary ===")
                        dag_logger.info(f"Total tasks: {len(task_metrics)}")
                        dag_logger.info(f"Valid tasks: {valid_tasks}")
                        dag_logger.info(f"Tasks with warnings: {warning_tasks}")
                        dag_logger.info(f"Tasks with errors: {error_tasks}")
                        if missing_tasks:
                            dag_logger.error(f"Failed to create {len(missing_tasks)} tasks in the DAG")
                        
                        build_logs = '\n'.join(log_capture)
                        
                        return {
                            'yaml': yaml_content,
                            'logs': build_logs,
                            'status': 'success' if error_tasks == 0 else 'warning',
                            'validation_errors': [m for m in task_metrics if m['status'] != 'valid'],
                            'metrics': {
                                'total_tasks': len(task_metrics),
                                'valid_tasks': valid_tasks,
                                'warning_tasks': warning_tasks,
                                'error_tasks': error_tasks
                            }
                        }
                    except Exception as e:
                        error_msg = f"Error building DAG: {str(e)}"
                        dag_logger.error(error_msg)
                        build_logs = '\n'.join(log_capture)
                        
                        # Try to extract task-specific errors from the build error
                        validation_errors = []
                        if hasattr(e, 'args') and len(e.args) > 0:
                            error_str = str(e.args[0])
                            # Look for task-specific error patterns
                            for task in tasks:
                                if task.task_id in error_str or task.task_type in error_str:
                                    validation_errors.append(f"Error in task {task.task_id} ({task.task_type}): {error_str}")
                        
                        if not validation_errors:
                            validation_errors = [error_msg]
                        
                        return {
                            'yaml': yaml_content,
                            'logs': build_logs,
                            'status': 'error',
                            'error': 'DAG validation failed',
                            'validation_errors': validation_errors
                        }
                except Exception as e:
                    build_logs = '\n'.join(log_capture)
                    dag_logger.error(f"Error during DAG building: {str(e)}")
                    return {
                        'yaml': yaml_content,
                        'logs': build_logs,
                        'status': 'error',
                        'error': str(e),
                        'validation_errors': [str(e)]
                    }
            finally:
                # Clean up the temporary file
                try:
                    os.unlink(temp_file_path)
                    dag_logger.info(f"Cleaned up temporary file: {temp_file_path}")
                except Exception as e:
                    dag_logger.warning(f"Failed to delete temporary file {temp_file_path}: {str(e)}")
        except ValueError as ve:
            dag_logger.error(f"Validation error for flow {flow_id}: {str(ve)}")
            raise
        except Exception as e:
            dag_logger.error(f"Unexpected error analyzing flow {flow_id}: {str(e)}")
            raise
        finally:
            # Remove log handler
            dag_logger.removeHandler(handler) 