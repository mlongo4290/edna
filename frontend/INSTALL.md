# EDNA Frontend - Installation Guide

## Prerequisites

- Node.js 18 or higher
- npm

## Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure API endpoint (if different from default):
```bash
# Edit src/app/services/api.service.ts
# Change the apiUrl if your backend is not at localhost:8000
```

## Development

Run the development server:
```bash
npm start
# or
ng serve
```

The application will be available at `http://localhost:4200`

## Production Build

Build for production:
```bash
npm run build
```

The build artifacts will be in the `dist/` directory.

## Deployment

### Nginx Configuration

Example Nginx configuration:

```nginx
server {
    listen 80;
    server_name edna.example.com;
    
    root /opt/edna/frontend/dist/edna-frontend;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Proxy API requests to backend
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Apache Configuration

Example Apache configuration:

```apache
<VirtualHost *:80>
    ServerName edna.example.com
    
    DocumentRoot /opt/edna/frontend/dist/edna-frontend
    
    <Directory /opt/edna/frontend/dist/edna-frontend>
        Options -Indexes +FollowSymLinks
        AllowOverride All
        Require all granted
        
        # Rewrite for Angular routing
        RewriteEngine On
        RewriteBase /
        RewriteRule ^index\.html$ - [L]
        RewriteCond %{REQUEST_FILENAME} !-f
        RewriteCond %{REQUEST_FILENAME} !-d
        RewriteRule . /index.html [L]
    </Directory>
    
    # Proxy API
    ProxyPass /api http://localhost:8000/api
    ProxyPassReverse /api http://localhost:8000/api
</VirtualHost>
```
