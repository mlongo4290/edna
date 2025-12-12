# EDNA - Quick Start Guide

## Quick Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt

# Configure
cp config/config.example.yaml config/config.yaml
nano config/config.yaml

# Run
python main.py
```

### Frontend

```bash
cd frontend
npm install
npm start
```

Open browser at `http://localhost:4200`

## Minimal Configuration

Edit `backend/config/config.yaml`:

```yaml
input:
  - type: netbox
    config:
      url: https://your-netbox.com
      token: your-api-token
      default_username: admin
      default_password: your-password

output:
  - type: filesystem
    config:
      path: /var/backups/network
      retention: 10

scheduler:
  enabled: true
  cron: "0 * * * *"  # Every hour

logging:
  level: INFO
```

## Main Features

### Dashboard
- View system and scheduler status
- Trigger manual backup
- Start/Stop scheduler

### Devices
- List devices from NetBox
- Last backup status
- Access backup history

### Backups
- View backup history per device
- View backup content
- Automatic rotation (n files)

## Supported Device Types

- Cisco IOS/IOS-XE/IOS-XR/NX-OS/ASA/Small Business
- Juniper Junos
- Arista EOS
- HP Procurve/Comware
- Dell OS10
- FortiGate/FortiOS
- Palo Alto PAN-OS
- MikroTik RouterOS

## Extensibility

### Add Input Module
Create `backend/modules/input/your_source.py` - see DEVELOPMENT.md

### Add Output Module
Create `backend/modules/output/your_dest.py` - see DEVELOPMENT.md

### Add Device Model
Create `backend/modules/models/your_vendor.py` - see DEVELOPMENT.md

## Troubleshooting

### Backend won't start
- Verify all dependencies are installed
- Check config.yaml configuration file
- Review logs: `journalctl -u edna -f`

### No devices found
- Verify NetBox connection
- Check API token
- Verify devices have:
  - Custom field `edna_backup: true`
  - Custom field `edna_model` with device type
  - Primary IP configured
  - Status "active"

### Device connection errors
- Verify credentials (username/password or group credentials)
- Check network connectivity
- Verify SSH is enabled on devices
- Check firewalls
- Review logs for detailed error messages

### Frontend can't connect to backend
- Verify backend is running on port 8000
- Check CORS in config.yaml
- For development: verify proxy.conf.json
- For production: verify Nginx configuration

## Complete Documentation

- `README.md` - Project overview
- `INSTALL.md` - Detailed installation guide
- `DEVELOPMENT.md` - Module development guide

## License

MIT License - See LICENSE file
