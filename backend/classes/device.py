from pydantic import BaseModel
from typing import Optional, Dict, Any

class Device(BaseModel):
    """Represents a network device"""
    
    name: str
    host: str
    device_type: str
    username: Optional[str] = None
    password: Optional[str] = None
    last_backup: Optional[str] = None
