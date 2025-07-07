# Deployment Guide - Forge-API-Tool

## 🎯 Overview
This guide provides comprehensive instructions for deploying the Forge-API-Tool across different environments, from development to production.

## 📋 Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.14+, or Linux
- **Memory**: Minimum 4GB RAM (8GB recommended for batch operations)
- **Storage**: 2GB free space for application + space for generated images
- **Network**: Internet connection for API access

### Required Accounts and API Keys
- **Forge API Account**: Active account with API key
- **Optional**: Additional AI service accounts for extended functionality

### Software Dependencies
- Python 3.8+
- pip (Python package manager)
- Git (for version control)
- Virtual environment tool (venv or conda)

## 🚀 Environment Setup

### Development Environment
```bash
# Clone the repository
git clone <repository-url>
cd Forge-API-Tool

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up pre-commit hooks
pre-commit install

# Configure environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Staging Environment
```bash
# Set up staging environment
python -m venv venv-staging
source venv-staging/bin/activate

# Install production dependencies only
pip install -r requirements.txt

# Configure staging environment
cp configs/staging.json configs/config.json
# Edit configuration for staging settings
```

### Production Environment
```bash
# Set up production environment
python -m venv venv-production
source venv-production/bin/activate

# Install production dependencies
pip install -r requirements.txt

# Configure production environment
cp configs/production.json configs/config.json
# Edit configuration for production settings
```

## ⚙️ Configuration Management

### Environment Variables
Create a `.env` file in the project root:

```bash
# API Configuration
FORGE_API_KEY=your_forge_api_key_here
FORGE_API_URL=https://api.forge.com/v1

# Application Configuration
APP_ENV=production  # development, staging, production
LOG_LEVEL=INFO
DEBUG=False

# Security Configuration
SECRET_KEY=your_secret_key_here
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Database Configuration (if applicable)
DATABASE_URL=sqlite:///forge_api_tool.db

# Cache Configuration
CACHE_TYPE=simple  # simple, redis, memcached
REDIS_URL=redis://localhost:6379/0

# File Storage
OUTPUT_DIR=outputs/
LOG_DIR=logs/
CACHE_DIR=cache/
```

### Configuration Files
The application uses JSON configuration files in the `configs/` directory:

#### Base Configuration (`configs/base.json`)
```json
{
  "api": {
    "timeout": 30,
    "retry_attempts": 3,
    "retry_delay": 1
  },
  "image_generation": {
    "default_width": 1024,
    "default_height": 1024,
    "max_batch_size": 10,
    "quality": "high"
  },
  "wildcards": {
    "enabled": true,
    "max_depth": 3,
    "cache_enabled": true
  },
  "logging": {
    "level": "INFO",
    "format": "detailed",
    "rotation": "daily"
  }
}
```

#### Production Configuration (`configs/production.json`)
```json
{
  "api": {
    "timeout": 60,
    "retry_attempts": 5,
    "retry_delay": 2
  },
  "image_generation": {
    "default_width": 1024,
    "default_height": 1024,
    "max_batch_size": 5,
    "quality": "high"
  },
  "wildcards": {
    "enabled": true,
    "max_depth": 2,
    "cache_enabled": true
  },
  "logging": {
    "level": "WARNING",
    "format": "json",
    "rotation": "hourly"
  },
  "security": {
    "rate_limiting": true,
    "max_requests_per_minute": 100,
    "session_timeout": 3600
  }
}
```

## 🐳 Docker Deployment

### Dockerfile
```dockerfile
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p outputs logs cache

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose port for web dashboard
EXPOSE 5000

