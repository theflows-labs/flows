from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from core.models import FlowConfiguration, TaskConfiguration, TaskDependency, FlowExecution, TaskExecution
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime
from enum import Enum

from config.database import SQLALCHEMY_CONN

class FlowConfigurationRepository:
    def __init__(self):
        # Initialize database connection
        self.engine = create_engine(SQLALCHEMY_CONN)
        self.Session = sessionmaker(bind=self.engine)

    def create_flow_config(self, flow_id: str, config_details: Dict[str, Any], config_details_yaml: Optional[str] = None, description: Optional[str] = None) -> FlowConfiguration:
        """Create a new Flow configuration."""
        session = self.Session()
        try:
            flow_config = FlowConfiguration(
                flow_id=flow_id,
                config_details=config_details,
                config_details_yaml=config_details_yaml,
                description=description,
                is_active=True
            )
            session.add(flow_config)
            session.commit()
            session.refresh(flow_config)
            return flow_config
        finally:
            session.close()

    def _json_serializer(self, obj):
        """Custom JSON serializer for objects that are not JSON serializable."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def get_flow_config(self, config_id: int) -> Optional[FlowConfiguration]:
        """Get a Flow configuration by ID."""
        session = self.Session()
        try:
            return session.query(FlowConfiguration).filter(FlowConfiguration.config_id == config_id).first()
        finally:
            session.close()

    def get_flow_config_by_flow_id(self, flow_id: str) -> Optional[FlowConfiguration]:
        """Get a Flow configuration by Flow ID."""
        session = self.Session()
        try:
            return session.query(FlowConfiguration).filter(FlowConfiguration.flow_id == flow_id).first()
        finally:
            session.close()

    def update_flow_config(self, config_id: int, config_details: Dict[str, Any], config_details_yaml: Optional[str] = None, description: Optional[str] = None) -> Optional[FlowConfiguration]:
        """Update a Flow configuration."""
        session = self.Session()
        try:
            flow_config = session.query(FlowConfiguration).filter(FlowConfiguration.config_id == config_id).first()
            if flow_config:
                flow_config.config_details = config_details
                if config_details_yaml is not None:
                    flow_config.config_details_yaml = config_details_yaml
                if description is not None:
                    flow_config.description = description
                session.commit()
                session.refresh(flow_config)
            return flow_config
        finally:
            session.close()

    def delete_flow_config(self, config_id: int) -> bool:
        """Delete a Flow configuration and its associated tasks."""
        session = self.Session()
        try:
            flow_config = session.query(FlowConfiguration).filter(FlowConfiguration.config_id == config_id).first()
            if flow_config:
                session.delete(flow_config)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def get_all_active_flow_configs(self) -> List[FlowConfiguration]:
        """Get all active Flow configurations."""
        session = self.Session()
        try:
            return session.query(FlowConfiguration).filter_by(is_active=True).all()
        finally:
            session.close()

class TaskConfigurationRepository:
    def __init__(self):
        # Initialize database connection
        self.engine = create_engine(SQLALCHEMY_CONN)
        self.Session = sessionmaker(bind=self.engine)

    def create_task_config(self, flow_config_id: int, task_type: str, task_sequence: int,
                          config_details: Dict[str, Any], config_details_yaml: Optional[str] = None,
                          description: Optional[str] = None) -> TaskConfiguration:
        """Create a new task configuration."""
        session = self.Session()
        try:
            task_config = TaskConfiguration(
                flow_config_id=flow_config_id,
                task_type=task_type,
                task_sequence=task_sequence,
                config_details=config_details,
                config_details_yaml=config_details_yaml,
                description=description,
                is_active=True
            )
            session.add(task_config)
            session.commit()
            session.refresh(task_config)
            return task_config
        finally:
            session.close()

    def _json_serializer(self, obj):
        """Custom JSON serializer for objects that are not JSON serializable."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def get_task_config(self, task_id: int) -> Optional[TaskConfiguration]:
        """Get a task configuration by ID."""
        session = self.Session()
        try:
            return session.query(TaskConfiguration).filter(TaskConfiguration.task_id == task_id).first()
        finally:
            session.close()

    def get_task_configs_by_flow_config(self, flow_config_id: int) -> List[TaskConfiguration]:
        """Get all task configurations for a Flow configuration."""
        session = self.Session()
        try:
            return session.query(TaskConfiguration).filter(
                TaskConfiguration.flow_config_id == flow_config_id
            ).order_by(TaskConfiguration.task_sequence).all()
        finally:
            session.close()

    def update_task_config(self, task_id: int, config_details: Optional[Dict[str, Any]] = None, 
                         description: Optional[str] = None, is_active: Optional[bool] = None) -> Optional[TaskConfiguration]:
        """Update a task configuration."""
        session = self.Session()
        try:
            task_config = session.query(TaskConfiguration).filter(TaskConfiguration.task_id == task_id).first()
            if task_config:
                if config_details is not None:
                    # Convert dictionary to JSON string
                    config_json = json.dumps(config_details, default=self._json_serializer)
                    task_config.config_details = config_json
                if description is not None:
                    task_config.description = description
                if is_active is not None:
                    task_config.is_active = is_active
                session.commit()
                session.refresh(task_config)
            return task_config
        finally:
            session.close()

    def delete_task_config(self, task_id: int) -> bool:
        """Delete a task configuration."""
        session = self.Session()
        try:
            task_config = session.query(TaskConfiguration).filter(TaskConfiguration.task_id == task_id).first()
            if task_config:
                session.delete(task_config)
                session.commit()
                return True
            return False
        finally:
            session.close()

