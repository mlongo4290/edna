from pydantic import BaseModel
from typing import Optional

class SchedulerConfig(BaseModel):
    """Scheduler configuration"""
    cron: Optional[str] = None
    enabled: bool = True
    max_workers: int = 4  # parallel backup threads