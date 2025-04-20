from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Sequence, Boolean, BigInteger, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from enum import Enum

Base = declarative_base()

class ExecutionStatus(str, Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"

class FlowConfiguration(Base):
    __tablename__ = 'flow_configuration'
    __table_args__ = {'schema': 'theflows'}

    config_id = Column(BigInteger, Sequence('flow_configuration_config_id_seq', schema='theflows'), primary_key=True)
    flow_id = Column(Text, nullable=False, unique=True)
    config_details = Column(JSONB, nullable=True)
    config_details_yaml = Column(Text, nullable=True)
    description = Column(Text)
    created_dt = Column(DateTime, server_default='now()', nullable=True)
    updated_dt = Column(DateTime, server_default='now()', nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationship with TaskConfiguration
    tasks = relationship("TaskConfiguration", back_populates="flow_config", cascade="all, delete-orphan")
    dependencies = relationship("TaskDependency", back_populates="flow_config", cascade="all, delete-orphan")
    executions = relationship("FlowExecution", back_populates="flow_config", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<FlowConfiguration(flow_id='{self.flow_id}', config_id={self.config_id})>"

class TaskConfiguration(Base):
    __tablename__ = 'task_configuration'
    __table_args__ = {'schema': 'theflows'}

    task_id = Column(BigInteger, Sequence('task_configuration_task_id_seq', schema='theflows'), primary_key=True)
    task_type = Column(Text, nullable=False)
    flow_config_id = Column(BigInteger, ForeignKey('theflows.flow_configuration.config_id', ondelete='CASCADE'), nullable=False)
    task_sequence = Column(Integer, nullable=False)
    config_details = Column(JSONB, nullable=True)
    config_details_yaml = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    created_dt = Column(DateTime, server_default='now()', nullable=True)
    updated_dt = Column(DateTime, server_default='now()', nullable=True)
    is_active = Column(Boolean, server_default='true', nullable=True)

    # Relationship with FlowConfiguration
    flow_config = relationship("FlowConfiguration", back_populates="tasks")
    dependencies = relationship("TaskDependency", 
                              back_populates="task",
                              foreign_keys="TaskDependency.task_id")
    dependent_tasks = relationship("TaskDependency",
                                 back_populates="depends_on_task",
                                 foreign_keys="TaskDependency.depends_on_task_id")

    def __repr__(self):
        return f"<TaskConfiguration(task_type='{self.task_type}', task_id={self.task_id})>"

class TaskDependency(Base):
    __tablename__ = 'task_dependency'
    __table_args__ = {'schema': 'theflows'}

    dependency_id = Column(BigInteger, primary_key=True)
    flow_config_id = Column(BigInteger, ForeignKey('theflows.flow_configuration.config_id', ondelete='CASCADE'), nullable=False)
    task_id = Column(BigInteger, ForeignKey('theflows.task_configuration.task_id', ondelete='CASCADE'), nullable=False)
    depends_on_task_id = Column(BigInteger, ForeignKey('theflows.task_configuration.task_id', ondelete='CASCADE'), nullable=False)
    dependency_type = Column(Text, nullable=False)
    condition = Column(Text)
    created_dt = Column(DateTime, server_default='now()', nullable=True)
    updated_dt = Column(DateTime, server_default='now()', nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    flow_config = relationship("FlowConfiguration", back_populates="dependencies")
    task = relationship("TaskConfiguration", back_populates="dependencies", foreign_keys=[task_id])
    depends_on_task = relationship("TaskConfiguration", back_populates="dependent_tasks", foreign_keys=[depends_on_task_id])

class FlowExecution(Base):
    __tablename__ = 'flow_execution'
    __table_args__ = {'schema': 'theflows'}

    execution_id = Column(BigInteger, primary_key=True)
    flow_config_id = Column(BigInteger, ForeignKey('theflows.flow_configuration.config_id', ondelete='CASCADE'), nullable=False)
    status = Column(String, nullable=False, default=ExecutionStatus.PENDING)
    start_time = Column(DateTime, server_default='now()', nullable=False)
    end_time = Column(DateTime, nullable=True)
    result = Column(JSONB, nullable=True)
    error = Column(Text, nullable=True)
    logs = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    flow_config = relationship("FlowConfiguration", back_populates="executions")
    task_executions = relationship("TaskExecution", back_populates="flow_execution")

class TaskExecution(Base):
    __tablename__ = 'task_execution'
    __table_args__ = {'schema': 'theflows'}

    task_execution_id = Column(BigInteger, primary_key=True)
    flow_execution_id = Column(BigInteger, ForeignKey('theflows.flow_execution.execution_id', ondelete='CASCADE'), nullable=False)
    task_id = Column(BigInteger, ForeignKey('theflows.task_configuration.task_id', ondelete='CASCADE'), nullable=False)
    status = Column(String, nullable=False, default=ExecutionStatus.PENDING)
    start_time = Column(DateTime, server_default='now()', nullable=False)
    end_time = Column(DateTime, nullable=True)
    result = Column(JSONB, nullable=True)
    error = Column(Text, nullable=True)
    logs = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationships
    flow_execution = relationship("FlowExecution", back_populates="task_executions")
    task = relationship("TaskConfiguration")

class TaskType(Base):
    __tablename__ = 'task_type'
    __table_args__ = {'schema': 'theflows'}

    type_id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False)
    type_key = Column(Text, nullable=False, unique=True)  # e.g., 'python', 'bash'
    description = Column(Text)
    plugin_source = Column(Text, nullable=False)  # e.g., 'airflow_plugin', 'custom'
    config_schema = Column(JSONB, nullable=False)  # JSON Schema for task configuration
    default_config = Column(JSONB)  # Default configuration values
    icon = Column(Text)  # Optional icon identifier
    created_dt = Column(DateTime, server_default='now()', nullable=False)
    updated_dt = Column(DateTime, server_default='now()', nullable=False)
    is_active = Column(Boolean, default=True) 