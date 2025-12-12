"""Cisco NX-OS device model"""
from core.plugin_manager import DeviceModel


class CiscoNxos(DeviceModel):
    """Cisco NX-OS (Nexus) model"""
    
    def get_commands(self) -> list:
        """Commands to retrieve configuration"""
        return [
            'show version',
            'show inventory',
            'show running-config'
        ]
    
    def process_config(self, config: str) -> str:
        return super().process_config(config)
