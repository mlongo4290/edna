from pydantic import BaseModel, Field

class APIConfig(BaseModel):
    """API configuration"""
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list = Field(default_factory=lambda: ["http://localhost:4200"])