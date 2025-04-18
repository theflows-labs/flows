import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, JSON, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from ..config.db import Base

class DAG(Base):
    __tablename__ = 'dags'
    __table_args__ = {'extend_existing': True}

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    schedule = Column(String(50), nullable=True)
    start_date = Column(DateTime, nullable=True)
    nodes = Column(JSON, nullable=True)
    edges = Column(JSON, nullable=True)
    yaml_content = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    tasks = relationship("Task", back_populates="dag", cascade="all, delete-orphan")
    executions = relationship("Execution", back_populates="dag", cascade="all, delete-orphan")

    def __init__(self, name, description, schedule, start_date, nodes, edges):
        self.name = name
        self.description = description
        self.schedule = schedule
        self.start_date = start_date
        self.nodes = nodes
        self.edges = edges

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'schedule': self.schedule,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'nodes': self.nodes,
            'edges': self.edges,
            'yaml_content': self.yaml_content,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            name=data['name'],
            description=data['description'],
            schedule=data['schedule'],
            start_date=datetime.fromisoformat(data['start_date']) if data.get('start_date') else None,
            nodes=data['nodes'],
            edges=data['edges']
        )

    def save(self):
        from ..config.db import SessionLocal
        db = SessionLocal()
        try:
            db.add(self)
            db.commit()
            db.refresh(self)
        finally:
            db.close()

    def delete(self):
        from ..config.db import SessionLocal
        db = SessionLocal()
        try:
            db.delete(self)
            db.commit()
        finally:
            db.close() 