from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime

class Backup(BaseModel):
    """Represents a network device backup"""
    
    id: str
    creation_time: datetime = None
    elapsed_time: str = None