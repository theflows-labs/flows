import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..config.db import Base

class Task(Base):
    __tablename__ = 'tasks'
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    dag_id = Column(String(36), ForeignKey('dags.id'))
    type = Column(String(50), nullable=False)
    config = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    dag = relationship("DAG", back_populates="tasks")

    def __init__(self, dag_id, type, config=None):
        self.dag_id = dag_id
        self.type = type
        self.config = config or {}

    def to_dict(self):
        return {
            'id': self.id,
            'dag_id': self.dag_id,
            'type': self.type,
            'config': self.config,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            dag_id=data['dag_id'],
            type=data['type'],
            config=data.get('config', {})
        ) 