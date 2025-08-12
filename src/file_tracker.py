# src/file_tracker.py - File Change Detection System

import os
import hashlib
from datetime import datetime, timezone
from typing import List, Dict, Optional, Set
from pathlib import Path
from sqlalchemy.orm import Session
from rich.console import Console
from rich.table import Table

from models import FileTracked, Project
from database import Database

class FileTracker:
    def __init__(self):
        self.console = Console()
        self.db = Database()
        
        # File extensions to track by default
        self.tracked_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.cpp', '.c', '.h',
            '.css', '.scss', '.html', '.vue', '.go', '.rs', '.rb', '.php',
            '.sql', '.md', '.txt', '.json', '.yaml', '.yml', '.toml', '.ini',
            '.sh', '.bat', '.ps1', '.dockerfile', '.gitignore', '.env'
        }
        
        # Directories to ignore
        self.ignored_dirs = {
            '__pycache__', '.git', 'node_modules', '.next', 'dist', 'build',
            '.vscode', '.idea', 'venv', 'env', '.env', 'target', 'vendor'
        }
    
    def get_file_hash(self, file_path: str) -> Optional[str]:
        """Calculate SHA-256 hash of file content"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()
        except (IOError, OSError) as e:
            self.console.print(f"[red]Error reading file {file_path}: {e}[/red]")
            return None
    
    def should_track_file(self, file_path: Path) -> bool:
        """Determine if a file should be tracked"""
        # Check if file extension is in tracked list
        if file_path.suffix.lower() not in self.tracked_extensions:
            return False
        
        # Check if file is in ignored directory
        for part in file_path.parts:
            if part in self.ignored_dirs:
                return False
        
        # Check file size (ignore very large files > 1MB)
        try:
            if file_path.stat().st_size > 1024 * 1024:  # 1MB
                return False
        except OSError:
            return False
        
        return True
    
    def scan_project_files(self, project: Project) -> List[str]:
        """Scan project directory for trackable files"""
        project_path = Path(project.path)
        tracked_files = []
        
        try:
            for file_path in project_path.rglob('*'):
                if file_path.is_file() and self.should_track_file(file_path):
                    # Store relative path from project root
                    relative_path = file_path.relative_to(project_path)
                    tracked_files.append(str(relative_path))
        except Exception as e:
            self.console.print(f"[red]Error scanning project files: {e}[/red]")
        
        return tracked_files
    
    def update_file_tracking(self, project: Project, file_path: str, insights: str = None) -> bool:
        """Update or create file tracking record"""
        session = self.db.get_session()
        try:
            full_path = os.path.join(project.path, file_path)
            file_hash = self.get_file_hash(full_path)
            
            if not file_hash:
                return False
            
            # Check if file is already tracked
            tracked_file = session.query(FileTracked).filter_by(
                project_id=project.id,
                path=file_path
            ).first()
            
            if tracked_file:
                # Update existing record if hash changed
                if tracked_file.hash != file_hash:
                    tracked_file.hash = file_hash
                    tracked_file.last_analyzed = datetime.now(timezone.utc)
                    if insights:
                        tracked_file.insights = insights
                    session.commit()
                    return True  # File changed
                return False  # File unchanged
            else:
                # Create new tracking record
                tracked_file = FileTracked(
                    project_id=project.id,
                    path=file_path,
                    hash=file_hash,
                    insights=insights
                )
                session.add(tracked_file)
                session.commit()
                return True  # New file
                
        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Error updating file tracking: {e}[/red]")
            return False
        finally:
            self.db.close_session(session)
    
    def get_changed_files(self, project: Project) -> List[Dict[str, any]]:
        """Get list of files that have changed since last scan"""
        session = self.db.get_session()
        try:
            tracked_files = session.query(FileTracked).filter_by(
                project_id=project.id
            ).all()
            
            changed_files = []
            current_files = set(self.scan_project_files(project))
            tracked_paths = {tf.path for tf in tracked_files}
            
            # Check for new files
            new_files = current_files - tracked_paths
            for file_path in new_files:
                changed_files.append({
                    'path': file_path,
                    'status': 'new',
                    'hash': self.get_file_hash(os.path.join(project.path, file_path))
                })
            
            # Check for modified files
            for tracked_file in tracked_files:
                if tracked_file.path in current_files:
                    full_path = os.path.join(project.path, tracked_file.path)
                    current_hash = self.get_file_hash(full_path)
                    
                    if current_hash and current_hash != tracked_file.hash:
                        changed_files.append({
                            'path': tracked_file.path,
                            'status': 'modified',
                            'old_hash': tracked_file.hash,
                            'new_hash': current_hash
                        })
                else:
                    # File was deleted
                    changed_files.append({
                        'path': tracked_file.path,
                        'status': 'deleted',
                        'hash': tracked_file.hash
                    })
            
            return changed_files
            
        finally:
            self.db.close_session(session)
    
    def sync_project_files(self, project: Project) -> Dict[str, int]:
        """Synchronize all project files with tracking database"""
        session = self.db.get_session()
        try:
            current_files = self.scan_project_files(project)
            stats = {'new': 0, 'updated': 0, 'unchanged': 0, 'deleted': 0}
            
            # Track current files
            for file_path in current_files:
                full_path = os.path.join(project.path, file_path)
                file_hash = self.get_file_hash(full_path)
                
                if not file_hash:
                    continue
                
                tracked_file = session.query(FileTracked).filter_by(
                    project_id=project.id,
                    path=file_path
                ).first()
                
                if tracked_file:
                    if tracked_file.hash != file_hash:
                        tracked_file.hash = file_hash
                        tracked_file.last_analyzed = datetime.now(timezone.utc)
                        stats['updated'] += 1
                    else:
                        stats['unchanged'] += 1
                else:
                    new_tracked_file = FileTracked(
                        project_id=project.id,
                        path=file_path,
                        hash=file_hash
                    )
                    session.add(new_tracked_file)
                    stats['new'] += 1
            
            # Remove tracking for deleted files
            tracked_files = session.query(FileTracked).filter_by(
                project_id=project.id
            ).all()
            
            current_file_set = set(current_files)
            for tracked_file in tracked_files:
                if tracked_file.path not in current_file_set:
                    session.delete(tracked_file)
                    stats['deleted'] += 1
            
            session.commit()
            return stats
            
        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Error syncing project files: {e}[/red]")
            return {'error': 1}
        finally:
            self.db.close_session(session)
    
    def display_file_changes(self, project: Project) -> None:
        """Display file changes in a nice table"""
        changed_files = self.get_changed_files(project)
        
        if not changed_files:
            self.console.print("[green]No file changes detected[/green]")
            return
        
        table = Table(title="File Changes Detected")
        table.add_column("File", style="cyan", width=50)
        table.add_column("Status", style="green", width=12)
        table.add_column("Hash", style="dim", width=16)
        
        for file_info in changed_files:
            status_color = {
                'new': 'green',
                'modified': 'yellow',
                'deleted': 'red'
            }.get(file_info['status'], 'white')
            
            status = f"[{status_color}]{file_info['status'].upper()}[/{status_color}]"
            hash_display = file_info.get('new_hash', file_info.get('hash', ''))[:12] + '...'
            
            table.add_row(file_info['path'], status, hash_display)
        
        self.console.print(table)
    
    def get_file_insights(self, project: Project, file_path: str) -> Optional[str]:
        """Get cached insights for a specific file"""
        session = self.db.get_session()
        try:
            tracked_file = session.query(FileTracked).filter_by(
                project_id=project.id,
                path=file_path
            ).first()
            
            return tracked_file.insights if tracked_file else None
            
        finally:
            self.db.close_session(session)
    
    def update_file_insights(self, project: Project, file_path: str, insights: str) -> bool:
        """Update insights for a specific file"""
        session = self.db.get_session()
        try:
            tracked_file = session.query(FileTracked).filter_by(
                project_id=project.id,
                path=file_path
            ).first()
            
            if tracked_file:
                tracked_file.insights = insights
                tracked_file.last_analyzed = datetime.now(timezone.utc)
                session.commit()
                return True
            
            return False
            
        except Exception as e:
            session.rollback()
            self.console.print(f"[red]Error updating file insights: {e}[/red]")
            return False
        finally:
            self.db.close_session(session)