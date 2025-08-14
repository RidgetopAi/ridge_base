import os
import shutil
import datetime
from pathlib import Path
import hashlib

class BackupManager:
    """Manages file backups before editing operations"""

    def __init__(self, project_root=None):
        self.project_root = project_root or os.getcwd()
        self.backup_dir = os.path.join(self.project_root, '.ridge_backups')
        self._ensure_backup_dir()
    
    def _ensure_backup_dir(self):
        """Create backup directory if it doesn't exist"""
        os.makedirs(self.backup_dir, exist_ok=True)

        # Create .gitignore for backup directory
        gitignore_path = os.path.join(self.backup_dir, '.gitignore')
        if not os.path.exists(gitignore_path):
            with open(gitignore_path, 'w') as f:
                f.write("@ Ridge Base backups - safe to delete\n*\n")
        
    def create_backups(self, file_path):
        """Create backup of file before editing

        Returns:
            str: Path to backup file
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Cannot backup non-existent file: {file_path}")
        
        # Generate backup filename with timestamp and hash
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_hash = self._get_file_hash(file_path)[:8]
        filename = os.path.basename(file_path)
        backup_name = f"{timestamp}_{file_hash}_{filename}"
        backup_path = os.path.join(self.backup_dir, backup_name)

        # Copy file to backup location
        shutil.copy2(file_path, backup_path)

        return backup_path
    
    def _get_file_hash(self, file_path):
        """Get SHA-256 has of file content"""
        with open(file_path,'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def list_backups(self, file_path=None):
        """List backups, optionally filtered by original file"""
        backups = []
        if not os.path.exists(self.backup_dir):
            return backups
    
        for backup_file in os.listdir(self.backup_dir):
            if backup_file.startswith('.'): # Skip .gitignore
                continue
                
            backup_path = os.path.join(self.backup_dir, backup_file)
            if os.path.isfile(backup_path):
                # Parse backup filename: timestamp_hash_originalname
                parts = backup_file.split('_', 2)
                if len(parts) >= 3:
                    timestamp_str = parts[0]
                    original_name = parts[2]

                    # Filter by file if specified
                    if file_path and os.path.basename(file_path) != original_name:
                        continue

                    backups.append({
                        'backup_path': backup_path,
                        'original_name': original_name,
                        'timestamp': timestamp_str,
                        'size': os.path.getsize(backup_path)
                    })

        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x['timestamp'], reverse=True)
        return backups
    
    def cleanup_old_backups(self, days_to_keep=7):
        """Remove backups older than specified days

        Args:
            days_to_keep (int): Number of days to keep backups
        
        Returns:
            init: Number of backups cleaned up
        """
        if not os.path.exists(self.backup_dir):
            return 0
        
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_to_keep)
        cleaned_count = 0

        for backup_file in os.listdir(self.backup_dir):
            if backup_file.startswith('.'): # Skip .gitignore
                continue

            backup_path = os.path.join(self.backup_dir, backup_file)
            if os.path.isfile(backup_path):
                # Get file modification time
                mod_time = datetime.datetime.fromtimestamp(os.path.getatime(backup_path))

                if mod_time < cutoff_date:
                    os.remove(backup_path)
                    cleaned_count +=1

        return cleaned_count

        
