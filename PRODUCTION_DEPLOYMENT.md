# Production Deployment Guide

## Architecture Overview

```
Internet
    ↓
Nginx (Reverse Proxy with SSL Termination)
    ↓
FastAPI Container ←→ n8n Container (Internal Communication)
```

### Why Reverse Proxy is Needed

1. **SSL Termination**: Handles HTTPS encryption/decryption
2. **Load Balancing**: Distributes traffic to backend services
3. **Security**: Acts as a shield protecting backend services
4. **Routing**: Directs requests to appropriate services based on URL paths
5. **Rate Limiting**: Prevents abuse and DDoS attacks

### SSL Termination at Nginx

SSL termination occurs at the Nginx reverse proxy level because:
- Containers don't need to handle SSL encryption/decryption
- Better performance and resource utilization
- Simplified certificate management
- Centralized security configuration

### Internal Container Communication

- FastAPI and n8n communicate internally via Docker's DNS resolution
- They use service names as hostnames (e.g., `http://n8n:5678`)
- This communication is secured within the Docker network
- External traffic never directly accesses containers

## Security Configuration

### Nginx Security Headers
- HSTS (HTTP Strict Transport Security)
- X-Frame-Options to prevent clickjacking
- X-Content-Type-Options to prevent MIME-type confusion
- Content Security Policy for XSS protection

### Rate Limiting
- API endpoints limited to 10 requests per second
- General traffic limited to 20 requests per second
- Helps prevent abuse and DDoS attacks

### n8n Security
- Basic authentication enabled
- Secure cookies enforced
- Webhook URL configured for HTTPS

## Production Environment Variables

Update your `.env` file for production:

```bash
# Domain Configuration
DOMAIN=yourdomain.com

# Google Generative AI API Key
GEMINI_API_KEY=your_production_api_key_here

# n8n Configuration
N8N_WEBHOOK_URL=https://yourdomain.com/n8n/webhook
N8N_USERNAME=your_admin_username
N8N_PASSWORD=your_secure_password

# Application Settings
APP_ENV=production
LOG_LEVEL=INFO
REQUEST_TIMEOUT=10
MAX_RETRIES=2

# Backend Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000

# Timezone
TIMEZONE=UTC
```

## Deployment Steps

### 1. Initial Server Setup (Ubuntu 22.04)

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install fail2ban for security
sudo apt install fail2ban -y

# Install UFW firewall
sudo apt install ufw -y

# Configure firewall
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 'Nginx Full'
sudo ufw --force enable

# Verify firewall status
sudo ufw status
```

### 2. Install Docker and Docker Compose

```bash
# Install Docker
sudo apt install ca-certificates curl gnupg lsb-release -y
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add current user to docker group
sudo usermod -aG docker $USER

# Enable Docker to start on boot
sudo systemctl enable docker

# Log out and back in for group changes to take effect
exit
```

### 3. Clone Repository and Prepare Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/your-repo.git
cd your-repo

# Create environment file
cp .env.example .env
nano .env  # Edit with your production values
```

### 4. Setup SSL Certificate with Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL certificate
sudo certbot --nginx -d yourdomain.com

# Test automatic renewal
sudo certbot renew --dry-run

# Add cron job for automatic renewal
echo "0 12 * * * /usr/bin/certbot renew --quiet" | crontab -
```

### 5. Update Nginx Configuration for Your Domain

```bash
# Update the nginx configuration with your domain
sudo nano nginx/conf.d/default.conf
# Replace YOUR_DOMAIN with your actual domain
```

### 6. Start Production Services

```bash
# Build and start services
docker compose -f docker-compose.prod.yml up -d --build

# Check service status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

### 7. Configure Domain DNS

Point your domain's A record to your VPS IP address:
- Type: A
- Name: @ (or your domain)
- Value: [Your VPS IP Address]

### 8. Verify Installation

```bash
# Check if services are running
curl https://yourdomain.com/health

# Check if n8n is accessible
curl -u username:password https://yourdomain.com/n8n
```

## Firewall Configuration

```bash
# Open required ports
sudo ufw allow 80/tcp    # HTTP (redirects to HTTPS)
sudo ufw allow 443/tcp   # HTTPS
sudo ufw deny 8000/tcp   # Block direct FastAPI access
sudo ufw deny 5678/tcp   # Block direct n8n access
```

## Backup Strategy

### n8n Data Backup

```bash
# Create backup script
cat << 'EOF' > backup_n8n.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/home/$USER/backups"
mkdir -p $BACKUP_DIR
tar -czf $BACKUP_DIR/n8n_backup_$DATE.tar.gz n8n_data/
echo "Backup created: n8n_backup_$DATE.tar.gz"
EOF

chmod +x backup_n8n.sh

# Schedule daily backups
echo "0 2 * * * /home/$USER/your-repo/backup_n8n.sh" | crontab -
```

## Security Checklist

### Before Going Live

- [ ] Update all passwords and API keys
- [ ] Verify SSL certificate installation
- [ ] Test webhook functionality
- [ ] Confirm rate limiting works
- [ ] Verify firewall rules
- [ ] Test backup procedures
- [ ] Review logs for sensitive information

### Ongoing Maintenance

- [ ] Monitor logs regularly
- [ ] Rotate API keys periodically
- [ ] Update software packages regularly
- [ ] Check SSL certificate expiration
- [ ] Review security configurations
- [ ] Monitor resource usage

## Troubleshooting

### Common Issues

1. **SSL Certificate Problems**
   ```bash
   sudo certbot --nginx -d yourdomain.com
   sudo nginx -t  # Test nginx configuration
   sudo systemctl reload nginx
   ```

2. **Service Not Starting**
   ```bash
   docker compose -f docker-compose.prod.yml logs --tail=50
   docker ps  # Check if containers are running
   ```

3. **Webhook Issues**
   - Verify webhook URL in n8n workflow
   - Check that the webhook path matches Nginx config
   - Ensure SSL certificate is valid

4. **Performance Issues**
   - Monitor resource usage: `docker stats`
   - Adjust resource limits in docker-compose file
   - Consider upgrading VPS resources if needed

### Monitoring Commands

```bash
# Check system resources
htop

# Monitor Docker containers
docker stats

# Check logs
docker compose -f docker-compose.prod.yml logs -f --tail=50

# Check Nginx status
sudo systemctl status nginx

# Check firewall status
sudo ufw status
```

## Rollback Procedure

If you need to rollback:

```bash
# Stop current services
docker compose -f docker-compose.prod.yml down

# If needed, restore from backup
tar -xzf backup_file.tar.gz

# Restart services
docker compose -f docker-compose.prod.yml up -d
```

Your production deployment is now complete with proper security, SSL, and reverse proxy configuration!