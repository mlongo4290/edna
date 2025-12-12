"""Device backup engine"""
from traceback import format_exc
from typing import Optional
from logging import getLogger
from netmiko import ConnectHandler
from netmiko.exceptions import NetMikoTimeoutException, NetMikoAuthenticationException

from classes.device import Device

logger = getLogger(__name__)

class BackupEngine:
    """Core backup engine"""
    
    def backup_device(self, device: Device, model) -> Optional[str]:
        """
        Backup a single device configuration
        
        Args:
            device: Device object
            model: Device model with commands
            
        Returns:
            Configuration string or None on failure
        """
        connection_params = {
            'device_type': device.device_type,
            'host': device.host,
            'username': device.username,
            'password': device.password,
            'timeout': 60,  # Connection timeout
            'session_timeout': 60,  # Session timeout
            'read_timeout_override': 90,  # Command execution timeout
        }
        
        try:
            logger.info(f"Connecting to {device.name} ({device.host})...")
            
            with ConnectHandler(**connection_params) as conn:
                logger.info(f"Connected to {device.name}")
                
                # Get commands from model
                commands = model.get_commands()
                
                config_output = []
                for cmd in commands:
                    logger.debug(f"Executing: {cmd}")
                    output = conn.send_command(cmd, read_timeout=90)
                    config_output.append(f"! Command: {cmd}\n{output}\n")
                
                # Post-process configuration
                config = model.process_config("\n".join(config_output))
                
                logger.info(f"Successfully backed up {device.name}")
                return config
                
        except NetMikoTimeoutException as e:
            logger.error(f"Timeout connecting to {device.name}: {str(e)}")
            logger.debug(format_exc())
            
        except NetMikoAuthenticationException as e:
            logger.error(f"Authentication failed for {device.name}: {str(e)}")
            logger.debug(format_exc())
            
        except Exception as e:
            logger.error(f"Error backing up {device.name}:\n{format_exc()}")
        
        return None
