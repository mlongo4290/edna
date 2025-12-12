from pydantic import BaseModel

class LoggingConfig(BaseModel):
    """Logging configuration"""
    level: str = "INFO"