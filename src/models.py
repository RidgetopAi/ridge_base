from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

Base = declarative_base()

class Project(Base):
    """Project tracking table"""
    __tablename__ = 'projects'

    project_id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    path = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default='active')

    # Relationships
    conversations = relationship("Conversation", back_populates="project")
    decisions = relationship("Decision", back_populates="project")
    files_tracked = relationship("FileTracked", back_populates="project")
    checkpoints = relationship("Checkpoint", back_populates="project")

class Conversation(Base):
    """Conversation history table"""
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.project_id'))
    timestamp = Column(DateTime, default=datetime.utcnow)
    command = Column(Text, nullable=False)
    context_snapshot = Column(Text) #JSON blob
    response = Column(Text)

    # Relationships
    project = relationship("Project", back_populates="conversations")

class Decision(Base):
    """Important decisions tracking"""
    __tablename__ = 'decisions'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.project_id'))
    category = Column(String(100))  # tech_choice, design_decision, etc.
    decision = Column(Text, nullable=False)
    reasoning = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="decisions")

class FileTracked(Base):
    """File tracking for change detection"""
    __tablename__ = 'files_tracked'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.project_id'))
    path = Column(Text, nullable=False)
    hash = Column(String(32))  # MD5 hash
    last_analyzed = Column(DateTime, default=datetime.utcnow)
    insights = Column(Text)  # JSON blob of analysis
    
    # Relationships
    project = relationship("Project", back_populates="files_tracked")

class Checkpoint(Base):
    """Context checkpoints for memory management"""
    __tablename__ = 'checkpoints'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.project_id'))
    message_id = Column(Integer)  # Reference to conversation
    description = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="checkpoints")

class DatabaseManager:
    """Manages database connections and operations"""
    
    def __init__(self, db_url=None):
        if db_url is None:
            # Default connection from our docker setup
            db_url = "postgresql://ridge_user:ridge_pass@localhost:5433/ridge_base"
        
        self.engine = create_engine(db_url)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create tables if they don't exist
        Base.metadata.create_all(bind=self.engine)
        print("✅ Database models initialized")

    def get_session(self):
        """Get database session"""
        return self.SessionLocal()

    def close_session(self, session):
        """Close database session"""
        session.close()
