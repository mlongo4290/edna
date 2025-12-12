"""MikroTik RouterOS device model"""
from core.plugin_manager import DeviceModel


class Routeros(DeviceModel):
    """MikroTik RouterOS device model"""
    
    def get_commands(self):
        """Return commands for RouterOS devices"""
        return [
            '/system resource print',
            '/system package update print',
            '/system routerboard print',
            '/export',
        ]
    
    def process_config(self, config: str) -> str:
        return super().process_config(config)


# Alias
class Mikrotik(Routeros):
    """Alias for RouterOS"""
    pass

class MikrotikRouteros(Routeros):
    """Alias for RouterOS"""
    pass