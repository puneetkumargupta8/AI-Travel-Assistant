#!/bin/bash
# SSL Setup Script for Production Deployment

set -e  # Exit on any error

echo "SSL Certificate Setup for AI Travel Assistant"
echo "=============================================="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should NOT be run as root" 
   exit 1
fi

# Check if domain is provided
if [ $# -eq 0 ]; then
    echo "Usage: $0 <your-domain.com>"
    exit 1
fi

DOMAIN=$1
EMAIL=$2

if [ -z "$EMAIL" ]; then
    echo "Enter your email for Let's Encrypt registration:"
    read EMAIL
fi

echo "Setting up SSL certificate for domain: $DOMAIN"
echo "Using email: $EMAIL"
echo ""

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    echo "Installing Certbot..."
    sudo apt update
    sudo apt install -y certbot python3-certbot-nginx
fi

# Check if nginx is installed
if ! command -v nginx &> /dev/null; then
    echo "Installing Nginx..."
    sudo apt install -y nginx
fi

echo "Obtaining SSL certificate from Let's Encrypt..."
sudo certbot --nginx -d $DOMAIN --non-interactive --agree-tos --email $EMAIL

echo "Testing automatic renewal..."
sudo certbot renew --dry-run

echo "Adding automatic renewal to cron..."
crontab -l | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet --post-hook 'systemctl reload nginx'"; } | crontab -

echo "Updating Nginx configuration with domain..."

# Create a temporary nginx config with the actual domain
sed "s/YOUR_DOMAIN/$DOMAIN/g" nginx/conf.d/default.conf > temp_default.conf
sudo mv temp_default.conf nginx/conf.d/default.conf

echo "Reloading Nginx configuration..."
sudo nginx -t
sudo systemctl reload nginx

echo ""
echo "SSL Setup Complete!"
echo "==================="
echo "Domain: $DOMAIN"
echo "Certificate location: /etc/letsencrypt/live/$DOMAIN/"
echo "Automatic renewal scheduled"
echo ""
echo "Next steps:"
echo "1. Update your .env file with the correct domain"
echo "2. Start your services with: docker compose -f docker-compose.prod.yml up -d --build"
echo "3. Verify the setup by visiting: https://$DOMAIN/health"