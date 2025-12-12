"""Cisco IOS device model"""
from core.plugin_manager import DeviceModel


class CiscoIos(DeviceModel):
    """Cisco IOS device model"""
    
    def get_commands(self):
        """Return commands for Cisco IOS devices"""
        return [
            'show version',
            'show running-config',
        ]
    
    def process_config(self, config: str) -> str:
        return super().process_config(config)


# Aliases for different IOS variants
class CiscoXe(CiscoIos):
    """Cisco IOS-XE model"""
    pass