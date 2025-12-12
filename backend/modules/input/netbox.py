"""NetBox API input module"""
from logging import getLogger
from typing import List
from pynetbox import api as pynetbox_api

from core.plugin_manager import InputModule
from core.engine import Device

logger = getLogger(__name__)


class Netbox(InputModule):
    """NetBox API input module"""
    
    def __init__(self, config):
        super().__init__(config)
        self.url = config.get('url')
        self.token = config.get('token')
        self.filter_tags = config.get('filter_tags', [])
        self.filter_status = config.get('filter_status', ['active'])
        self.custom_field_filter = config.get('custom_field_filter', {})
        self.model_custom_field = config.get('model_custom_field', 'oxidized_model')
        self.groups = config.get('groups', {})
        self.default_username = config.get('default_username', 'admin')
        self.default_password = config.get('default_password', '')
        
        if not self.url or not self.token:
            raise ValueError("NetBox URL and token are required")
        
        self.nb = pynetbox_api(self.url, token=self.token)
        logger.info(f"Connected to NetBox at {self.url}")
    
    def get_devices(self) -> List[Device]:
        """Get devices from NetBox"""
        devices = []
        
        try:
            # Query devices from NetBox
            nb_devices = self.nb.dcim.devices.filter(status=self.filter_status)
            
            for nb_device in nb_devices:
                # Filter by tags if specified
                if self.filter_tags:
                    device_tags = [tag.name for tag in nb_device.tags]
                    if not any(tag in device_tags for tag in self.filter_tags):
                        continue
                
                # Filter by custom fields if specified
                if self.custom_field_filter and nb_device.custom_fields:
                    skip_device = False
                    for cf_name, cf_expected_value in self.custom_field_filter.items():
                        cf_value = nb_device.custom_fields.get(cf_name)
                        if cf_value != cf_expected_value:
                            logger.debug(f"Device {nb_device.name} skipped: {cf_name}={cf_value} (expected {cf_expected_value})")
                            skip_device = True
                            break
                    if skip_device:
                        continue
                
                # Get primary IP
                primary_ip = None
                if nb_device.primary_ip4:
                    primary_ip = str(nb_device.primary_ip4.address).split('/')[0]
                elif nb_device.primary_ip6:
                    primary_ip = str(nb_device.primary_ip6.address).split('/')[0]
                
                if not primary_ip:
                    logger.warning(f"Device {nb_device.name} has no primary IP, skipping")
                    continue
                
                # Get device type from custom field (required)
                device_type = None
                if nb_device.custom_fields:
                    device_type = nb_device.custom_fields.get(self.model_custom_field)
                
                if not device_type:
                    logger.warning(f"Device {nb_device.name} has no {self.model_custom_field}, skipping")
                    continue
                
                # Get group for credentials (use manufacturer slug or device_type)
                group = None
                if nb_device.device_type and nb_device.device_type.manufacturer:
                    group = nb_device.device_type.manufacturer.slug
                
                # Get credentials from group or defaults
                if group and group in self.groups:
                    username = self.groups[group].get('username', self.default_username)
                    password = self.groups[group].get('password', self.default_password)
                    logger.debug(f"Device {nb_device.name} using credentials from group '{group}'")
                else:
                    username = self.default_username
                    password = self.default_password
                    logger.debug(f"Device {nb_device.name} using default credentials")
                
                # Create device object
                device = Device(
                    name=nb_device.name,
                    host=primary_ip,
                    device_type=device_type,
                    username=username,
                    password=password,
                    port=self.config.get('port', 22)
                )
                
                devices.append(device)
                logger.debug(f"Added device: {device.name} ({primary_ip}) type={device_type} group={group}")
            
            logger.info(f"Retrieved {len(devices)} devices from NetBox")
            
        except Exception as e:
            logger.error(f"Error retrieving devices from NetBox: {e}")
            raise
        
        return devices