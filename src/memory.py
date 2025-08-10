from models import DatabaseManager, Project, Conversation, Decision, FileTracked, Checkpoint
from datetime import datetime, timedelta
import json
import os

class MemoryManager:
    """Handles project memory operations"""

    def __init__(self):
        self.db = DatabaseManager()
        self.current_project = None

    def init_project(self, name, path=None):
        """Initialize a new project in memory"""
        if path is None:
            path = os.getcwd()
        
        session = self.db.get_session() 
        try:
            # Check if project already exists
            existing = session.query(Project).filter_by(name=name).first()
            if existing:
                existing.last_active = datetime.utcnow()
                existing.status = 'active'
                session.commit()
                #  Get data before closing session
                project_data = {
                    'name': existing.name,
                    'path': existing.path,
                    'project_id': existing.project_id
                }
                self.current_project = existing 
                return project_data, False # False = not newly created

            # Create new project
            project = Project(
                name=name,
                path=path,
                status='active'
            )
            session.add(project)
            session.commit()

            # Get data before closing session
            project_data = {
                    'name': project.name,
                    'path': project.path,
                    'project_id': project.project_id
                }
            self.current_project = project
            return project_data, True # True = newly created

        finally:
            self.db.close_session(session)

    def get_current_project(self):
        """Get or detect current project"""
        if self.current_project:
            return self.current_project
        
        # Try to detect project from current directory
        cwd = os.getcwd()
        session = self.db.get_session()
        try:
            project = session.query(Project).filter_by(path=cwd).first()
            if project:
                self.current_project = project
                return project
            return None
        finally:
            self.db.close_session(session)

    def log_conversation(self, command, response, context=None):
        """Log a conversation to memory"""
        project = self.get_current_project()
        if not project:
            return None

        session = self.db.get_session()
        try:
            conversation = Conversation(
                project_id=project.project_id,
                command=command, 
                response=response,
                context_snapshot=json.dumps(context) if context else None
            )
            session.add(conversation)

            # Update project last_active
            project.last_active = datetime.utcnow()
            session.commit()

            return conversation
        finally:
            self.db.close_session(session)

    def log_decision(self, decision_text, category=None, reasoning=None):
        """Log an important decision"""
        project = self.get_current_project()
        if not project:
            return None
        
        session = self.db.get_session()
        try:
            decision = Decision(
                project_id=project.project_id,
                decision=decision_text,
                category=category or 'general',
                reasoning=reasoning
            )
            session.add(decision)
            session.commit()
            return decision
        finally:
            self.db.close_session(session)

    def search_memory(self, search_term, days_back=30):
        """Search through project memory"""
        project = self.get_current_project()
        if not project:
            return []
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        session = self.db.get_session()
        try:
            results = []

            # Search conversations 
            conversations = session.query(Conversation)\
                .filter(Conversation.project_id == project.project_id)\
                .filter(Conversation.timestamp >= cutoff_date)\
                .filter(Conversation.response.contains(search_term))\
                .order_by(Conversation.timestamp.desc())\
                .limit(10).all()

            for conv in conversations:
                results.append({
                    'type': 'conversation',
                    'content': conv.response[:200] + '...',
                    'timestamp': conv.timestamp,
                    'command': conv.command
                })

            # Search decisions
            decisions = session.query(Decision)\
                .filter(Decision.project_id == project.project_id)\
                .filter(Decision.timestamp >= cutoff_date)\
                .filter(Decision.decision.contains(search_term))\
                .order_by(Decision.timestamp.desc())\
                .limit(5).all()

            for decision in decisions:
                results.append({
                    'type': 'decision',
                    'content': decision.decision,
                    'timestamp': decision.timestamp,
                    'category': decision.category 
                })
            
            return sorted(results, key=lambda x: x['timestamp'], reverse=True)

        finally:
            self.db.close_session(session)

    def get_recent_activity(self, days_back=7):
        """Get recent project activity"""
        project = self.get_current_project()
        if not project:
            return []
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        session = self.db.get_session()
        try:
            activity = []
            
            # Recent conversations
            conversations = session.query(Conversation)\
                .filter(Conversation.project_id == project.project_id)\
                .filter(Conversation.timestamp >= cutoff_date)\
                .order_by(Conversation.timestamp.desc())\
                .limit(5).all()
            
            for conv in conversations:
                activity.append({
                    'type': 'Conversation',
                    'description': conv.command,
                    'timestamp': conv.timestamp
                })
            
            # Recent decisions
            decisions = session.query(Decision)\
                .filter(Decision.project_id == project.project_id)\
                .filter(Decision.timestamp >= cutoff_date)\
                .order_by(Decision.timestamp.desc())\
                .limit(3).all()
            
            for decision in decisions:
                activity.append({
                    'type': 'Decision',
                    'description': f"[{decision.category}] {decision.decision}",
                    'timestamp': decision.timestamp
                })
            
            return sorted(activity, key=lambda x: x['timestamp'], reverse=True)
            
        finally:
            self.db.close_session(session)