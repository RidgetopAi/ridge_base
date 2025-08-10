import os
import hashlib
from pathlib import Path

def file_exists(filepath):
    """Check if file exists and is readable"""
    path = Path(filepath)
    return path.exists() and path.is_file()

def folder_exists(folderpath):
    """Check if folder exists and is readable"""
    path = Path(folderpath)
    return path.exists() and path.is_dir()

def read_file_content(filepath):
    """Read file content with error handling"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except UnicodeDecodeError:
        # Handle binary files gracefully
        return f"[Error reading {filepath}]"
    except Exception as e:
        return f"[Error reading {filepath}: {str(e)}]"

def get_file_hash(filepath):
    """Generate has for file change detection"""
    try:
        content = read_file_content(filepath)
        return hashlib.md5(content.encode()).hexdigest()
    except Exception:
        return None

def scan_folder(folderpath, extensions=None):
    """Scan folder for files, optionally filter by extensions"""
    path = Path(folderpath)
    files = []

    # Default to common code file extensions
    if extensions is None:
        extensions = ['.py', '.js', '.ts', '.json', '.md', '.txt', '.yml', '.yaml']
    
    for file_path in path.rglob('*'):
        if file_path.is_file() and file_path.suffix in extensions:
            files.append(str(file_path))
    
    return files