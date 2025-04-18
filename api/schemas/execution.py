import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..config.db import Base

class ExecutionStatus(Enum):
    PENDING = 'pending'
    RUNNING = 'running'
    SUCCESS = 'success'
    FAILED = 'failed'
    CANCELLED = 'cancelled'

class Execution(Base):
    __tablename__ = 'executions'
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dag_id = Column(String(36), ForeignKey('dags.id'))
    status = Column(SQLEnum(ExecutionStatus), nullable=False, default=ExecutionStatus.PENDING)
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    result = Column(JSON, nullable=True)
    error = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    dag = relationship("DAG", back_populates="executions")

    def __init__(self, dag_id, status=ExecutionStatus.PENDING):
        self.dag_id = dag_id
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'dag_id': self.dag_id,
            'status': self.status.value,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'result': self.result,
            'error': self.error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            dag_id=data['dag_id'],
            status=ExecutionStatus(data.get('status', 'pending'))
        ) 