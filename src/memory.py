# src/memory.py - Updated with Context Management Integration

import os
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

from models import Project, Conversation, Decision, FileTracked, Checkpoint
from database import Database

class MemoryManager:
    def __init__(self):
        self.console = Console()
        self.db = Database()
        self.current_project = None
        
        # Auto-load current project if there's only one active
        self._auto_load_project()
    
    def _auto_load_project(self):
        """Automatically load the most recently active project"""
        session = self.db.get_session()
        try:
            # Get the most recently active project
            project = session.query(Project).filter_by(
                status='active'
            ).order_by(Project.last_active.desc()).first()
        
            if project:
                self.current_project = project
        finally:
            self.db.close_session(session)
    
    def init_project(self, project_name: str, project_path: str = None) -> bool:
        """Initialize or activate a project for memory tracking"""
        if project_path is None:
            project_path = os.getcwd()
        
        session = self.db.get_session()
        try:
            # Check if project already exists
            existing_project = session.query(Project).filter_by(name=project_name).first()
            
            if existing_project:
                self.current_project = existing_project
                existing_project.last_active = datetime.now(timezone.utc)
                existing_project.status = 'active'
                session.commit()
                self.console.print(f"[green]✓[/green] Activated existing project: [bold]{project_name}[/bold]")
            else:
                # Create new project
                new_project = Project(
                    name=project_name,
                    path=project_path,
                    status='active'
                )
                session.add(new_project)
                session.commit()
                self.current_project = new_project
                self.console.print(f"[green]✓[/green] Created new project: [bold]{project_name}[/bold]")
            
            return True
            
        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Error initializing project: {e}[/red]")
            return False
        finally:
            self.db.close_session(session)
    
    def log_conversation(self, command: str, context_snapshot: str = None, response: str = None) -> bool:
        """Log a conversation with auto-checkpoint check"""
        if not self.current_project:
            self.console.print("[red]No active project. Use 'ridge memory init [project]' first.[/red]")
            return False
        
        session = self.db.get_session()
        try:
            conversation = Conversation(
                project_id=self.current_project.id,
                command=command,
                context_snapshot=context_snapshot,
                response=response
            )
            
            session.add(conversation)
            session.commit()
            
            # Check if auto-checkpoint is needed
            self._check_auto_checkpoint(session)
            
            return True
            
        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Error logging conversation: {e}[/red]")
            return False
        finally:
            self.db.close_session(session)
    
    def _check_auto_checkpoint(self, session: Session):
        """Check if auto-checkpoint should be created"""
        if not self.current_project:
            return
        
        # Count non-archived conversations
        conversation_count = session.query(Conversation).filter_by(
            project_id=self.current_project.id,
            archived=False
        ).count()
        
        # Get recent conversations for token estimation
        recent_conversations = session.query(Conversation).filter_by(
            project_id=self.current_project.id,
            archived=False
        ).order_by(Conversation.timestamp.desc()).limit(50).all()
        
        # Estimate tokens (rough approximation)
        estimated_tokens = sum(
            len(conv.context_snapshot or '') + len(conv.response or '')
            for conv in recent_conversations
        ) // 4  # ~4 chars per token
        
        # Check auto-checkpoint conditions
        should_checkpoint = (
            conversation_count > 0 and 
            (conversation_count % 25 == 0 or estimated_tokens > 28000)
        )
        
        if should_checkpoint:
            # Create auto-checkpoint
            latest_conversation = session.query(Conversation).filter_by(
                project_id=self.current_project.id
            ).order_by(Conversation.timestamp.desc()).first()
            
            checkpoint = Checkpoint(
                project_id=self.current_project.id,
                message_id=latest_conversation.id if latest_conversation else 0,
                description=f"Auto-checkpoint at {conversation_count} messages",
                auto_created=True
            )
            
            session.add(checkpoint)
            session.commit()
            
            self.console.print(f"[dim]Auto-checkpoint created at {conversation_count} messages[/dim]")
    
    def log_decision(self, decision_text: str, category: str = "general", reasoning: str = None) -> bool:
        """Log an important project decision"""
        if not self.current_project:
            self.console.print("[red]No active project. Use 'ridge memory init [project]' first.[/red]")
            return False
        
        session = self.db.get_session()
        try:
            decision = Decision(
                project_id=self.current_project.id,
                category=category,
                decision=decision_text,
                reasoning=reasoning
            )
            
            session.add(decision)
            session.commit()
            
            self.console.print(f"[green]✓[/green] Decision logged: [bold]{category}[/bold] - {decision_text[:50]}...")
            return True
            
        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Error logging decision: {e}[/red]")
            return False
        finally:
            self.db.close_session(session)
    
    def search_memory(self, search_term: str) -> None:
        """Search conversations and decisions for a term"""
        if not self.current_project:
            self.console.print("[red]No active project. Use 'ridge memory init [project]' first.[/red]")
            return
        
        session = self.db.get_session()
        try:
            # Search conversations (excluding archived ones)
            conversations = session.query(Conversation).filter(
                Conversation.project_id == self.current_project.id,
                Conversation.archived == False,
                (Conversation.command.ilike(f'%{search_term}%') |
                 Conversation.response.ilike(f'%{search_term}%'))
            ).order_by(Conversation.timestamp.desc()).limit(10).all()
            
            # Search decisions
            decisions = session.query(Decision).filter(
                Decision.project_id == self.current_project.id,
                (Decision.decision.ilike(f'%{search_term}%') |
                 Decision.reasoning.ilike(f'%{search_term}%'))
            ).order_by(Decision.timestamp.desc()).limit(10).all()
            
            self._display_search_results(search_term, conversations, decisions)
            
        finally:
            self.db.close_session(session)
    
    def get_recent_activity(self) -> None:
        """Show recent project activity with beautiful formatting"""
        if not self.current_project:
            self.console.print("[red]No active project. Use 'ridge memory init [project]' first.[/red]")
            return
        
        session = self.db.get_session()
        try:
            # Get recent conversations (non-archived)
            recent_conversations = session.query(Conversation).filter_by(
                project_id=self.current_project.id,
                archived=False
            ).order_by(Conversation.timestamp.desc()).limit(5).all()
            
            # Get recent decisions
            recent_decisions = session.query(Decision).filter_by(
                project_id=self.current_project.id
            ).order_by(Decision.timestamp.desc()).limit(5).all()
            
            # Get checkpoints
            checkpoints = session.query(Checkpoint).filter_by(
                project_id=self.current_project.id
            ).order_by(Checkpoint.timestamp.desc()).limit(3).all()
            
            self._display_recent_activity(recent_conversations, recent_decisions, checkpoints)
            
        finally:
            self.db.close_session(session)
    
    def _display_search_results(self, search_term: str, conversations: List[Conversation], decisions: List[Decision]):
        """Display search results with Rich formatting"""
        self.console.print(f"\n[bold]Search Results for '[cyan]{search_term}[/cyan]'[/bold]\n")
        
        if conversations:
            table = Table(title="Conversations")
            table.add_column("Date", style="dim", width=12)
            table.add_column("Command", style="cyan", width=30)
            table.add_column("Preview", style="white", width=50)
            
            for conv in conversations:
                date_str = conv.timestamp.strftime("%m/%d %H:%M")
                command = conv.command[:30] if conv.command else "N/A"
                preview = (conv.response[:50] + "...") if conv.response else "No response"
                table.add_row(date_str, command, preview)
            
            self.console.print(table)
        
        if decisions:
            table = Table(title="Decisions")
            table.add_column("Date", style="dim", width=12)
            table.add_column("Category", style="green", width=15)
            table.add_column("Decision", style="white", width=60)
            
            for decision in decisions:
                date_str = decision.timestamp.strftime("%m/%d %H:%M")
                category = decision.category or "general"
                decision_text = decision.decision[:60] if decision.decision else "N/A"
                table.add_row(date_str, category, decision_text)
            
            self.console.print(table)
        
        if not conversations and not decisions:
            self.console.print(f"[yellow]No results found for '{search_term}'[/yellow]")
    
    def _display_recent_activity(self, conversations: List[Conversation], decisions: List[Decision], checkpoints: List[Checkpoint]):
        """Display recent activity with Rich formatting"""
        
        # Project info panel
        project_info = f"""
[bold]Project:[/bold] {self.current_project.name}
[bold]Path:[/bold] {self.current_project.path}
[bold]Last Active:[/bold] {self.current_project.last_active.strftime("%Y-%m-%d %H:%M")}
        """.strip()
        
        panel = Panel(
            project_info,
            title="[bold]Project Status[/bold]",
            border_style="blue"
        )
        self.console.print(panel)
        
        # Recent conversations
        if conversations:
            table = Table(title="Recent Conversations")
            table.add_column("Time", style="dim", width=12)
            table.add_column("Command", style="cyan", width=35)
            table.add_column("Status", style="green", width=10)
            
            for conv in conversations:
                time_str = conv.timestamp.strftime("%m/%d %H:%M")
                command = conv.command[:35] if conv.command else "N/A"
                status = "✓" if conv.response else "⏳"
                table.add_row(time_str, command, status)
            
            self.console.print(table)
        else:
            self.console.print("[dim]No recent conversations[/dim]")
        
        # Recent decisions
        if decisions:
            table = Table(title="Recent Decisions")
            table.add_column("Date", style="dim", width=12)
            table.add_column("Category", style="green", width=15)
            table.add_column("Decision", style="white", width=50)
            
            for decision in decisions:
                date_str = decision.timestamp.strftime("%m/%d %H:%M")
                category = decision.category or "general"
                decision_text = decision.decision[:50] if decision.decision else "N/A"
                table.add_row(date_str, category, decision_text)
            
            self.console.print(table)
        else:
            self.console.print("[dim]No recent decisions[/dim]")
        
        # Checkpoints
        if checkpoints:
            table = Table(title="Recent Checkpoints")
            table.add_column("Date", style="dim", width=12)
            table.add_column("Description", style="cyan", width=40)
            table.add_column("Type", style="green", width=10)
            
            for checkpoint in checkpoints:
                date_str = checkpoint.timestamp.strftime("%m/%d %H:%M")
                description = checkpoint.description[:40] if checkpoint.description else "N/A"
                checkpoint_type = "Auto" if checkpoint.auto_created else "Manual"
                table.add_row(date_str, description, checkpoint_type)
            
            self.console.print(table)
        else:
            self.console.print("[dim]No checkpoints created yet[/dim]")
    
    def get_context_for_ai(self, limit_conversations: int = 20) -> Dict[str, Any]:
        """Get relevant context for AI conversations"""
        if not self.current_project:
            return {}
        
        session = self.db.get_session()
        try:
            # Get recent non-archived conversations
            recent_conversations = session.query(Conversation).filter_by(
                project_id=self.current_project.id,
                archived=False
            ).order_by(Conversation.timestamp.desc()).limit(limit_conversations).all()
            
            # Get recent decisions
            recent_decisions = session.query(Decision).filter_by(
                project_id=self.current_project.id
            ).order_by(Decision.timestamp.desc()).limit(10).all()
            
            # Get tracked files
            tracked_files = session.query(FileTracked).filter_by(
                project_id=self.current_project.id
            ).order_by(FileTracked.last_analyzed.desc()).limit(10).all()
            
            context = {
                "project": {
                    "name": self.current_project.name,
                    "path": self.current_project.path,
                    "status": self.current_project.status
                },
                "conversations": [
                    {
                        "command": conv.command,
                        "response": conv.response,
                        "timestamp": conv.timestamp.isoformat()
                    } for conv in reversed(recent_conversations)  # Chronological order
                ],
                "decisions": [
                    {
                        "category": dec.category,
                        "decision": dec.decision,
                        "reasoning": dec.reasoning,
                        "timestamp": dec.timestamp.isoformat()
                    } for dec in recent_decisions
                ],
                "tracked_files": [
                    {
                        "path": file.path,
                        "insights": file.insights,
                        "last_analyzed": file.last_analyzed.isoformat()
                    } for file in tracked_files
                ]
            }
            
            return context
            
        finally:
            self.db.close_session(session)