import click
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from sqlalchemy.orm import Session
from models import Project, Checkpoint, Conversation
from database import Database
import json

class ContextManager:
    def __init__(self):
        self.console = Console()
        self.db = Database()
        self.current_project = None

        # Context limits (in tokens)
        self.MAX_CONTEXT_TOKENS = 32000
        self.RECENT_CONTEXT_TOKENS = 8000
        self.FILE_CONTENT_TOKENS = 16000
        self.MEMORY_INSIGHTS_TOKENS = 4000
        self.AGENT_INSTRUCTIONS_TOKENS = 2000
        self.BUFFER_TOKENS = 2000

        #Auto-checkpoint triggers
        self.AUTO_CHECKPOINT_MESSAGE_COUNT = 25
        self.AUTO_CHECKPOINT_SIZE_THRESHOLD = 28000 #28K tokens triggers checkpoint 

    def set_current_project(self, project: Project):
        """Set the active project for context operations"""
        self.current_project = project

    def show_context_status(self) -> None:
        """Display current context usage and checkpoint information"""
        if not self.current_project:
            self.console.print("[red]No active project. Use 'ridge memory init [project]' first.[/red]")
            return
        
        session = self.db.get_session()
        try:
            # Get conversation count
            conversation_count = session.query(Conversation).filter_by(
                project_id=self.current_project.id).count()
            
            # Get checkpoints
            checkpoints = session.query(Checkpoint).filter_by(
                project_id=self.current_project.id
            ).order_by(Checkpoint.timestamp.desc()).limit(50).all()
            
            # Estimate current context size
            recent_conversations = session.query(Conversation).filter_by(
                project_id=self.current_project.id
            ).order_by(Conversation.timestamp.desc()).limit(50).all()

            estimated_tokens = self._estimate_context_tokens(recent_conversations)

            # Create status display
            self._display_context_status(conversation_count, checkpoints, estimated_tokens)

        finally:
            self.db.close_session(session)
        
    def create_checkpoint(self, description: str) -> bool:
        """Create a manual checkpoint with description"""
        if not self.current_project:
            self.console.print("[red]No active project. Use 'ridge memory init [project]' first.[/red]")
            return False

        session = self.db.get_session()
        try:
            # Get latest conversation ID for checkpoint reference
            latest_conversation = session.query(Conversation).filter_by(
                project_id=self.current_project.id
            ).order_by(Conversation.timestamp.desc()).first()

            message_id = latest_conversation.id if latest_conversation else 0

            # Create checkpoint
            checkpoint = Checkpoint(
                project_id=self.current_project.id,
                message_id=message_id,
                description=description,
                timestamp=datetime.now(timezone.utc)
            )

            session.add(checkpoint)
            session.commit()

            self.console.print(f"[green]✓[/green] Checkpoint created: '{description}'")
            return True

        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Error creating checkpoint: {e}[/red]")
            return False
        finally:
            self.db.close_session(session)

    def reset_to_checkpoint(self, checkpoint_identifier: str) -> bool:
        """Reset context to a specific checkpoint"""
        if not self.current_project:
            self.console.print("[red]No active project. Use 'ridge memory init [project]' first.[/red]")
            return False
        
        session = self.db.get_session()
        try:
            checkpoint = None

            if checkpoint_identifier == "latest":
                # Get the most recent checkpoint
                checkpoint = session.query(Checkpoint).filter_by(
                    project_id=self.current_project.id
                ).order_by(Checkpoint.timestamp.desc()).first()
            else:
                # Find checkpoint by description
                checkpoint = session.query(Checkpoint).filter_by(
                    project_id=self.current_project.id,
                    description=checkpoint_identifier
                ).first()
            
            if not checkpoint:
                self.console.print(f"[red]Checkpoint '{checkpoint_identifier}' not found.[/red]")
                return False
            
            # Archive conversations after checkpoint
            conversations_to_archive = session.query(Conversation).filter(
                Conversation.project_id == self.current_project.id,
                Conversation.id > checkpoint.message_id
            ).all()

            if conversations_to_archive:
                # Mark conversations as archived (soft delete)
                for conv in conversations_to_archive:
                    conv.archived = True

                session.commit()

                self.console.print(f"[green]✓[/green]) Reset to checkpoint '{checkpoint.description}'")
                self.console.print(f"[dim]Archived {len(conversations_to_archive)} conversations after checkpoint]/dim]")
            else:
                self.console.print(f"[yellow]Already at checkpoint '{checkpoint.description}'[/yellow]")
            
            return True
        except Exception as e:
            session.rollback()
            self.console.print(f"[red]error resetting to checkpoint: {e}[/red]")
            return False
        finally:
            self.db.close_session(session)
        
    def should_auto_checkpoint(self,conversation_count: int, estimated_tokens: int) -> bool:
        """Determine if an auto_checkpoint should be created"""
        return (
            conversation_count > 0 and 
            (conversation_count % self.AUTO_CHECKPOINT_MESSAGE_COUNT == 0 or
             estimated_tokens > self.AUTO_CHECKPOINT_SIZE_THRESHOLD)
        )

    def create_auto_checkpoint(self) -> bool:
        """Create an automatic checkpoint"""
        if not self.current_project:
            return False 
        
        session = self.db.get_session()
        try:
            conversation_count = session.query(Conversation).filter_by(
                project_id=self.current_project.id,
                archived=False
            ).count()

            description = f"auto-checkpoint at {conversation_count} messages"

            # Create checkpoint 
            latest_conversation = session.query(Conversation).filter_by(
                project_id=self.current_project.id
            ).order_by(Conversation.timestamp.desc()).first()

            message_id = latest_conversation.id if latest_conversation else 0

            checkpoint = Checkpoint(
                project_id=self.current_project.id,
                message_id=message_id,
                description=description,
                timestamp=datetime.now(timezone.utc),
                auto_created=True
            )

            session.add(checkpoint)
            session.commit()

            self.console.print(f"]dim]Auto-checkpoint created: {description}[/dim]")
            return True
        
        except Exception as e:
            session.rollback()
            return False
        finally:
            self.db.close_session(session)
        
    def _estimate_context_tokens(self, conversations: List[Conversation]) -> int:
        """rough estimation of token count for conversations"""
        total_chars = 0
        for conv in conversations:
            if conv.context_snapshot:
                total_chars += len(conv.context_snapshot)
            if conv.response:
                total_chars += len(conv.response)

        # Rough approximation: ~4 characters per token
        return total_chars // 4 
    
    def _display_context_status(self, conversation_count: int, checkpoints: List[Checkpoint], estimated_tokens: int):
        """display context status with Rich formatting"""

        # Context usage panel
        usage_percentage = min(100, (estimated_tokens / self.MAX_CONTEXT_TOKENS) * 100)

        if usage_percentage < 60:
            color = "green"
        elif usage_percentage < 85:
            color = "yellow"
        else:
            color = "red"
        
        usage_text = f"[{color}]{estimated_tokens:,}[/{color}] / {self.MAX_CONTEXT_TOKENS:,} tokens ({usage_percentage:.1f}%)"

        # Create status panel
        status_content = f"""
[bold]Project: [/bold] {self.current_project.name}
[bold]Conversations:[/bold] {conversation_count:,} total
[bold]Context Usage:[/bold] {usage_text}
[bold]Next Auto-Checkpoint:[/bold] {self.AUTO_CHECKPOINT_MESSAGE_COUNT -(conversation_count % self.AUTO_CHECKPOINT_MESSAGE_COUNT)} messages
        """.strip()

        panel = Panel(
            status_content,
            title="[bold]Context Status[/bold]",
            border_style="blue"
        )
        self.console.print(panel)

        #Checkpoints table
        if checkpoints:
            table = Table(title="Recent Checkpoints")
            table.add_column("Description", style="cyan")
            table.add_column("Created", style="dim")
            table.add_column("Type", style='green')

            for checkpoint in checkpoints:
                checkpoint_type = "Auto" if getattr(checkpoint, 'auto_created', False) else "Manual"
                time_str = checkpoint.timestamp.strftime("%Y-%m-%d %H:%M")
                table.add_row(checkpoint.description, time_str, checkpoint_type)

            self.console.print(table)
        else:
            self.console.print("[dim]No checkpoints created yet[/dim]")
