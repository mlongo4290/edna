#!/usr/bin/env python3
"""
EDNA - nEtwork Device coNfiguration bAckup
Main entry point
"""
from logging import getLogger, basicConfig
from pathlib import Path
import uvicorn

# Load environment variables first
from core.env_loader import load_env_file
load_env_file()

from core.config import Config
from core.scheduler import BackupScheduler
from core.database import DeviceDatabase
from core.init_db import init_admin_user
from api.server import create_app


def main():
    """Main application entry point"""
    # Load configuration first
    config_path = Path(__file__).parent / "config" / "config.yaml"
    config = Config.load(config_path)
    
    # Setup logging with config level
    basicConfig(
        level=config.logging.level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = getLogger(__name__)
    
    logger.info("Starting EDNA...")
    
    logger.info(f"Loaded configuration from {config_path}")
    
    # Initialize database and create admin user if needed
    db = DeviceDatabase()
    init_admin_user(db)
    
    # Create scheduler
    scheduler = BackupScheduler(config)
    
    # Start FastAPI server
    app = create_app(config, scheduler)
    
    uvicorn.run(
        app,
        host=config.api.get('host', '0.0.0.0'),
        port=config.api.get('port', 8000),
        log_level=config.logging.level.lower()
    )


if __name__ == "__main__":
    main()
