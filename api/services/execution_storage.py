from typing import Dict, List, Optional, Any
import yaml
from pathlib import Path
from datetime import datetime
from core.repositories.repository import FlowExecutionRepository, TaskExecutionRepository
from core.models.models import FlowExecution, TaskExecution

class ExecutionStorage:
    def __init__(self, base_dir: str = "executions"):
        """Initialize execution storage with base directory for logs and results."""
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)
        self.flow_exec_repo = FlowExecutionRepository()
        self.task_exec_repo = TaskExecutionRepository()

    def save_execution_result(self, execution_id: int, result: Dict[str, Any]) -> None:
        """Save execution result to file system."""
        execution_dir = self._get_execution_dir(execution_id)
        result_file = execution_dir / "result.yaml"
        
        # Save result as YAML
        with result_file.open('w') as f:
            yaml.dump(result, f)

        # Update database
        self.flow_exec_repo.update_execution(
            execution_id=execution_id,
            result=result
        )

    def save_execution_log(self, execution_id: int, log_content: str) -> None:
        """Save execution log to file system."""
        execution_dir = self._get_execution_dir(execution_id)
        log_file = execution_dir / "execution.log"
        
        # Append to log file
        with log_file.open('a') as f:
            f.write(f"[{datetime.now().isoformat()}] {log_content}\n")

        # Update database
        execution = self.flow_exec_repo.get_execution(execution_id)
        if execution:
            current_logs = execution.logs or ""
            updated_logs = current_logs + f"[{datetime.now().isoformat()}] {log_content}\n"
            self.flow_exec_repo.update_execution(
                execution_id=execution_id,
                logs=updated_logs
            )

    def save_task_execution_result(self, task_execution_id: int, result: Dict[str, Any]) -> None:
        """Save task execution result to file system."""
        task_execution = self.task_exec_repo.get_task_execution(task_execution_id)
        if not task_execution:
            raise ValueError(f"Task execution {task_execution_id} not found")

        execution_dir = self._get_execution_dir(task_execution.flow_execution_id)
        task_dir = execution_dir / f"task_{task_execution_id}"
        task_dir.mkdir(parents=True, exist_ok=True)
        
        result_file = task_dir / "result.yaml"
        with result_file.open('w') as f:
            yaml.dump(result, f)

        # Update database
        self.task_exec_repo.update_task_execution(
            task_execution_id=task_execution_id,
            result=result
        )

    def save_task_execution_log(self, task_execution_id: int, log_content: str) -> None:
        """Save task execution log to file system."""
        task_execution = self.task_exec_repo.get_task_execution(task_execution_id)
        if not task_execution:
            raise ValueError(f"Task execution {task_execution_id} not found")

        execution_dir = self._get_execution_dir(task_execution.flow_execution_id)
        task_dir = execution_dir / f"task_{task_execution_id}"
        task_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = task_dir / "task.log"
        with log_file.open('a') as f:
            f.write(f"[{datetime.now().isoformat()}] {log_content}\n")

        # Update database
        current_logs = task_execution.logs or ""
        updated_logs = current_logs + f"[{datetime.now().isoformat()}] {log_content}\n"
        self.task_exec_repo.update_task_execution(
            task_execution_id=task_execution_id,
            logs=updated_logs
        )

    def get_execution_result(self, execution_id: int) -> Optional[Dict[str, Any]]:
        """Get execution result from file system."""
        result_file = self._get_execution_dir(execution_id) / "result.yaml"
        if result_file.exists():
            with result_file.open('r') as f:
                return yaml.safe_load(f)
        return None

    def get_execution_log(self, execution_id: int) -> Optional[str]:
        """Get execution log from file system."""
        log_file = self._get_execution_dir(execution_id) / "execution.log"
        if log_file.exists():
            return log_file.read_text()
        return None

    def get_task_execution_result(self, task_execution_id: int) -> Optional[Dict[str, Any]]:
        """Get task execution result from file system."""
        task_execution = self.task_exec_repo.get_task_execution(task_execution_id)
        if not task_execution:
            return None

        result_file = (self._get_execution_dir(task_execution.flow_execution_id) / 
                      f"task_{task_execution_id}" / "result.yaml")
        if result_file.exists():
            with result_file.open('r') as f:
                return yaml.safe_load(f)
        return None

    def get_task_execution_log(self, task_execution_id: int) -> Optional[str]:
        """Get task execution log from file system."""
        task_execution = self.task_exec_repo.get_task_execution(task_execution_id)
        if not task_execution:
            return None

        log_file = (self._get_execution_dir(task_execution.flow_execution_id) / 
                   f"task_{task_execution_id}" / "task.log")
        if log_file.exists():
            return log_file.read_text()
        return None

    def _get_execution_dir(self, execution_id: int) -> Path:
        """Get or create execution directory."""
        execution_dir = self.base_dir / str(execution_id)
        execution_dir.mkdir(parents=True, exist_ok=True)
        return execution_dir 