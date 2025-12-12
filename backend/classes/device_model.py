from abc import ABC, abstractmethod

class DeviceModel(ABC):
    """Base class for device models"""
    
    @abstractmethod
    def get_commands(self) -> list:
        """Return list of commands to execute"""
        pass

    @abstractmethod
    def process_config(self, config: str) -> str:
        """Post-process configuration"""
        return config