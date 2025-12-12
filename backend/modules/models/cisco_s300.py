"""Cisco Small Business (CBS, SG series) device model"""
from core.plugin_manager import DeviceModel

class CiscoS300(DeviceModel):
    """Cisco Small Business switches (CBS350, SG300, etc.)"""
    
    def get_commands(self) -> list:
        """Return commands to get device configuration"""
        return [
            'show running-config'
        ]
    
    def process_config(self, config: str) -> str:
        return super().process_config(config)