class TaskDependencyRepository:
    def __init__(self):
        # Initialize database connection
        self.engine = create_engine(SQLALCHEMY_CONN)
        self.Session = sessionmaker(bind=self.engine)

    def create_dependency(self, flow_config_id: int, task_id: int, depends_on_task_id: int,
                         dependency_type: str = 'success', condition: Optional[str] = None) -> TaskDependency:
        """Create a new task dependency."""
        session = self.Session()
        try:
            dependency = TaskDependency(
                flow_config_id=flow_config_id,
                task_id=task_id,
                depends_on_task_id=depends_on_task_id,
                dependency_type=dependency_type,
                condition=condition,
                is_active=True
            )
            session.add(dependency)
            session.commit()
            session.refresh(dependency)
            return dependency
        finally:
            session.close()

    def get_dependency(self, dependency_id: int) -> Optional[TaskDependency]:
        """Get a task dependency by ID."""
        session = self.Session()
        try:
            return session.query(TaskDependency).filter(TaskDependency.dependency_id == dependency_id).first()
        finally:
            session.close()

    def get_dependencies_by_flow(self, flow_config_id: int) -> List[TaskDependency]:
        """Get all dependencies for a Flow configuration."""
        session = self.Session()
        try:
            return session.query(TaskDependency).filter(
                TaskDependency.flow_config_id == flow_config_id
            ).all()
        finally:
            session.close()

    def get_dependencies_by_task(self, task_id: int) -> List[TaskDependency]:
        """Get all task dependencies for a task."""
        session = self.Session()
        try:
            return session.query(TaskDependency).filter(
                TaskDependency.task_id == task_id,
                TaskDependency.is_active == True
            ).all()
        finally:
            session.close()

    def get_dependencies_by_depends_on_task(self, depends_on_task_id: int) -> List[TaskDependency]:
        """Get all task dependencies that depend on a task."""
        session = self.Session()
        try:
            return session.query(TaskDependency).filter(
                TaskDependency.depends_on_task_id == depends_on_task_id,
                TaskDependency.is_active == True
            ).all()
        finally:
            session.close()

    def update_dependency(self, dependency_id: int, dependency_type: Optional[str] = None,
                         condition: Optional[str] = None) -> Optional[TaskDependency]:
        """Update a task dependency."""
        session = self.Session()
        try:
            dependency = session.query(TaskDependency).filter(
                TaskDependency.dependency_id == dependency_id
            ).first()
            if dependency:
                if dependency_type is not None:
                    dependency.dependency_type = dependency_type
                if condition is not None:
                    dependency.condition = condition
                session.commit()
                session.refresh(dependency)
            return dependency
        finally:
            session.close()

    def delete_dependency(self, dependency_id: int) -> bool:
        """Delete a task dependency."""
        session = self.Session()
        try:
            dependency = session.query(TaskDependency).filter(TaskDependency.dependency_id == dependency_id).first()
            if dependency:
                session.delete(dependency)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def get_task_dependency_graph(self, flow_config_id: int) -> Dict[int, List[int]]:
        """Get the dependency graph for a Flow as a dictionary of task_id -> [dependent_task_ids]."""
        session = self.Session()
        try:
            dependencies = session.query(TaskDependency).filter(
                TaskDependency.flow_config_id == flow_config_id,
                TaskDependency.is_active == True
            ).all()
            
            graph = {}
            for dep in dependencies:
                if dep.depends_on_task_id not in graph:
                    graph[dep.depends_on_task_id] = []
                graph[dep.depends_on_task_id].append(dep.task_id)
            
            return graph
        finally:
            session.close()

