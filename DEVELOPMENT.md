# Module Development Guide

## Modular Architecture

EDNA uses a plugin system that allows easy extension of functionality without modifying the core application.

## Module Types

### 1. Input Modules

Input modules are responsible for providing the list of devices to backup.

#### Creating a New Input Module

1. Create a file in `backend/modules/input/` (e.g., `csv.py`)
2. Implement the class inheriting from `InputModule`
3. Implement the `get_devices()` method that returns a list of `Device` objects

Example:

```python
from classes.input_module import InputModule
from classes.device import Device
from typing import List
import csv

class Csv(InputModule):
    """CSV file input module"""
    
    def __init__(self, config):
        super().__init__(config)
        self.csv_file = config.get('file', 'devices.csv')
    
    def get_devices(self) -> List[Device]:
        """Load devices from CSV file"""
        devices = []
        
        with open(self.csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                device = Device(
                    name=row['name'],
                    host=row['ip'],
                    device_type=row['type'],
                    username=row.get('username', 'admin'),
                    password=row.get('password', '')
                )
                devices.append(device)
        
        return devices
```

#### Configuration

In the `config.yaml` file:

```yaml
input:
  - type: csv
    config:
      file: /path/to/devices.csv
```

### 2. Output Modules

Output modules handle where and how to save backups.

#### Creating a New Output Module

1. Create a file in `backend/modules/output/` (e.g., `git.py`)
2. Implement the class inheriting from `OutputModule`
3. Implement the `save_backup(device, config)` method

Example:

```python
from classes.output_module import OutputModule
import subprocess
from pathlib import Path
from datetime import datetime

class Git(OutputModule):
    """Git repository output module"""
    
    def __init__(self, config):
        super().__init__(config)
        self.repo_path = Path(config.get('path'))
        self.auto_commit = config.get('auto_commit', True)
        
        # Initialize repo if needed
        if not (self.repo_path / '.git').exists():
            subprocess.run(['git', 'init'], cwd=self.repo_path)
    
    def save_backup(self, device, config: str):
        """Save backup to git repository"""
        # Create device directory
        device_dir = self.repo_path / device.name
        device_dir.mkdir(parents=True, exist_ok=True)
        
        # Write config file
        config_file = device_dir / f"{device.name}.cfg"
        with open(config_file, 'w') as f:
            f.write(config)
        
        if self.auto_commit:
            # Git add and commit
            subprocess.run(['git', 'add', '.'], cwd=self.repo_path)
            commit_msg = f"Backup {device.name} - {datetime.now().isoformat()}"
            subprocess.run(['git', 'commit', '-m', commit_msg], cwd=self.repo_path)
```

#### Configuration

```yaml
output:
  - type: git
    config:
      path: /var/backups/network-git
      auto_commit: true
```

### 3. Device Models

Models define how to interact with specific device types.

#### Creating a New Device Model

1. Create a file in `backend/modules/models/` (e.g., `vendor.py`)
2. Implement the class with capitalized name matching device_type
3. Implement `get_commands()` and `process_config()` methods

Example:

```python
class MikrotikRouteros:
    """MikroTik RouterOS model"""
    
    @staticmethod
    def get_commands():
        """Return commands for MikroTik"""
        return [
            '/system resource print',
            '/export compact',
        ]
    
    @staticmethod
    def process_config(config: str) -> str:
        """Return configuration as-is without modifications"""
        return config
```

**Important:** The class name must match the Netmiko device_type capitalized:
- `mikrotik_routeros` → `MikrotikRouteros`
- `cisco_ios` → `CiscoIos`
- `fortinet` → `Fortinet`

## Netmiko Device Types

Supported device types:

### Cisco
- `cisco_ios`
- `cisco_xe`  
- `cisco_xr`
- `cisco_nxos`
- `cisco_asa`
- `cisco_s300`

### Juniper
- `juniper_junos`

### Arista
- `arista_eos`

### HP/HPE
- `hp_procurve`
- `hp_comware`

### Dell
- `dell_os10`
- `dell_force10`

### Other Vendors
- `fortinet` / `fortios`
- `paloalto_panos`
- `mikrotik_routeros`
- `linux`
- `vyos`
- `extreme`

## Testing Modules

### Test Input Module

```python
from modules.input.your_module import YourModule

config = {'param1': 'value1'}
module = YourModule(config)
devices = module.get_devices()

for device in devices:
    print(f"Device: {device.name} @ {device.host}")
```

### Test Output Module

```python
from modules.output.your_module import YourModule
from classes.device import Device

config = {'path': '/tmp/test'}
module = YourModule(config)

device = Device(name='test-device', host='192.168.1.1', device_type='cisco_ios', 
                username='admin', password='pass')
module.save_backup(device, 'test configuration')
```

### Test Device Model

```python
from modules.models.your_model import YourModel

model = YourModel()
commands = model.get_commands()
print(f"Commands: {commands}")

sample_config = "your sample config..."
processed = model.process_config(sample_config)
print(processed)
```

## Best Practices

1. **Error Handling**: Always handle exceptions and log errors
2. **Logging**: Use `from logging import getLogger; logger = getLogger(__name__)`
3. **Configuration**: Validate configuration parameters in `__init__`
4. **Documentation**: Document your code with docstrings
5. **Testing**: Test the module before using in production
6. **No Modifications**: Never modify device configurations in `process_config()` - return as-is

## Contributing

If you develop a useful module, consider contributing it to the project!
