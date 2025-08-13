# src/cli.py - Updated CLI with Context Management Integration

import os
import sys
import click
from datetime import datetime
from rich.console import Console

#local imports
from agents import AgentManager
from api import RidgeAPI
from memory import MemoryManager
from context import ContextManager
from file_tracker import FileTracker
from utils import get_file_hash
from models import Project
from utils import read_file_content

# Add the src directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
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
def main(target, action, debug, explain, manager,code, deep, ultra, quick, interactive, batch, watch, dry_run, allow_all):
    """Main command: ridge [target] [action] --[flags]"""
    
    # Only handle 'analyze' action for now
    if action != 'analyze':
        click.echo(f"Action '{action}' not implemented yet. Currently supports: analyze")
        return
    
    # Collect mode flags
    mode_flags = {
        'debug': debug,
        'explain': explain,
        'code': code,
        'manager': manager,
        'deep': deep,
        'ultra': ultra,
        'quick': quick
    }

    # Collect behavior flags
    behavior_flags = {
        'interactive': interactive,
        'batch': batch,
        'watch': watch,
        'dry_run': dry_run,
        'allow_all': allow_all
    }

    try:
        # Initialize systems
        #from agents import AgentManager
        #from api import RidgeAPI
        #from memory import MemoryManager
        #from utils import read_file_content

        agent_manager = AgentManager() 
        api = RidgeAPI()
        memory_manager = MemoryManager()

        # Ensure we have an active project
        if not memory_manager.current_project:
            click.echo("No active project found. Please run 'ridge memory init [project-name]' first.")
            return
        
        # Check if target exists
        if not os.path.exists(target):
            click.echo(f"Error: Target '[target]' does not exist.")
            return
        
        # Read file content
        file_content = read_file_content(target)
        if not file_content:
            click.echo(f"Error: Could not read '{target}' or file is empty.")
            return
        
        # Select agent based on flags
        agent = agent_manager.select_agent_from_flags(mode_flags)
        
        # Build the analysis prompt
        prompt = f"""Please analyze this file: {target}

File content:
{file_content}

Please provide insights about:
- Code structure and quality
- Potential issues or improvements
- Best practices recommendations
- Any concerns or suggestions

File path: {target}
"""
           

        if dry_run:
            click.echo(f"\n[DRY RUN] Would analyze {target} with {agent.name} agent")

            click.echo(f"Prompt preview: {prompt[:200]}...")
            return

        # Show what we're doing
        click.echo(f"\n🔍 Analyzing {target} with {agent.name} agent...")

        # Get AI response
        response = api.chat_with_agent(agent, prompt, mode_flags)

        # Display response with Rich formatting
        from rich.console import Console
        from rich.panel import Panel

        console = Console()

        # Create a panel with the analysis
        panel = Panel(
            response,
            title=f"analysis of {target}",
            title_align="left",
            border_style="blue",
            padding=(1, 2)
        )  
        console.print(panel)

        # Log the conversation to memory
        command = f"ridge {target} analyze"
        if any(mode_flags.values()):
            active_flags = [k for k, v in mode_flags.items() if v]
            command += f" --{'--'.join(active_flags)}"

        memory_manager.log_conversation(
            command=command,
            context_snapshot=f"Analyzed {target} with {agent.name} agent",
            response=response[:500] + "..." if len(response) > 500 else response
        )

        click.echo(f"\n✔️ Analysis complete and logged to project memory")
    
    except Exception as e:
        click.echo(f"Error during analysis: {str(e)}")
        console.print_exception()


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