# Run the application
CMD ["python", "cli.py", "web", "start", "production"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  forge-api-tool:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FORGE_API_KEY=${FORGE_API_KEY}
      - APP_ENV=production
    volumes:
      - ./outputs:/app/outputs
      - ./logs:/app/logs
      - ./cache:/app/cache
      - ./configs:/app/configs
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

volumes:
  redis_data:
```

### Docker Deployment Commands
```bash
# Build and run with Docker Compose
docker-compose up -d

# Build image manually
docker build -t forge-api-tool .

# Run container
docker run -d \
  --name forge-api-tool \
  -p 5000:5000 \
  -e FORGE_API_KEY=your_key \
  -v $(pwd)/outputs:/app/outputs \
  -v $(pwd)/logs:/app/logs \
  forge-api-tool

# View logs
docker logs forge-api-tool

# Stop container
docker stop forge-api-tool
```

## ☁️ Cloud Deployment

### AWS Deployment

#### EC2 Instance Setup
```bash
# Launch EC2 instance (Ubuntu 20.04 recommended)
# Connect to instance
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Clone repository
git clone <repository-url>
cd Forge-API-Tool

# Set up virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure application
cp .env.example .env
# Edit .env with your configuration

# Set up systemd service
sudo nano /etc/systemd/system/forge-api-tool.service
```

#### Systemd Service Configuration
```ini
[Unit]
Description=Forge API Tool
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/Forge-API-Tool
Environment=PATH=/home/ubuntu/Forge-API-Tool/venv/bin
ExecStart=/home/ubuntu/Forge-API-Tool/venv/bin/python cli.py web start production
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### Start Service
```bash
# Enable and start service
sudo systemctl enable forge-api-tool
sudo systemctl start forge-api-tool

# Check status
sudo systemctl status forge-api-tool

# View logs
sudo journalctl -u forge-api-tool -f
```

### Google Cloud Platform Deployment

#### App Engine Configuration
```yaml
# app.yaml
runtime: python39
entrypoint: python cli.py web start production

env_variables:
  FORGE_API_KEY: "your_api_key"
  APP_ENV: "production"

handlers:
  - url: /.*
    script: auto

automatic_scaling:
  target_cpu_utilization: 0.6
  min_instances: 1
  max_instances: 10
```

#### Deploy to App Engine
```bash
# Install Google Cloud SDK
# Initialize project
gcloud init

# Deploy application
gcloud app deploy

# View application
gcloud app browse
```

### Azure Deployment

#### Azure App Service Configuration
```bash
# Create App Service
az webapp create \
  --resource-group your-resource-group \
  --plan your-app-service-plan \
  --name forge-api-tool \
  --runtime "PYTHON|3.9"

# Configure environment variables
az webapp config appsettings set \
  --resource-group your-resource-group \
  --name forge-api-tool \
  --settings FORGE_API_KEY="your_api_key" APP_ENV="production"

# Deploy application
az webapp deployment source config-local-git \
  --resource-group your-resource-group \
  --name forge-api-tool

git remote add azure <azure-git-url>
git push azure main
```

## 🔧 Web Server Configuration

### Nginx Configuration
```nginx
# /etc/nginx/sites-available/forge-api-tool
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/Forge-API-Tool/web_dashboard/static/;
        expires 30d;
    }

    location /outputs/ {
        alias /path/to/Forge-API-Tool/outputs/;
        expires 1d;
    }
}
```

### Apache Configuration
```apache
# /etc/apache2/sites-available/forge-api-tool.conf
<VirtualHost *:80>
    ServerName your-domain.com
    
    ProxyPreserveHost On
    ProxyPass / http://127.0.0.1:5000/
    ProxyPassReverse / http://127.0.0.1:5000/
    
    Alias /static/ /path/to/Forge-API-Tool/web_dashboard/static/
    <Directory /path/to/Forge-API-Tool/web_dashboard/static/>
        Require all granted
    </Directory>
    
    Alias /outputs/ /path/to/Forge-API-Tool/outputs/
    <Directory /path/to/Forge-API-Tool/outputs/>
        Require all granted
    </Directory>
</VirtualHost>
```

## 🔒 Security Configuration

### SSL/TLS Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Obtain SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### Firewall Configuration
```bash
# Configure UFW firewall
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### Security Headers
```nginx
# Add to Nginx configuration
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
```

## 📊 Monitoring and Logging

### Application Monitoring
```bash
# Set up monitoring with systemd
sudo systemctl status forge-api-tool

# Monitor logs
tail -f logs/app.log

# Monitor resource usage
htop
iotop
```

### Log Rotation
```bash
# Configure logrotate
sudo nano /etc/logrotate.d/forge-api-tool

# Add configuration
/path/to/Forge-API-Tool/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        systemctl reload forge-api-tool
    endscript
}
```

### Health Checks
```bash
# Create health check script
cat > health_check.sh << 'EOF'
#!/bin/bash
curl -f http://localhost:5000/health || exit 1
EOF

chmod +x health_check.sh

# Add to crontab for regular checks
crontab -e
# Add: */5 * * * * /path/to/health_check.sh
```

## 🔄 Backup and Recovery

### Backup Strategy
```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backups/forge-api-tool"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup configuration
tar -czf $BACKUP_DIR/config_$DATE.tar.gz configs/

# Backup outputs (if needed)
tar -czf $BACKUP_DIR/outputs_$DATE.tar.gz outputs/

# Backup logs
tar -czf $BACKUP_DIR/logs_$DATE.tar.gz logs/

# Clean up old backups (keep 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
EOF

chmod +x backup.sh

# Add to crontab for daily backups
crontab -e
# Add: 0 2 * * * /path/to/backup.sh
```

### Recovery Procedures
```bash
# Restore from backup
tar -xzf /backups/forge-api-tool/config_YYYYMMDD_HHMMSS.tar.gz -C /

# Restart application
sudo systemctl restart forge-api-tool

# Verify recovery
curl http://localhost:5000/health
```

## 🚨 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
sudo journalctl -u forge-api-tool -f

# Check configuration
python cli.py config validate

# Check dependencies
pip list

# Check permissions
ls -la outputs/ logs/ cache/
```

#### API Connection Issues
```bash
# Test API connectivity
python cli.py api test

# Check API key
echo $FORGE_API_KEY

# Check network connectivity
curl -I https://api.forge.com/v1/health
```

#### Performance Issues
```bash
# Monitor resource usage
top
free -h
df -h

# Check application logs
tail -f logs/app.log | grep -i error

# Profile application
python -m cProfile -o profile.stats cli.py [command]
```

### Emergency Procedures
```bash
# Emergency restart
sudo systemctl restart forge-api-tool

# Rollback to previous version
git checkout HEAD~1
sudo systemctl restart forge-api-tool

# Disable application
sudo systemctl stop forge-api-tool

# Emergency maintenance mode
echo "MAINTENANCE" > maintenance.txt
```

## 📈 Performance Optimization

### Production Optimizations
```python
# In production configuration
{
  "performance": {
    "worker_processes": 4,
    "max_connections": 1000,
    "timeout": 30,
    "keepalive": 2
  },
  "caching": {
    "enabled": true,
    "type": "redis",
    "ttl": 3600
  }
}
```

### Monitoring Setup
```bash
# Install monitoring tools
sudo apt install prometheus node-exporter grafana

# Configure Prometheus
sudo nano /etc/prometheus/prometheus.yml

# Start monitoring
sudo systemctl start prometheus
sudo systemctl start grafana-server
```

This deployment guide provides comprehensive instructions for deploying the Forge-API-Tool across various environments. Customize the configurations and procedures based on your specific infrastructure and requirements. 