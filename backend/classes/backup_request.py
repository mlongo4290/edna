from pydantic import BaseModel
from typing import Optional

class BackupRequest(BaseModel):
    """Request to trigger backup"""
    device_name: Optional[str] = None