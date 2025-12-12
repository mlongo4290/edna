"""Backup scheduler using APScheduler"""
from logging import getLogger
from datetime import datetime
from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.cron import CronTrigger

from core.config import Config
from core.database import DeviceDatabase
from core.engine import BackupEngine
from core.plugin_manager import PluginManager

logger = getLogger(__name__)


class BackupScheduler:
    """Manages scheduled backups using APScheduler"""
    
    def __init__(self, config: Config):
        self.config = config
        self.engine = BackupEngine()
        self.plugin_manager = PluginManager()
        self.database = DeviceDatabase()
        self.scheduler = BackgroundScheduler()
        self.last_run: Optional[datetime] = None
        
        # Setup schedule if enabled
        if config.scheduler.enabled:
            # Determine trigger type
            trigger = None
            schedule_desc = ""
            
            if config.scheduler.cron:
                # Use cron expression
                trigger = CronTrigger.from_crontab(config.scheduler.cron)
                schedule_desc = f"cron '{config.scheduler.cron}'"
            else:
                logger.warning("Scheduler enabled but no cron configured")
                return
            
            self.scheduler.add_job(
                func=self.run_backup,
                trigger=trigger,
                id='backup_devices',
                name='Backup all devices',
                replace_existing=True
            )
            
            # Start scheduler
            self.scheduler.start()
            logger.info(f"Scheduler started with {schedule_desc}")
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def stop(self):
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")
    
    def sync_devices(self):
        """Sync devices from all input sources to database"""
        logger.info("Syncing devices from input sources...")
        self.last_run = datetime.now()
        
        try:
            all_devices = []
            
            # Load devices from all input sources
            for source in self.config.input:
                try:
                    input_module = self.plugin_manager.load_input_module(
                        source['type'],
                        source['config']
                    )
                    devices = input_module.get_devices()
                    all_devices.extend(devices)
                    logger.info(f"Loaded {len(devices)} devices from {source['type']}")
                    
                except Exception as e:
                    logger.error(f"Failed to load devices from {source['type']}: {e}")
            
            # Update database
            if all_devices:
                self.database.upsert_devices(all_devices)
                logger.info(f"Synced {len(all_devices)} devices to database")
            
            # Remove stale devices (not seen in 24h)
            self.database.remove_stale_devices(hours=24)
            
        except Exception as e:
            logger.error(f"Device sync failed: {e}")
    
    def _backup_single_device(self, device, output_modules):
        """Backup a single device"""
        try:
            # Get device model
            model = self.plugin_manager.get_device_model(device.device_type)
            
            # Backup device
            config = self.engine.backup_device(device, model)
            
            if config:
                # Save to all output destinations
                for output_module in output_modules:
                    try:
                        output_module.save_backup(device, config)
                    except Exception as e:
                        logger.error(f"Failed to save backup for {device.name} to {type(output_module).__name__}: {e}")
                
                logger.info(f"Backup successful for {device.name}")
                return device.name  # Return device name on success
            else:
                logger.warning(f"No config retrieved for {device.name}")
                return None
                
        except Exception as e:
            logger.error(f"Backup failed for {device.name}: {e}")
            return None
    
    def run_backup(self):
        """Execute backup of all devices from input sources"""
        logger.info("Starting backup run...")
        self.last_run = datetime.now()
        
        try:
            # Load devices from all input sources
            all_devices = []
            for source in self.config.input:
                try:
                    input_module = self.plugin_manager.load_input_module(
                        source['type'],
                        source['config']
                    )
                    devices = input_module.get_devices()
                    all_devices.extend(devices)
                    logger.info(f"Loaded {len(devices)} devices from {source['type']}")
                    
                except Exception as e:
                    logger.error(f"Failed to load devices from {source['type']}: {e}")
            
            if not all_devices:
                logger.warning("No devices loaded from input sources")
                return {'success': 0, 'failed': 0, 'total': 0}
            
            # Load output modules
            output_modules = []
            for dest in self.config.output:
                try:
                    output_module = self.plugin_manager.load_output_module(
                        dest['type'],
                        dest['config']
                    )
                    output_modules.append(output_module)
                except Exception as e:
                    logger.error(f"Failed to load output module {dest['type']}: {e}")
            
            if not output_modules:
                logger.error("No output modules loaded")
                return {'success': 0, 'failed': 0, 'total': len(all_devices)}
            
            # Backup devices in parallel
            results = {'success': 0, 'failed': 0, 'total': len(all_devices)}
            max_workers = self.config.scheduler.max_workers
            successful_devices = []
            
            # Execute backups in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(self._backup_single_device, device, output_modules): device for device in all_devices}
                
                for future in as_completed(futures):
                    device_name = future.result()
                    if device_name:
                        results['success'] += 1
                        successful_devices.append(device_name)
                    else:
                        results['failed'] += 1
            
            # Update database with devices and their backup timestamps
            self.database.upsert_devices(all_devices)
            logger.info(f"Updated {len(all_devices)} devices in database")
            
            logger.info(f"Backup run completed: {results}")
            return results
            
        except Exception as e:
            logger.error(f"Backup run failed: {e}")
            return {'success': 0, 'failed': 0, 'total': 0}
    
    def get_status(self):
        """Get scheduler status"""
        next_run = None
        if self.scheduler.running:
            job = self.scheduler.get_job('backup_devices')
            if job and job.next_run_time:
                next_run = job.next_run_time.isoformat()
        
        return {
            'is_running': self.scheduler.running,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': next_run,
            'cron': self.config.scheduler.cron
        }
