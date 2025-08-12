# src/cli.py - Updated CLI with Context Management Integration

import os
import sys
import click
from datetime import datetime
from rich.console import Console

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import AgentManager
from api import RidgeAPI
from memory import MemoryManager
from context import ContextManager
from file_tracker import FileTracker
from utils import get_file_hash
from models import Project

console = Console()

@click.group()
def cli():
    """Ridge Base CLI - AI-powered development assistant with memory"""
    pass

@cli.command()
@click.argument('target')
@click.argument('action')
@click.option('--debug', is_flag=True, help='Use debug agent for methodical troubleshooting')
@click.option('--explain', is_flag=True, help='Use professor agent for teaching mode')
@click.option('--manager', is_flag=True, help='Use manager agent for project management')
@click.option('--code', is_flag=True, help='Use code agent for pure coding focus')
@click.option('--deep', is_flag=True, help='Enable web search and deep reasoning')
@click.option('--ultra', is_flag=True, help='Use maximum reasoning (with --deep)')
@click.option('--quick', is_flag=True, help='Use fast responses')
@click.option('--interactive', is_flag=True, help='Enable back-and-forth conversation')
@click.option('--batch', is_flag=True, help='Process multiple targets')
@click.option('--watch', is_flag=True, help='Monitor file changes')
@click.option('--dry-run', is_flag=True, help='Show what would happen without executing')
@click.option('--allow-all', is_flag=True, help='Skip approval prompts')
def main(target, action, **flags):
    """Main command: ridge [target] [action] --[flags]"""
    
    # Initialize managers
    agent_manager = AgentManager()
    api = RidgeAPI()
    memory_manager = MemoryManager()
    file_tracker = FileTracker()
    
    # Log the command for memory
    command_str = f"ridge {target} {action}"
    flag_str = " ".join([f"--{k}" for k, v in flags.items() if v])
    if flag_str:
        command_str += f" {flag_str}"
    
    try:
        # Select agent based on flags
        mode_flags = {k: v for k, v in flags.items() if k in ['debug', 'explain', 'manager', 'code']}
        agent = agent_manager.select_agent_from_flags(mode_flags)
        
        # Build context from memory
        context = {}
        if memory_manager.current_project:
            context = memory_manager.get_context_for_ai()
            
            # Check for file changes if working with files
            if os.path.isfile(target):
                # Update file tracking
                rel_path = os.path.relpath(target, memory_manager.current_project.path)
                file_tracker.update_file_tracking(memory_manager.current_project, rel_path)
        
        # Prepare message for AI
        message = f"""
Target: {target}
Action: {action}
Context: {context if context else 'No previous context'}

Please {action} the {target} according to my request.
        """.strip()
        
        # Get response from AI
        response = api.chat_with_agent(agent, message, flags)
        
        console.print("\n[bold]Response:[/bold]")
        console.print(response)
        
        # Log conversation to memory
        if memory_manager.current_project:
            memory_manager.log_conversation(
                command=command_str,
                context_snapshot=str(context),
                response=response
            )
        
        # Handle file watching if requested
        if flags.get('watch'):
            console.print("\n[dim]Watching for file changes... (Press Ctrl+C to stop)[/dim]")
            _watch_files(target, agent, api, memory_manager, file_tracker, flags)
            
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        if memory_manager.current_project:
            memory_manager.log_conversation(
                command=command_str,
                response=f"Error: {e}"
            )

def _watch_files(target, agent, api, memory_manager, file_tracker, flags):
    """Watch for file changes and respond automatically"""
    import time
    
    if not memory_manager.current_project:
        console.print("[red]Cannot watch files without an active project[/red]")
        return
    
    last_check = datetime.now()
    
    try:
        while True:
            time.sleep(2)  # Check every 2 seconds
            
            # Get changed files
            changed_files = file_tracker.get_changed_files(memory_manager.current_project)
            
            if changed_files:
                console.print(f"\n[yellow]Detected {len(changed_files)} file changes[/yellow]")
                file_tracker.display_file_changes(memory_manager.current_project)
                
                # Auto-respond to changes
                change_summary = ", ".join([f"{f['path']} ({f['status']})" for f in changed_files])
                message = f"Files changed: {change_summary}. Please review and provide insights."
                
                response = api.chat_with_agent(agent, message, flags)
                console.print(f"\n[bold]Auto-response:[/bold]\n{response}")
                
                # Log to memory
                memory_manager.log_conversation(
                    command=f"auto-watch: {change_summary}",
                    response=response
                )
                
                # Update file tracking
                for file_info in changed_files:
                    if file_info['status'] != 'deleted':
                        file_tracker.update_file_tracking(
                            memory_manager.current_project, 
                            file_info['path']
                        )
            
    except KeyboardInterrupt:
        console.print("\n[dim]File watching stopped[/dim]")

# Memory commands group
@cli.group()
def memory():
    """Memory management commands"""
    pass

