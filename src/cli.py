import click
import os
import sys

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
            click.echo(f"Warning: {target} does not exit")

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


if __name__ == '__main__':
    cli()