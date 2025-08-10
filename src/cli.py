import click
import os
import sys
from models import DatabaseManager
from rich.console import Console
from rich.table import Table
from memory import MemoryManager
from datetime import datetime

# Initialize rich console for beautiful output
console = Console()

# Add src directory to path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils import file_exists, folder_exists, read_file_content, scan_folder

# Valid targets and actions from design
VALID_TARGETS = ['file', 'folder', 'project','memory', 'context', 'session']
VALID_ACTIONS = ['edit', 'create', 'analyze', 'debug', 'status', 'health', 'explain']

def validate_command(target, action):
    """Enhanced validation with file existence checks"""
    if action not in VALID_ACTIONS:
        raise click.BadParameter(f"Invalid action '{action}'. Valid actions: {', '.join(VALID_ACTIONS)}")
    
    # Check if target is a special command or file/folder
    if target not in VALID_TARGETS:
        # Assume it a file or folder path - check existence
        if not file_exists(target) and not folder_exists(target):
            click.echo(f"Warning: {target} does not exist")

    return True


@click.group()
def cli():
    """Ridge Base CLI - AI Development Partner"""
    pass

# Mode flags - control HOW the AI thinks
@click.option('--deep', is_flag=True, help='Web search + reasoning')
@click.option('--ultra', is_flag=True, help='Maximum reasoning power')
@click.option('--debug', is_flag=True, help='Debug agent mode')
@click.option('--code', is_flag=True, help='Pure coding focus')
@click.option('--explain', is_flag=True, help='Teaching Mode')
@click.option('--quick', is_flag=True, help='Fast responses')
@click.option('--manager', is_flag=True, help='Project management mode')

# Behavior flags - control WHAT the AI does
@click.option('--watch', is_flag=True, help='Monitor file changes')
@click.option('--interactive', is_flag=True, help='Back-and-forth conversation')
@click.option('--batch', is_flag=True, help='Process multiple targets')
@click.option('--dry-run', is_flag=True, help='show what would happen')
@click.option('--allow-all', is_flag=True, help='skip approval prompts')

@cli.command()
@click.argument('target')
@click.argument('action')

def main(target, action,deep, ultra, debug, code, explain, quick, manager, watch, interactive, batch, dry_run, allow_all):
    """Main Command: ridge [target] [action]"""

    # Validate input
    validate_command(target, action)
    
    # Collect active flags for processing
    mode_flags = {
        'deep': deep, 'ultra': ultra, 'debug': debug, 'code': code, 'explain': explain, 'quick': quick, 'manager': manager
    }

    behavior_flags = {
        'watch': watch, 'interactive': interactive, 'batch': batch, 'dry_run': dry_run, 'allow_all': allow_all
    }

    # Filter to only active flags
    active_modes = [flag for flag, active in mode_flags.items() if active]
    active_behaviors = [flag for flag, active in behavior_flags.items() if active]

    click.echo(f"Target: {target}")
    click.echo(f"Action: {action}")
    click.echo(f"Mode flags: {active_modes}")
    click.echo(f"Behavior flags: {active_behaviors}")

@cli.group()
def memory():
    """Memory management commands"""
    pass

@memory.command()
@click.argument('project_name')
def init(project_name):
    """Initialize memory for a new project"""
    console.print(f"🧠 Initializing memory for project: [bold]{project_name}[/bold]")
    
    memory_manager = MemoryManager()
    project_data, is_new = memory_manager.init_project(project_name)

    if is_new:
        console.print(f"✅ New project '[bold]{project_name}[/bold]' created and activated")
    else:
        console.print(f"✅ Existing project '[bold]{project_name}[/bold]' reactivated")
    
    console.print(f"📁 Project path: {project_data['path']}")

@memory.command()
def status():
    """Show current project memory status"""
    memory_manager = MemoryManager()
    project = memory_manager.get_current_project()
    
    if not project:
        console.print("❌ No active project found. Run 'ridge memory init [project_name]' first")
        return
    
    console.print(f"📊 Memory Status for [bold]{project.name}[/bold]")
    
    # Get recent activity
    activity = memory_manager.get_recent_activity()
    
    if activity:
        table = Table(title="Recent Activity (Last 7 Days)")
        table.add_column("Type", style="cyan")
        table.add_column("Description", style="magenta")
        table.add_column("Time", style="green")
        
        for item in activity[:10]:  # Show last 10 items
            # Calculate relative time
            time_diff = datetime.utcnow() - item['timestamp']
            if time_diff.days > 0:
                time_str = f"{time_diff.days} days ago"
            elif time_diff.seconds > 3600:
                time_str = f"{time_diff.seconds // 3600} hours ago"
            else:
                time_str = f"{time_diff.seconds // 60} minutes ago"
            
            table.add_row(
                item['type'],
                item['description'][:50] + "..." if len(item['description']) > 50 else item['description'],
                time_str
            )
        
        console.print(table)
    else:
        console.print("No recent activity found")

@memory.command()
@click.argument('search_term')
@click.option('--days', default=30, help='Days back to search (deafault: 30)')
def search(search_term, days):
    """Search through project memory"""
    memory_manager = MemoryManager()
    project = memory_manager.get_current_project()

    if not project:
        console.print("🔴 No active project found. Run 'ridge memory init [project_name]' first")
        return

    console.print(f"🔍 Searching for '[bold]{search_term}[/bold]' in {project.name}")

    results = memory_manager.search_memory(search_term, days)

    if results:
        table = Table(title=f"Search Results ({len(results)} found)")
        table.add_column("Type", style="cyan")
        table.add_column("Content",style="magenta")
        table.add_column("Time", style="green")

        for result in results:
            # Calculate relative time
            time_diff = datetime.utcnow() - result['timestamp']
            if time_diff.days > 0:
                time_str = f"{time_diff.days} days ago"
            elif time_diff.seconds > 3600:
                time_str = f"{time_diff.seconds // 3600} hours ago"
            else:
                time_str = f"{time_diff.seconds // 60} minutes ago"
            
            table.add_row(
                result['type'].title(),
                result['content'][:80] + "..." if len(result['content']) > 80 else result['content'],
                time_str
            )

        console.print(table)
    else:
        console.print(f"No results found for '{search_term}' in the last {days} days")

@memory.command()
@click.argument('decision_text')
@click.option('--category',default='general', help='Decision category (e.g., tech_choice, design)')
@click.option('--reasoning', help='Why this decision was made')
def decision(decision_text, category, reasoning):
    """Log an important project decision"""
    memory_manager = MemoryManager()
    project = memory_manager.get_current_project()

    if not project:
        console.print("🔴 No active project found, Run 'ridge memory init '[project_name]' first")
        return
    
    decision_obj = memory_manager.log_decision(decision_text, category, reasoning)

    if decision_obj:
        console.print(f"🟢 Decision logged: [bold]{decision_text}[/bold]")
        console.print(f"📁 Category: {category}")
        if reasoning:
            console.print(f"💭 Reasoning: {reasoning}")
    else:
        console.print("🔴 failed to log decision")


if __name__ == '__main__':
    cli()