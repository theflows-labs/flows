from typing import Dict, List, Optional, Any
from datetime import datetime
import threading
import subprocess
import logging
from core.repositories.repository import (
    FlowConfigurationRepository,
    TaskConfigurationRepository,
    FlowExecutionRepository,
    TaskExecutionRepository
)
from core.models.models import ExecutionStatus

logger = logging.getLogger(__name__)

class ExecutionService:
    def __init__(self):
        self.flow_repo = FlowConfigurationRepository()
        self.task_repo = TaskConfigurationRepository()
        self.flow_exec_repo = FlowExecutionRepository()
        self.task_exec_repo = TaskExecutionRepository()

    @classmethod
    def trigger_execution(cls, flow_id: str) -> Dict[str, Any]:
        """Trigger a new flow execution."""
        service = cls()
        
        # Get flow configuration
        flow_config = service.flow_repo.get_flow_config_by_flow_id(flow_id)
        if not flow_config:
            raise ValueError(f"Flow {flow_id} not found")

        # Create execution record
        execution = service.flow_exec_repo.create_execution(flow_config.config_id)

        # Start execution in background thread
        thread = threading.Thread(
            target=service._execute_flow,
            args=(execution.execution_id,)
        )
        thread.start()

        return service._execution_to_dict(execution)

    @classmethod
    def get_execution_status(cls, execution_id: int) -> Optional[Dict[str, Any]]:
        """Get execution status."""
        service = cls()
        execution = service.flow_exec_repo.get_execution(execution_id)
        return service._execution_to_dict(execution) if execution else None

    @classmethod
    def get_execution_logs(cls, execution_id: int) -> Optional[Dict[str, Any]]:
        """Get execution logs."""
        service = cls()
        execution = service.flow_exec_repo.get_execution(execution_id)
        if not execution:
            return None
        
        return {
            'execution_id': execution.execution_id,
            'flow_logs': execution.logs,
            'task_logs': [
                {
                    'task_id': task_exec.task_id,
                    'logs': task_exec.logs,
                    'error': task_exec.error
                }
                for task_exec in execution.task_executions
            ]
        }

    def _execute_flow(self, execution_id: int) -> None:
        """Execute a flow and its tasks."""
        try:
            # Update status to running
            self.flow_exec_repo.update_execution(
                execution_id,
                status=ExecutionStatus.RUNNING
            )

            # Get flow configuration and tasks
            execution = self.flow_exec_repo.get_execution(execution_id)
            flow_config = self.flow_repo.get_flow_config(execution.flow_config_id)
            tasks = self.task_repo.get_task_configs_by_flow_config(flow_config.config_id)

            # Sort tasks by sequence
            tasks.sort(key=lambda x: x.task_sequence)

            # Execute tasks in sequence
            for task in tasks:
                task_execution = self.task_exec_repo.create_task_execution(
                    execution_id,
                    task.task_id
                )
                
                try:
                    # Execute task based on type
                    if task.task_type == 'python':
                        result = self._execute_python_task(task.config_details)
                    elif task.task_type == 'bash':
                        result = self._execute_bash_task(task.config_details)
                    elif task.task_type == 'sql':
                        result = self._execute_sql_task(task.config_details)
                    elif task.task_type == 'http':
                        result = self._execute_http_task(task.config_details)
                    elif task.task_type == 'docker':
                        result = self._execute_docker_task(task.config_details)
                    else:
                        raise ValueError(f"Unsupported task type: {task.task_type}")

                    # Update task execution status
                    self.task_exec_repo.update_task_execution(
                        task_execution.task_execution_id,
                        status=ExecutionStatus.SUCCESS,
                        result=result,
                        end_time=datetime.utcnow()
                    )

                except Exception as e:
                    # Update task execution status to failed
                    self.task_exec_repo.update_task_execution(
                        task_execution.task_execution_id,
                        status=ExecutionStatus.FAILED,
                        error=str(e),
                        end_time=datetime.utcnow()
                    )
                    raise

            # Update flow execution status to success
            self.flow_exec_repo.update_execution(
                execution_id,
                status=ExecutionStatus.SUCCESS,
                end_time=datetime.utcnow()
            )

        except Exception as e:
            # Update flow execution status to failed
            self.flow_exec_repo.update_execution(
                execution_id,
                status=ExecutionStatus.FAILED,
                error=str(e),
                end_time=datetime.utcnow()
            )
            logger.error(f"Error executing flow {execution_id}: {str(e)}")

    @staticmethod
    def _execute_python_task(config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Python task."""
        python_callable = config.get('python_callable')
        if not python_callable:
            raise ValueError("Python callable not specified")

        module_path, func_name = python_callable.rsplit('.', 1)
        cmd = [
            'python',
            '-c',
            f"from {module_path} import {func_name}; {func_name}(*{config.get('op_args', [])}, **{config.get('op_kwargs', {})})"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {
            'stdout': result.stdout,
            'stderr': result.stderr
        }

    @staticmethod
    def _execute_bash_task(config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a bash task."""
        cmd = config.get('bash_command')
        if not cmd:
            raise ValueError("Bash command not specified")

        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return {
            'stdout': result.stdout,
            'stderr': result.stderr
        }

    @staticmethod
    def _execute_sql_task(config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a SQL task."""
        # TODO: Implement SQL execution
        raise NotImplementedError("SQL task execution not implemented")

    @staticmethod
    def _execute_http_task(config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an HTTP task."""
        # TODO: Implement HTTP execution
        raise NotImplementedError("HTTP task execution not implemented")

    @staticmethod
    def _execute_docker_task(config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a Docker task."""
        # TODO: Implement Docker execution
        raise NotImplementedError("Docker task execution not implemented")

    @staticmethod
    def _execution_to_dict(execution: 'FlowExecution') -> Dict[str, Any]:
        """Convert an execution model to a dictionary."""
        return {
            'execution_id': execution.execution_id,
            'flow_config_id': execution.flow_config_id,
            'status': execution.status,
            'start_time': execution.start_time.isoformat() if execution.start_time else None,
            'end_time': execution.end_time.isoformat() if execution.end_time else None,
            'result': execution.result,
            'error': execution.error,
            'is_active': execution.is_active
        } 