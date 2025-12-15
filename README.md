# EDNA - nEtwork Device coNfiguration bAckup

Modular system for automated network device configuration backup, inspired by [Oxidized](https://github.com/ytti/oxidized).

Unlike Oxidized, EDNA does not rely on `diff` to version configuration backups. This design choice solves situations where secret hashes change with each backup (e.g., FortiOS) and removing secrets is not desirable. The goal is to maintain complete backups for fast recovery of failed devices, with configurations left untouched as they were generated.

The filesystem output module stores a separate file for each configuration and rotates them according to the retention policy.

**This project was developed primarily (~90%) using AI assistance (GitHub Copilot & Claude) and should be considered experimental.**

## Features

- **Python Backend** with Netmiko for SSH/Telnet connections
- **Angular Frontend** for management and visualization
- **Modular System** for input sources and output destinations
- **Automatic Rotation** of backups (n historical files)
- **YAML Configuration** without database
- **Extensible** - easy to add new modules

## Architecture

```
edna/
├── backend/           # Python backend
│   ├── core/          # Core engine
│   ├── modules/       # Plugin system
│   │   ├── input/     # Input sources (NetBox, CSV, etc.)
│   │   ├── output/    # Output destinations (filesystem, git, etc.)
│   │   └── models/    # Device models (Cisco, Juniper, etc.)
│   └── api/           # FastAPI REST endpoints
└── frontend/          # Angular frontend
    └── src/
        ├── app/
        └── assets/
```

## Installation

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Frontend

```bash
cd frontend
npm install
```

## Configuration

Edit `config/config.yaml`:

```yaml
# Input source configuration
input:
  type: netbox
  config:
    url: https://netbox.example.com
    token: your-api-token

# Output destination
output:
  type: filesystem
  config:
    path: /var/backups/network
    retention: 10  # Number of backups to keep

# Scheduler
scheduler:
  enabled: true
  cron: "0 * * * *"  # Every hour
```

## Running

### Backend
```bash
cd backend
python main.py
```

### Frontend
```bash
cd frontend
ng serve
```

Access at `http://localhost:4200`

## Adding New Modules

### Input Module
Create `backend/modules/input/your_source.py` implementing `InputModule`

### Output Module
Create `backend/modules/output/your_destination.py` implementing `OutputModule`

### Device Model
Create `backend/modules/models/your_vendor.py` implementing `DeviceModel`

## License

MIT