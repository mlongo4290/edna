"""FastAPI server"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import List
from asyncio import create_task, to_thread
from pydantic import BaseModel

from core.config import Config
from core.database import DeviceDatabase
from core.scheduler import BackupScheduler
from core.plugin_manager import PluginManager
from core.auth import AuthService, TokenData
from classes.device import Device
from classes.backup_request import BackupRequest

from logging import getLogger

from classes.backup import Backup

logger = getLogger(__name__)

# Global instances
plugin_manager = PluginManager()
device_db = DeviceDatabase()
security = HTTPBearer()


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


def create_app(config: Config, scheduler: BackupScheduler) -> FastAPI:
    """Create FastAPI application"""
    
    app = FastAPI(
        title="EDNA API",
        description="nEtwork Device coNfiguration bAckup",
        version="1.0.0"
    )
    
    # Initialize auth service with database
    auth_service = AuthService(config.get('auth', {}), device_db)
    
    # Configure CORS
    cors_origins = config.api.get('cors_origins', ['http://localhost:4200'])
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Dependency: get current user from JWT
    async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
        token = credentials.credentials
        token_data = auth_service.verify_token(token)
        if token_data is None:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        return token_data
    
    @app.post("/api/auth/login", response_model=LoginResponse)
    async def login(request: LoginRequest):
        """Login with username and password"""
        token_data = auth_service.authenticate(request.username, request.password)
        if token_data is None:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = auth_service.create_access_token(token_data.username, token_data.role)
        return LoginResponse(
            access_token=access_token,
            username=token_data.username,
            role=token_data.role
        )
    
    @app.get("/api/auth/me")
    async def get_current(current_user: TokenData = Depends(get_current_user)):
        """Get current authenticated user"""
        return {
            "username": current_user.username,
            "role": current_user.role
        }
    
    @app.post("/api/auth/logout")
    async def logout(current_user: TokenData = Depends(get_current_user)):
        """Logout endpoint (client clears token from localStorage)"""
        return {"message": "Logged out successfully"}
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "name": "EDNA API",
            "version": "1.0.0",
            "status": "running"
        }
    
    @app.get("/api/status")
    async def get_status():
        """Get system status"""
        input_types = [s['type'] for s in config.input]
        output_types = [d['type'] for d in config.output]
        
        return {
            "scheduler": scheduler.get_status(),
            "config": {
                "input": ', '.join(input_types),
                "output": ', '.join(output_types),
                "retention": config.output[0]['config'].get('retention', 10) if config.output else 10
            }
        }
    
    @app.post("/api/backup/run")
    async def trigger_backup(request: BackupRequest = None):
        """Trigger a backup run"""
        try:
            logger.info("Manual backup triggered via API")
            create_task(to_thread(scheduler.run_backup))
            return {"status": "success", "message": "Backup started in background"}
        except Exception as e:
            logger.error(f"Failed to start backup: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/devices")
    async def get_devices() -> List[Device]:
        """Get list of devices from database"""
        try:
            # Get devices from database
            devices = device_db.get_all_devices()
            device_list = []
            
            # Get output module to check for backups
            output_module = None
            if config.output:
                try:
                    dest = config.output[0]
                    output_module = plugin_manager.load_output_module(
                        dest['type'],
                        dest['config']
                    )
                except Exception as e:
                    logger.error(f"Failed to load output module: {e}")
            
            for d in devices:
                # Get last backup date from output module
                last_backup = None
                if output_module:
                    try:
                        backups = output_module.get_device_backups(d.name)
                        if backups:
                            # Get most recent backup
                            last_backup = max(b['timestamp'] for b in backups)
                    except:
                        pass
                
                device_list.append(Device(
                    name=d.name,
                    host=d.host,
                    device_type=d.device_type,
                    last_backup=d.last_backup if d.last_backup else last_backup
                ))
            
            return device_list
        except Exception as e:
            logger.error(f"Error getting devices: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/devices/{device_name}/last_backup")
    async def get_device_last_backup_content(device_name: str):
        """Get last backup date for a device"""
        try:
            # Get device from database
            device = device_db.get_device(device_name)
            if not device:
                raise HTTPException(status_code=404, detail="Device not found")
            
            # Get output module to check for backups
            if not config.output:
                raise HTTPException(status_code=500, detail="No output configured")
            
            output_module = plugin_manager.load_output_module(
                config.output[0]['type'],
                config.output[0]['config']
            )
            
            content = output_module.get_device_last_backup_content(device_name)
            return {"content": content}
        except Exception as e:
            logger.error(f"Error getting last backup for {device_name}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/api/devices/{device_name}/backups")
    async def get_device_backups(device_name: str):
        """Get list of backups for a device"""
        try:
            # Load first output module
            if not config.output:
                raise HTTPException(status_code=500, detail="No output configured")
            
            output_module = plugin_manager.load_output_module(
                config.output[0]['type'],
                config.output[0]['config']
            )
            
            backups = output_module.get_device_backups(device_name)
            return backups
        except Exception as e:
            logger.error(f"Error getting backups: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/devices/{device_name}/backups/{id}")
    async def get_backup_content(device_name: str, id: str):
        """Get content of a specific backup"""
        try:
            # Load first output module
            if not config.output:
                raise HTTPException(status_code=500, detail="No output configured")
            
            output_module = plugin_manager.load_output_module(
                config.output[0]['type'],
                config.output[0]['config']
            )
            
            content = output_module.get_backup_content(device_name, Backup(id=id))
            return {"content": content}
        except Exception as e:
            logger.error(f"Error getting backup content: {e}")
            raise HTTPException(status_code=404, detail="Backup not found")
    
    @app.post("/api/scheduler/start")
    async def start_scheduler():
        """Start the backup scheduler"""
        scheduler.start()
        return {"status": "success", "message": "Scheduler started"}
    
    @app.post("/api/scheduler/stop")
    async def stop_scheduler():
        """Stop the backup scheduler"""
        scheduler.stop()
        return {"status": "success", "message": "Scheduler stopped"}
    
    return app
