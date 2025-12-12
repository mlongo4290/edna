# EDNA Backend - Installation Guide

## Prerequisites

- Python 3.8 or higher
- pip

## Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
```

3. Activate the virtual environment:
```bash
# On Linux/Mac
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Configure the application:
```bash
# Edit config/config.yaml with your settings
cp config/config.example.yaml config/config.yaml
nano config/config.yaml
```

Key configuration items:
- **NetBox URL and API token**: Required for device discovery
- **Output path**: Where backups will be stored
- **Retention**: Number of backups to keep per device
- **Scheduler interval**: Backup frequency in seconds

6. Create backup directory:
```bash
sudo mkdir -p /var/backups/network
sudo chown $USER:$USER /var/backups/network
```

## Running

Start the backend server:
```bash
python main.py
```

The API will be available at `http://localhost:8000`

## Testing

Test the API:
```bash
# Check status
curl http://localhost:8000/api/status

# Get devices
curl http://localhost:8000/api/devices

# Trigger manual backup
curl -X POST http://localhost:8000/api/backup/run
```

## Production Deployment

Use a process manager like systemd or supervisor:

### Systemd Service

Create `/etc/systemd/system/edna.service`:

```ini
[Unit]
Description=EDNA Service
After=network.target

[Service]
Type=simple
User=edna
WorkingDirectory=/opt/edna/backend
Environment="PATH=/opt/edna/backend/venv/bin"
ExecStart=/opt/edna/backend/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable edna
sudo systemctl start edna
sudo systemctl status edna
```
