"""Configuration management"""
from os import getenv
from yaml import safe_load, dump
from re import sub
from pathlib import Path
from typing import Dict, Any
from classes.scheduler_config import SchedulerConfig
from classes.logging_config import LoggingConfig

def _expand_env_vars(value: Any) -> Any:
    """
    Recursively expand environment variables in configuration values.
    Supports ${VAR_NAME} and ${VAR_NAME:-default_value} syntax.
    """
    if isinstance(value, str):
        # Pattern for ${VAR_NAME} or ${VAR_NAME:-default}
        pattern = r'\$\{([^}:]+)(?::(-)?([^}]*))?\}'
        
        def replace_var(match):
            var_name = match.group(1)
            has_default = match.group(2) is not None
            default_value = match.group(3) if has_default else None
            
            env_value = getenv(var_name)
            if env_value is not None:
                return env_value
            elif has_default:
                return default_value if default_value is not None else ''
            else:
                raise ValueError(f"Environment variable '{var_name}' not found and no default provided")
        
        return sub(pattern, replace_var, value)
    
    elif isinstance(value, dict):
        return {k: _expand_env_vars(v) for k, v in value.items()}
    
    elif isinstance(value, list):
        return [_expand_env_vars(item) for item in value]
    
    return value


# Input and output are just lists of configs
InputConfig = list[Dict[str, Any]]
OutputConfig = list[Dict[str, Any]]
class Config:
    """Main configuration class"""
    
    def __init__(self, data: Dict[str, Any]):
        self.input = data.get('input', [])
        self.output = data.get('output', [])
        self.scheduler = SchedulerConfig(**data.get('scheduler', {}))
        self.api = data.get('api', {})
        self.logging = LoggingConfig(**data.get('logging', {}))
        self.raw_data = data
    
    @classmethod
    def load(cls, config_path: Path) -> 'Config':
        """Load configuration from YAML file"""
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            data = safe_load(f)
        
        # Expand environment variables
        data = _expand_env_vars(data)
        
        return cls(data)
    
    def save(self, config_path: Path):
        """Save configuration to YAML file"""
        with open(config_path, 'w') as f:
            dump(self.raw_data, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key"""
        return self.raw_data.get(key, default)
