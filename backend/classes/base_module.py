from typing import Dict, Any

class BaseModule:
    """Base class for all modules"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config