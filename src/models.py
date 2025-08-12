# src/models.py - Updated Database Models

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

Base = declarative_base()

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    path = Column(String(1024), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_active = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    status = Column(String(50), default='active')
    
    # Relationships
    conversations = relationship("Conversation", back_populates="project")
    decisions = relationship("Decision", back_populates="project")
    files_tracked = relationship("FileTracked", back_populates="project")
    checkpoints = relationship("Checkpoint", back_populates="project")
    
    def __repr__(self):
        return f"<Project(name='{self.name}', path='{self.path}')>"

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    command = Column(String(1024))
    context_snapshot = Column(Text)
    response = Column(Text)
    archived = Column(Boolean, default=False)  # For context management
    
    # Relationships
    project = relationship("Project", back_populates="conversations")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, project_id={self.project_id}, command='{self.command}')>"

class Decision(Base):
    __tablename__ = 'decisions'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    category = Column(String(100))
    decision = Column(Text, nullable=False)
    reasoning = Column(Text)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    project = relationship("Project", back_populates="decisions")
    
    def __repr__(self):
        return f"<Decision(id={self.id}, category='{self.category}', decision='{self.decision[:50]}...')>"

class FileTracked(Base):
    __tablename__ = 'files_tracked'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    path = Column(String(1024), nullable=False)
    hash = Column(String(64))  # SHA-256 hash
    last_analyzed = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    insights = Column(Text)  # Cached analysis results
    
    # Relationships
    project = relationship("Project", back_populates="files_tracked")
    
    def __repr__(self):
        return f"<FileTracked(id={self.id}, path='{self.path}', hash='{self.hash[:8]}...')>"

class Checkpoint(Base):
    __tablename__ = 'checkpoints'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    message_id = Column(Integer)  # Reference to conversation ID
    description = Column(String(255), nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    auto_created = Column(Boolean, default=False)  # Distinguish auto vs manual checkpoints
    
    # Relationships
    project = relationship("Project", back_populates="checkpoints")
    
    def __repr__(self):
        return f"<Checkpoint(id={self.id}, description='{self.description}', auto_created={self.auto_created})>"