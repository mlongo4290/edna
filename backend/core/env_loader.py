"""Load environment variables from .env file"""
from pathlib import Path
import os


def load_env_file(env_path: Path = None):
    """
    Load environment variables from .env file
    
    Args:
        env_path: Path to .env file. If None, looks for .env in current directory
    """
    if env_path is None:
        env_path = Path(__file__).parent.parent / '.env'
    
    if not env_path.exists():
        return
    
    with open(env_path, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            
            # Parse KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()
                # Remove quotes if present
                if value.startswith('"') and value.endswith('"'):
                    value = value[1:-1]
                elif value.startswith("'") and value.endswith("'"):
                    value = value[1:-1]
                
                # Set environment variable if not already set
                if key not in os.environ:
                    os.environ[key] = value
