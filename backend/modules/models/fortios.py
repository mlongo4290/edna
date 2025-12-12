"""Fortinet FortiOS device model"""
from core.plugin_manager import DeviceModel


class Fortios(DeviceModel):
    """Fortinet FortiOS device model"""
    
    def get_commands(self):
        """Return commands for FortiOS devices"""
        return [
            'get system status',
            'show | grep .',  # Avoids --More-- prompt
        ]
    
    def process_config(self, config: str) -> str:
        """Return configuration as-is without modifications"""
        return config


# Aliases
class Fortigate(Fortios):
    """Alias for FortiOS"""
    pass

class Fortinet(Fortios):
    """Alias for FortiOS"""
    pass
