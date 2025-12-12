"""Filesystem output module with rotation"""
from logging import getLogger
from pathlib import Path
from datetime import datetime
from typing import List
from core.plugin_manager import OutputModule
from classes.backup import Backup

logger = getLogger(__name__)


class Filesystem(OutputModule):
    """Filesystem output module with backup rotation"""
    
    def __init__(self, config):
        super().__init__(config)
        self.path = Path(config.get('path', '/var/backups/network'))
        self.retention = config.get('retention', 10)
        self.format = config.get('format', 'text')  # text or yaml
        self.organize_by = config.get('organize_by', 'device')  # device or date
        
        # Create base directory
        self.path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Filesystem output initialized at {self.path}")
    
    def save_backup(self, device, config: str):
        """
        Save device backup to filesystem with rotation
        
        Args:
            device: Device object
            config: Configuration string to save
        """
        try:
            # Determine directory structure
            if self.organize_by == 'device':
                device_dir = self.path / device.name
            else:  # by date
                date_str = datetime.now().strftime('%Y-%m-%d')
                device_dir = self.path / date_str / device.name
            
            device_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{device.name}_{timestamp}.cfg"
            backup_file = device_dir / filename
            
            # Write configuration
            with open(backup_file, 'w') as f:
                f.write(config)
            
            logger.info(f"Saved backup to {backup_file}")
            
            # Create/update symlink to latest
            latest_link = device_dir / f"{device.name}_latest.cfg"
            if latest_link.exists() or latest_link.is_symlink():
                latest_link.unlink()
            latest_link.symlink_to(filename)
            
            # Perform rotation
            self._rotate_backups(device_dir, device.name)
            
        except Exception as e:
            logger.error(f"Error saving backup for {device.name}: {e}")
            raise
    
    def _rotate_backups(self, device_dir: Path, device_name: str):
        """
        Rotate old backups, keeping only the most recent N files
        
        Args:
            device_dir: Directory containing device backups
            device_name: Name of the device
        """
        try:
            # Get all backup files (excluding symlinks)
            backup_files = [
                f for f in device_dir.glob(f"{device_name}_*.cfg")
                if not f.is_symlink() and f.name != f"{device_name}_latest.cfg"
            ]
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Remove old backups
            if len(backup_files) > self.retention:
                files_to_remove = backup_files[self.retention:]
                for old_file in files_to_remove:
                    logger.info(f"Removing old backup: {old_file.name}")
                    old_file.unlink()
                
                logger.info(f"Rotation complete. Kept {self.retention} backups for {device_name}")
            
        except Exception as e:
            logger.error(f"Error during backup rotation: {e}")
    
    def get_device_backups(self, device_name: str) -> List[Backup]:
        """
        Get list of backups for a device
        
        Args:
            device_name: Name of the device
            
        Returns:
            List of backup info dictionaries
        """
        backups = []
        
        try:
            if self.organize_by == 'device':
                device_dir = self.path / device_name
            else:
                # Search across all date directories
                device_dir = self.path
            
            if not device_dir.exists():
                return backups
            
            # Find all backup files
            if self.organize_by == 'device':
                backup_files = [
                    f for f in device_dir.glob(f"{device_name}_*.cfg")
                    if not f.is_symlink()
                ]
            else:
                backup_files = [
                    f for f in device_dir.rglob(f"*/{device_name}/{device_name}_*.cfg")
                    if not f.is_symlink()
                ]
            
            # Sort by modification time (newest first)
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            now = datetime.now()
            for backup_file in backup_files:
                stat = backup_file.stat()
                creation_time = datetime.fromtimestamp(stat.st_mtime)
                elapsed = now - creation_time
                
                # Format elapsed time
                if elapsed.days > 0:
                    elapsed_str = f"{elapsed.days}d ago"
                elif elapsed.seconds >= 3600:
                    hours = elapsed.seconds // 3600
                    elapsed_str = f"{hours}h ago"
                elif elapsed.seconds >= 60:
                    minutes = elapsed.seconds // 60
                    elapsed_str = f"{minutes}m ago"
                else:
                    elapsed_str = f"{elapsed.seconds}s ago"
                
                backups.append(Backup(
                    id=str(backup_file.name),
                    creation_time=creation_time,
                    elapsed_time=elapsed_str
                ))
            
        except Exception as e:
            logger.error(f"Error getting backups for {device_name}: {e}")
        
        return backups
    
    def get_device_last_backup_content(self, device_name: str) -> str:
        """
        Get content of the last backup for a device
        
        Args:
            device_name: Name of the device
        Returns:
            Backup content as string
        """        
        try:
            return self.get_backup_content(device_name, Backup(id=f"{device_name}_latest.cfg"))
        
        except Exception as e:
            logger.error(f"Error getting last backup for {device_name}: {e}")
            raise

    def get_backup_content(self, device_name: str, backup: Backup) -> str:
        """
        Get content of a backup file
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Backup content
        """
        try:
            if self.organize_by == 'device':
                device_dir = self.path / device_name
            else:
                # Search across all date directories
                device_dir = self.path
            
            # Locate the backup file
            if self.organize_by == 'device':
                backup_file = device_dir / backup.id
            else:
                # Search in all date subdirectories
                backup_file = next(device_dir.rglob(f"*/{device_name}/{backup.id}"), None)
            
            if not backup_file or not backup_file.exists():
                raise FileNotFoundError(f"Backup file {backup.id} not found for {device_name}")
            
            with open(backup_file, 'r') as f:
                content = f.read()
            
            return content
        
        except Exception as e:
            logger.error(f"Error getting backup content for {device_name}, {backup.id}: {e}")
            raise