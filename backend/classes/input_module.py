from typing import List
from classes.base_module import BaseModule
from abc import ABC, abstractmethod

class InputModule(ABC, BaseModule):
    """Base class for input modules"""
    
    @abstractmethod
    def get_devices(self) -> list:
        """Return list of Device objects"""
        pass