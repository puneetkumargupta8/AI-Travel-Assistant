# Production Setup Guide - Complete Reference

## Overview
This document provides a comprehensive guide to deploying your AI Travel Assistant to production with all security and performance considerations.

## Architecture Diagram

```
Internet Traffic
       ↓
┌─────────────────┐
│   Nginx         │ ← SSL Termination, Rate Limiting, Security Headers
│ (Reverse Proxy) │
└─────────┬───────┘
          │
    ┌─────▼──────┐    ┌──────────┐
    │  FastAPI   │◄──►│   n8n    │ ← Internal Docker Network
    │ Container  │    │ Container│
    └────────────┘    └──────────┘
         │                   │
    ┌────▼───────────────────▼──┐
    │     Internal Network      │
    │      (Docker Bridge)      │
    └───────────────────────────┘
```

## Component Responsibilities

### Nginx (Edge Server)
- SSL/TLS termination
- Request routing to appropriate services
- Rate limiting and DDoS protection
- Security header enforcement
- Static file serving (if needed)

### FastAPI Container
- Handles API requests
- Validates input/output
- Communicates with n8n via internal network
- Implements business logic

### n8n Container
- Processes workflows
- Handles webhook requests
- Sends emails via SMTP
- Stores workflow configurations

## SSL/HTTPS Configuration

### Let's Encrypt Certificate Setup
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain certificate (replace with your domain)
sudo certbot --nginx -d yourdomain.com

# Test renewal
sudo certbot renew --dry-run
```

### Automatic Renewal Cron Job
```bash
# Add to crontab
0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'systemctl reload nginx'
```

## Security Configuration Details

### Nginx Security Headers
- **Strict-Transport-Security**: Enforces HTTPS usage
- **X-Frame-Options**: Prevents clickjacking
- **X-Content-Type-Options**: Prevents MIME-type confusion
- **Content-Security-Policy**: Mitigates XSS attacks

### Rate Limiting Configuration
- **API Endpoints**: 10 requests per second
- **General Traffic**: 20 requests per second
- **Burst Capacity**: Allows occasional spikes

### n8n Security Settings
- **Basic Authentication**: Required for UI access
- **Secure Cookies**: Enabled for production
- **HTTPS Webhook URL**: Enforced in production

## Environment Variables for Production

```bash
# Essential for production
DOMAIN=yourdomain.com
APP_ENV=production
LOG_LEVEL=INFO

# Security settings
N8N_BASIC_AUTH_ACTIVE=true
N8N_SECURE_COOKIE=true

# Webhook configuration
N8N_WEBHOOK_URL=https://yourdomain.com/n8n/webhook

# Timezone (critical for scheduling)
TIMEZONE=UTC

# Resource limits
REQUEST_TIMEOUT=10
MAX_RETRIES=2
```

## Firewall Configuration (UFW)

```bash
# Allow essential services
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'

# Deny direct access to internal services
sudo ufw deny 8000
sudo ufw deny 5678

# Enable firewall
sudo ufw --force enable
```

## Monitoring and Logging

### System Monitoring
```bash
# Monitor system resources
htop
docker stats

# Check application logs
docker compose -f docker-compose.prod.yml logs -f --tail=50
```

### Log Rotation
Configure log rotation to prevent disk space issues:

```bash
sudo nano /etc/logrotate.d/nginx-fastapi
```

Content:
```
/var/log/nginx/fastapi_*.log {
    daily
    missingok
    rotate 52
    compress
    delaycompress
    notifempty
    create 640 nginx adm
    postrotate
        systemctl reload nginx
    endscript
}
```

## Backup Strategy

### n8n Data Backup
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/$USER/backups"
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/n8n_backup_$DATE.tar.gz n8n_data/
echo "Backup created: n8n_backup_$DATE.tar.gz"
```

### Scheduled Backups
```bash
# Daily backup at 2 AM
0 2 * * * /home/$USER/your-repo/backup_n8n.sh
```

## Performance Tuning

### Docker Resource Limits
In `docker-compose.prod.yml`:
```yaml
deploy:
  resources:
    limits:
      memory: 512M    # Adjust based on your needs
      cpus: '0.5'
    reservations:
      memory: 256M
      cpus: '0.25'
```

### Nginx Performance
- Enable gzip compression
- Optimize worker connections
- Configure proper buffer sizes
- Set appropriate timeouts

## Health Checks and Monitoring

### Application Health Check
```bash
# Verify application is responding
curl -k https://yourdomain.com/health
```

### Service Status
```bash
# Check if all containers are running
docker compose -f docker-compose.prod.yml ps

# Check specific service logs
docker compose -f docker-compose.prod.yml logs fastapi
docker compose -f docker-compose.prod.yml logs n8n
```

## Troubleshooting Common Issues

### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew manually if needed
sudo certbot renew

# Verify nginx SSL configuration
sudo nginx -t
```

### Service Connectivity Issues
```bash
# Test internal connectivity
docker compose -f docker-compose.prod.yml exec fastapi curl http://n8n:5678/

# Check network configuration
docker network ls
docker inspect [network-id]
```

### Performance Issues
```bash
# Monitor resource usage
docker stats

# Check for bottlenecks
docker compose -f docker-compose.prod.yml logs --tail=100 -f
```

## Security Best Practices

### Regular Updates
- Keep Docker and system packages updated
- Monitor for security vulnerabilities
- Apply security patches promptly

### Access Control
- Use strong passwords for n8n authentication
- Rotate API keys regularly
- Limit SSH access to authorized IPs

### Monitoring
- Set up alerts for service downtime
- Monitor access logs for suspicious activity
- Track performance metrics

## Rollback Plan

If production issues occur:

1. **Immediate Response**:
   ```bash
   docker compose -f docker-compose.prod.yml logs --tail=100
   ```

2. **Rollback Command**:
   ```bash
   # Stop current services
   docker compose -f docker-compose.prod.yml down
   
   # If needed, restore from backup
   tar -xzf backup_file.tar.gz
   
   # Restart previous version
   docker compose -f docker-compose.prod.yml up -d
   ```

This comprehensive setup ensures your AI Travel Assistant is deployed securely, scalably, and with proper monitoring and maintenance procedures in place.