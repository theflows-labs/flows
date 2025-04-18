from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from flows.plugin_core.metadata.models import DAGConfiguration, TaskConfiguration, TaskDependency
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
import json
from datetime import datetime

from ..constants import SQLALCHEMY_CONN

class DAGConfigurationRepository:
    def __init__(self):
        # Initialize database connection
        self.engine = create_engine(SQLALCHEMY_CONN)
        self.Session = sessionmaker(bind=self.engine)

    def create_dag_config(self, dag_id: str, config_details: Dict[str, Any], description: Optional[str] = None) -> DAGConfiguration:
        """Create a new DAG configuration."""
        session = self.Session()
        try:
            # Convert dictionary to JSON string
            config_json = json.dumps(config_details, default=self._json_serializer)
            dag_config = DAGConfiguration(
                dag_id=dag_id,
                config_details=config_json,
                description=description,
                is_active=True
            )
            session.add(dag_config)
            session.commit()
            session.refresh(dag_config)
            return dag_config
        finally:
            session.close()

    def _json_serializer(self, obj):
        """Custom JSON serializer for objects that are not JSON serializable."""
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def get_dag_config(self, config_id: int) -> Optional[DAGConfiguration]:
        """Get a DAG configuration by ID."""
        session = self.Session()
        try:
            return session.query(DAGConfiguration).filter(DAGConfiguration.config_id == config_id).first()
        finally:
            session.close()

    def get_dag_config_by_dag_id(self, dag_id: str) -> Optional[DAGConfiguration]:
        """Get a DAG configuration by DAG ID."""
        session = self.Session()
        try:
            return session.query(DAGConfiguration).filter(DAGConfiguration.dag_id == dag_id).first()
        finally:
            session.close()

    def update_dag_config(self, config_id: int, config_details: Dict[str, Any], description: Optional[str] = None) -> Optional[DAGConfiguration]:
        """Update a DAG configuration."""
        session = self.Session()
        try:
            dag_config = session.query(DAGConfiguration).filter(DAGConfiguration.config_id == config_id).first()
            if dag_config:
                # Convert dictionary to JSON string
                config_json = json.dumps(config_details, default=self._json_serializer)
                dag_config.config_details = config_json
                if description is not None:
                    dag_config.description = description
                session.commit()
                session.refresh(dag_config)
            return dag_config
        finally:
            session.close()

    def delete_dag_config(self, config_id: int) -> bool:
        """Delete a DAG configuration and its associated tasks."""
        session = self.Session()
        try:
            dag_config = session.query(DAGConfiguration).filter(DAGConfiguration.config_id == config_id).first()
            if dag_config:
                session.delete(dag_config)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def get_all_active_dag_configs(self) -> List[DAGConfiguration]:
        """Get all active DAG configurations."""
        session = self.Session()
        try:
            return session.query(DAGConfiguration).filter_by(is_active=True).all()
        finally:
            session.close()

class TaskConfigurationRepository:
    def __init__(self):
        # Initialize database connection
        self.engine = create_engine(SQLALCHEMY_CONN)
        self.Session = sessionmaker(bind=self.engine)

    def create_task_config(self, dag_config_id: int, task_type: str, task_sequence: int, 
                         config_details: Optional[Dict[str, Any]] = None, description: Optional[str] = None) -> TaskConfiguration:
        """Create a new task configuration."""
        session = self.Session()
        try:
            # Convert dictionary to JSON string
            config_json = json.dumps(config_details, default=self._json_serializer)
            task_config = TaskConfiguration(
                dag_config_id=dag_config_id,
                task_type=task_type,
                task_sequence=task_sequence,
                config_details=config_json,
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

    def get_task_configs_by_dag_config(self, dag_config_id: int) -> List[TaskConfiguration]:
        """Get all task configurations for a DAG configuration."""
        session = self.Session()
        try:
            return session.query(TaskConfiguration).filter(
                TaskConfiguration.dag_config_id == dag_config_id
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

    def create_dependency(self, dag_config_id: int, task_id: int, depends_on_task_id: int, 
                         dependency_type: str = 'success') -> TaskDependency:
        """Create a new task dependency."""
        session = self.Session()
        try:
            dependency = TaskDependency(
                dag_config_id=dag_config_id,
                task_id=task_id,
                depends_on_task_id=depends_on_task_id,
                dependency_type=dependency_type,
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

    # def get_dependencies_by_dag_config(self, dag_config_id: int) -> List[TaskDependency]:
    #     """Get all task dependencies for a DAG configuration."""
    #     session = self.Session()
    #     try:
    #         return session.query(TaskDependency).filter(
    #             TaskDependency.dag_config_id == dag_config_id,
    #             TaskDependency.is_active == True
    #         ).all()
    #     finally:
    #         session.close()

    def get_dependencies_by_dag(self, dag_config_id: int) -> List[TaskDependency]:
        """Get all task dependencies for a DAG configuration."""
        session = self.Session()
        try:
            return session.query(TaskDependency).filter(
                TaskDependency.dag_config_id == dag_config_id,
                TaskDependency.is_active == True
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
                         is_active: Optional[bool] = None) -> Optional[TaskDependency]:
        """Update a task dependency."""
        session = self.Session()
        try:
            dependency = session.query(TaskDependency).filter(TaskDependency.dependency_id == dependency_id).first()
            if dependency:
                if dependency_type is not None:
                    dependency.dependency_type = dependency_type
                if is_active is not None:
                    dependency.is_active = is_active
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

    def get_task_dependency_graph(self, dag_config_id: int) -> Dict[int, List[int]]:
        """Get the dependency graph for a DAG as a dictionary of task_id -> [dependent_task_ids]."""
        session = self.Session()
        try:
            dependencies = session.query(TaskDependency).filter(
                TaskDependency.dag_config_id == dag_config_id,
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