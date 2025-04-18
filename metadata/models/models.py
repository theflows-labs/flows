from sqlalchemy import Column, Integer, String, JSON, DateTime, ForeignKey, Sequence, Boolean, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class DAGConfiguration(Base):
    __tablename__ = 'dag_configuration'
    __table_args__ = {'schema': 'theflows'}

    config_id = Column(BigInteger, Sequence('dag_configuration_config_id_seq', schema='theflows'), primary_key=True)
    dag_id = Column(String, nullable=False, unique=True)
    config_details = Column(JSON, nullable=False)
    description = Column(Text)
    created_dt = Column(DateTime, server_default='now()', nullable=True)
    updated_dt = Column(DateTime, server_default='now()', nullable=True)
    is_active = Column(Boolean, default=True)

    # Relationship with TaskConfiguration
    tasks = relationship("TaskConfiguration", back_populates="dag_config", cascade="all, delete-orphan")
    dependencies = relationship("TaskDependency", back_populates="dag_config", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<DAGConfiguration(dag_id='{self.dag_id}', config_id={self.config_id})>"

class TaskConfiguration(Base):
    __tablename__ = 'task_configuration'
    __table_args__ = {'schema': 'theflows'}

    task_id = Column(BigInteger, Sequence('task_configuration_task_id_seq', schema='theflows'), primary_key=True)
    task_type = Column(String, nullable=False)
    dag_config_id = Column(BigInteger, ForeignKey('theflows.dag_configuration.config_id', ondelete='CASCADE'), nullable=False)
    task_sequence = Column(Integer, nullable=False)
    config_details = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    created_dt = Column(DateTime, server_default='now()', nullable=True)
    updated_dt = Column(DateTime, server_default='now()', nullable=True)
    is_active = Column(Boolean, server_default='true', nullable=True)

    # Relationship with DAGConfiguration
    dag_config = relationship("DAGConfiguration", back_populates="tasks")
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
    dag_config_id = Column(BigInteger, ForeignKey('theflows.dag_configuration.config_id', ondelete='CASCADE'), nullable=False)
    task_id = Column(BigInteger, ForeignKey('theflows.task_configuration.task_id', ondelete='CASCADE'), nullable=False)
    depends_on_task_id = Column(BigInteger, ForeignKey('theflows.task_configuration.task_id', ondelete='CASCADE'), nullable=False)
    dependency_type = Column(String, nullable=False)  # e.g., 'success', 'failure', 'skip', 'all_done'
    condition = Column(Text)  # Optional condition for the dependency
    created_dt = Column(DateTime, default=datetime.utcnow)
    updated_dt = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    # Relationships
    dag_config = relationship("DAGConfiguration", back_populates="dependencies")
    task = relationship("TaskConfiguration", back_populates="dependencies", foreign_keys=[task_id])
    depends_on_task = relationship("TaskConfiguration", back_populates="dependent_tasks", foreign_keys=[depends_on_task_id]) 