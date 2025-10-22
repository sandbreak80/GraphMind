#!/bin/bash

# Let's Encrypt SSL Certificate Setup for emini.riffyx.com
# This script sets up real SSL certificates for production

set -e

DOMAIN="emini.riffyx.com"
EMAIL="your-email@example.com"  # Change this to your email
NGINX_CONTAINER="emini-nginx"

echo "🔐 Setting up Let's Encrypt SSL certificates for $DOMAIN..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "This script must be run as root (use sudo)"
    exit 1
fi

# Check if certbot is installed
if ! command -v certbot &> /dev/null; then
    print_status "Installing certbot..."
    apt update
    apt install -y certbot
fi

# Check if domain is accessible
print_status "Checking if domain $DOMAIN is accessible..."
if ! curl -s "http://$DOMAIN" > /dev/null; then
    print_error "Domain $DOMAIN is not accessible. Please ensure:"
    echo "   1. DNS is pointing to this server"
    echo "   2. Port 80 is open"
    echo "   3. Nginx is running and serving the domain"
    exit 1
fi

print_success "Domain is accessible"

# Stop nginx temporarily
print_status "Stopping nginx for certificate generation..."
docker stop $NGINX_CONTAINER 2>/dev/null || true

# Generate certificates
print_status "Generating SSL certificates..."
certbot certonly --standalone \
    --email $EMAIL \
    --agree-tos \
    --no-eff-email \
    --domains $DOMAIN

# Create SSL directory
mkdir -p nginx/ssl

# Copy certificates
print_status "Copying certificates..."
cp /etc/letsencrypt/live/$DOMAIN/fullchain.pem nginx/ssl/cert.pem
cp /etc/letsencrypt/live/$DOMAIN/privkey.pem nginx/ssl/key.pem

# Set proper permissions
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem

print_success "SSL certificates generated and copied"

# Start nginx
print_status "Starting nginx with SSL certificates..."
docker start $NGINX_CONTAINER

# Test SSL
print_status "Testing SSL configuration..."
sleep 5
if curl -s "https://$DOMAIN" > /dev/null; then
    print_success "SSL is working correctly!"
else
    print_error "SSL test failed. Check nginx configuration."
fi

# Set up auto-renewal
print_status "Setting up certificate auto-renewal..."
cat > /etc/cron.d/certbot-renew << EOF
# Renew Let's Encrypt certificates
0 12 * * * root certbot renew --quiet --post-hook "docker restart $NGINX_CONTAINER"
EOF

print_success "Auto-renewal configured"

echo ""
print_success "SSL setup completed!"
echo "🌐 Your site is now available at: https://$DOMAIN"
echo "🔐 SSL certificates will auto-renew via cron job"
echo ""
print_warning "Next steps:"
echo "   1. Test your site thoroughly"
echo "   2. Set up monitoring for certificate expiration"
echo "   3. Consider using a reverse proxy like Cloudflare for additional security"