class FlowExecutionRepository:
    def __init__(self):
        self.engine = create_engine(SQLALCHEMY_CONN)
        self.Session = sessionmaker(bind=self.engine)

    def create_execution(self, flow_config_id: int) -> FlowExecution:
        """Create a new flow execution."""
        session = self.Session()
        try:
            execution = FlowExecution(
                flow_config_id=flow_config_id,
                status=ExecutionStatus.PENDING
            )
            session.add(execution)
            session.commit()
            session.refresh(execution)
            return execution
        finally:
            session.close()

    def get_execution(self, execution_id: int) -> Optional[FlowExecution]:
        """Get an execution by ID."""
        session = self.Session()
        try:
            return session.query(FlowExecution).filter(
                FlowExecution.execution_id == execution_id
            ).first()
        finally:
            session.close()

    def update_execution(self, execution_id: int, status: Optional[str] = None,
                        result: Optional[Dict] = None, error: Optional[str] = None,
                        end_time: Optional[datetime] = None) -> Optional[FlowExecution]:
        """Update an execution."""
        session = self.Session()
        try:
            execution = session.query(FlowExecution).filter(
                FlowExecution.execution_id == execution_id
            ).first()
            if execution:
                if status:
                    execution.status = status
                if result is not None:
                    execution.result = result
                if error is not None:
                    execution.error = error
                if end_time:
                    execution.end_time = end_time
                session.commit()
                session.refresh(execution)
            return execution
        finally:
            session.close()

class TaskExecutionRepository:
    def __init__(self):
        self.engine = create_engine(SQLALCHEMY_CONN)
        self.Session = sessionmaker(bind=self.engine)

    def create_task_execution(self, flow_execution_id: int, task_id: int) -> TaskExecution:
        """Create a new task execution."""
        session = self.Session()
        try:
            task_execution = TaskExecution(
                flow_execution_id=flow_execution_id,
                task_id=task_id,
                status=ExecutionStatus.PENDING
            )
            session.add(task_execution)
            session.commit()
            session.refresh(task_execution)
            return task_execution
        finally:
            session.close()

    def update_task_execution(self, task_execution_id: int, status: Optional[str] = None,
                            result: Optional[Dict] = None, error: Optional[str] = None,
                            end_time: Optional[datetime] = None) -> Optional[TaskExecution]:
        """Update a task execution."""
        session = self.Session()
        try:
            task_execution = session.query(TaskExecution).filter(
                TaskExecution.task_execution_id == task_execution_id
            ).first()
            if task_execution:
                if status:
                    task_execution.status = status
                if result is not None:
                    task_execution.result = result
                if error is not None:
                    task_execution.error = error
                if end_time:
                    task_execution.end_time = end_time
                session.commit()
                session.refresh(task_execution)
            return task_execution
        finally:
            session.close() 