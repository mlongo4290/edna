from typing import List
from classes.base_module import BaseModule
from classes.backup import Backup
from abc import ABC, abstractmethod

class OutputModule(ABC, BaseModule):
    """Base class for output modules"""
    
    @abstractmethod
    def save_backup(self, device, config: str):
        """
        Save device backup to output destination
        
        Args:
            device: Device object
            config: Configuration string to save
        """
        pass

    @abstractmethod
    def get_device_backups(self, device_name: str) -> List[Backup]:
        """
        Get list of backups for a device
        
        Args:
            device_name: Name of the device
        Returns:
            List of backup info dictionaries
        """
        pass

    @abstractmethod
    def get_device_last_backup_content(self, device_name: str) -> str:
        """
        Get the content of the last backup for a device
        
        Args:
            device_name: Name of the device
        Returns:
            Backup content as string
        """
        pass

    @abstractmethod
    def get_backup_content(self, device_name: str, backup: Backup) -> str:
        """
        Get the content of a specific backup given its path
        
        Args:
            backup_path: Path to the backup file
        Returns:
            Backup content as string
        """
        pass