@memory.command()
@click.argument('project_name')
@click.option('--path', help='Project path (defaults to current directory)')
def init(project_name, path):
    """Initialize project memory tracking"""
    memory_manager = MemoryManager()
    file_tracker = FileTracker()
    
    project_path = path or os.getcwd()
    
    if memory_manager.init_project(project_name, project_path):
        # Sync initial files  
        console.print("[dim]Scanning project files...[/dim]")
        
        # Get fresh project object
        session = memory_manager.db.get_session()
    try:
        project = session.query(Project).filter_by(name=project_name).first()
        stats = file_tracker.sync_project_files(project)
        console.print(f"[green]✓[/green] Tracking {stats.get('new', 0)} files")
    finally:
        memory_manager.db.close_session(session)

@memory.command()
def status():
    """Show recent project activity"""
    memory_manager = MemoryManager()
    memory_manager.get_recent_activity()

@memory.command()
@click.argument('search_term')
def search(search_term):
    """Search conversations and decisions"""
    memory_manager = MemoryManager()
    memory_manager.search_memory(search_term)

@memory.command()
@click.argument('decision_text')
@click.option('--category', default='general', help='Decision category')
@click.option('--reasoning', help='Reasoning behind the decision')
def decision(decision_text, category, reasoning):
    """Log an important project decision"""
    memory_manager = MemoryManager()
    memory_manager.log_decision(decision_text, category, reasoning)

# Context commands group
@cli.group()
def context():
    """Context management commands"""
    pass

@context.command()
def status():
    """Show context usage and checkpoint information"""
    memory_manager = MemoryManager()
    context_manager = ContextManager()
    
    if memory_manager.current_project:
        context_manager.set_current_project(memory_manager.current_project)
        context_manager.show_context_status()
    else:
        console.print("[red]No active project. Use 'ridge memory init [project]' first.[/red]")

@context.command()
@click.argument('description')
def checkpoint(description):
    """Create a manual checkpoint with description"""
    memory_manager = MemoryManager()
    context_manager = ContextManager()
    
    if memory_manager.current_project:
        context_manager.set_current_project(memory_manager.current_project)
        context_manager.create_checkpoint(description)
    else:
        console.print("[red]No active project. Use 'ridge memory init [project]' first.[/red]")

@context.command('reset-to')
@click.argument('checkpoint_identifier')
def reset_to(checkpoint_identifier):
    """Reset context to a specific checkpoint (use 'latest' for most recent)"""
    memory_manager = MemoryManager()
    context_manager = ContextManager()
    
    if memory_manager.current_project:
        context_manager.set_current_project(memory_manager.current_project)
        context_manager.reset_to_checkpoint(checkpoint_identifier)
    else:
        console.print("[red]No active project. Use 'ridge memory init [project]' first.[/red]")

# File tracking commands group
@cli.group()
def files():
    """File tracking and change detection commands"""
    pass

@files.command()
def sync():
    """Synchronize project files with tracking database"""
    memory_manager = MemoryManager()
    file_tracker = FileTracker()
    
    if memory_manager.current_project:
        console.print("[dim]Synchronizing project files...[/dim]")
        stats = file_tracker.sync_project_files(memory_manager.current_project)
        
        if 'error' not in stats:
            console.print(f"[green]✓[/green] Sync complete:")
            console.print(f"  New: {stats['new']}")
            console.print(f"  Updated: {stats['updated']}")
            console.print(f"  Unchanged: {stats['unchanged']}")
            console.print(f"  Deleted: {stats['deleted']}")
    else:
        console.print("[red]No active project. Use 'ridge memory init [project]' first.[/red]")

@files.command()
def changes():
    """Show recent file changes"""
    memory_manager = MemoryManager()
    file_tracker = FileTracker()
    
    if memory_manager.current_project:
        file_tracker.display_file_changes(memory_manager.current_project)
    else:
        console.print("[red]No active project. Use 'ridge memory init [project]' first.[/red]")

# Health check commands
@cli.command()
def health():
    """Check system health and connections"""
    from database import Database
    
    console.print("[bold]Ridge Base System Health Check[/bold]\n")
    
    # Test database connection
    try:
        db = Database()
        session = db.get_session()
        db.close_session(session)
        console.print("[green]✓[/green] PostgreSQL connection: OK")
    except Exception as e:
        console.print(f"[red]✗[/red] PostgreSQL connection: FAILED - {e}")
    
    # Test Redis connection (if implemented)
    console.print("[yellow]○[/yellow] Redis caching: Not implemented yet")
    
    # Check agent files
    try:
        agent_manager = AgentManager()
        agent_count = len(agent_manager.agents)
        console.print(f"[green]✓[/green] Agent system: {agent_count} agents loaded")
    except Exception as e:
        console.print(f"[red]✗[/red] Agent system: FAILED - {e}")
    
    # Check API
    try:
        api = RidgeAPI()
        console.print("[green]✓[/green] API wrapper: Ready")
    except Exception as e:
        console.print(f"[red]✗[/red] API wrapper: FAILED - {e}")

if __name__ == '__main__':
    cli()