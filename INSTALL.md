# EDNA Installation Guide

## Prerequisites

- Python 3.8+
- Node.js 18+
- Nginx
- Systemd

## Backend Setup

1. Install Python dependencies:
```bash
cd /opt/edna/backend
pip install -r requirements.txt
```

2. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

3. Install systemd service:
```bash
sudo cp /opt/edna/backend/edna.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable edna
sudo systemctl start edna
```

4. Check status:
```bash
sudo systemctl status edna
sudo journalctl -u edna -f  # View logs
```

## Frontend Setup

1. Install dependencies:
```bash
cd /opt/edna/frontend-ng
npm install
```

2. Build for production:
```bash
npm run build
```

3. Configure Nginx:
```bash
sudo cp /opt/edna/nginx-edna.conf /etc/nginx/sites-available/edna
sudo ln -s /etc/nginx/sites-available/edna /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Access

- Frontend: http://your-server/
- Backend API: http://your-server/api/

## Systemd Commands

```bash
# Start service
sudo systemctl start edna

# Stop service
sudo systemctl stop edna

# Restart service
sudo systemctl restart edna

# View logs
sudo journalctl -u edna -f

# Enable on boot
sudo systemctl enable edna

# Disable on boot
sudo systemctl disable edna
```

## Development Mode

### Backend
```bash
cd /opt/edna/backend
python main.py
```

### Frontend
```bash
cd /opt/edna/frontend-ng
npm start
```
