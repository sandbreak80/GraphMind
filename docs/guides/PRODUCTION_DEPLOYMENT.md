# 🚀 Production Deployment Guide - emini.riffyx.com

Complete guide for deploying EminiPlayer RAG to your production domain.

## 📋 Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04+ or similar Linux distribution
- **RAM**: 8GB+ (16GB+ recommended for optimal performance)
- **Storage**: 50GB+ SSD
- **CPU**: 4+ cores
- **Network**: Static IP address with ports 80, 443 open

### Software Requirements
- Docker 20.10+
- Docker Compose 2.0+
- Git
- Nginx (optional, for additional reverse proxy)

### Domain Setup
- Domain `emini.riffyx.com` pointing to your server's IP
- DNS A record configured
- Port 80 and 443 accessible from internet

## 🔧 Quick Deployment

### 1. Clone and Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd EminiPlayer

# Make scripts executable
chmod +x deploy.sh
chmod +x nginx/generate-ssl.sh
chmod +x nginx/setup-letsencrypt.sh
```

### 2. Deploy with Self-Signed Certificates (Development)
```bash
# Quick deployment with self-signed certificates
./deploy.sh
```

### 3. Deploy with Let's Encrypt (Production)
```bash
# First, ensure domain is accessible
curl http://emini.riffyx.com

# Generate real SSL certificates
sudo ./nginx/setup-letsencrypt.sh

# Update email in the script first!
# Edit nginx/setup-letsencrypt.sh and change:
# EMAIL="your-email@example.com"
```

## 🔐 SSL Certificate Setup

### Option 1: Let's Encrypt (Recommended)
```bash
# Run the Let's Encrypt setup script
sudo ./nginx/setup-letsencrypt.sh

# The script will:
# - Install certbot
# - Generate certificates
# - Configure auto-renewal
# - Restart nginx
```

### Option 2: Custom Certificates
```bash
# Place your certificates in nginx/ssl/
cp your-cert.pem nginx/ssl/cert.pem
cp your-key.pem nginx/ssl/key.pem

# Set proper permissions
chmod 644 nginx/ssl/cert.pem
chmod 600 nginx/ssl/key.pem

# Restart nginx
docker-compose restart nginx
```

## 🌐 Domain Configuration

### DNS Setup
Configure your DNS provider with these records:

```
Type: A
Name: emini
Value: YOUR_SERVER_IP
TTL: 300

Type: CNAME
Name: www.emini
Value: emini.riffyx.com
TTL: 300
```

### Firewall Configuration
```bash
# Allow HTTP and HTTPS traffic
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH (if needed)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

## 🐳 Docker Services

### Service Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx Proxy   │────│   Frontend      │    │   RAG Backend   │
│   Port 80/443   │    │   Port 3000     │    │   Port 8000     │
│   emini.riffyx.com │    │   Next.js      │    │   FastAPI       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Service Configuration
- **Nginx**: Reverse proxy with SSL termination
- **Frontend**: Next.js application with SSR
- **Backend**: FastAPI with RAG capabilities
- **Obsidian**: External integration via HTTPS

## 🔧 Configuration Files

### Environment Variables
```bash
# Production environment
DOMAIN=emini.riffyx.com
FRONTEND_URL=https://emini.riffyx.com
API_URL=https://emini.riffyx.com/api
SSL_CERT_PATH=./nginx/ssl/cert.pem
SSL_KEY_PATH=./nginx/ssl/key.pem
```

### Nginx Configuration
- **SSL/TLS**: Modern cipher suites
- **Security Headers**: HSTS, XSS protection, etc.
- **Rate Limiting**: API and chat endpoints
- **CORS**: Configured for frontend domain

## 📊 Monitoring and Logs

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f nginx
docker-compose logs -f frontend
docker-compose logs -f rag-service
```

### Health Checks
```bash
# Frontend
curl https://emini.riffyx.com

# API
curl https://emini.riffyx.com/api/health

# SSL Certificate
openssl s_client -connect emini.riffyx.com:443 -servername emini.riffyx.com
```

### Performance Monitoring
```bash
# Container stats
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

## 🔄 Maintenance

### Updates
```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Backup
```bash
# Backup volumes
docker run --rm -v eminiplayer_chroma-data:/data -v $(pwd):/backup alpine tar czf /backup/chroma-backup.tar.gz -C /data .

# Backup configuration
tar czf config-backup.tar.gz nginx/ docker-compose.yml .env.production
```

### SSL Certificate Renewal
```bash
# Manual renewal
sudo certbot renew

# Check certificate status
sudo certbot certificates

# Test renewal
sudo certbot renew --dry-run
```

## 🛡️ Security

### Security Headers
- **HSTS**: Strict Transport Security
- **X-Frame-Options**: Clickjacking protection
- **X-Content-Type-Options**: MIME type sniffing protection
- **X-XSS-Protection**: Cross-site scripting protection

### Rate Limiting
- **API Endpoints**: 10 requests/second
- **Chat Endpoints**: 5 requests/second
- **Burst Handling**: Configurable burst limits

### Firewall Rules
```bash
# Basic UFW rules
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
```

## 🚨 Troubleshooting

### Common Issues

#### 1. SSL Certificate Problems
```bash
# Check certificate validity
openssl x509 -in nginx/ssl/cert.pem -text -noout

# Verify domain
curl -I https://emini.riffyx.com
```

#### 2. Service Not Starting
```bash
# Check logs
docker-compose logs

# Check port conflicts
sudo netstat -tlnp | grep :80
sudo netstat -tlnp | grep :443
```

#### 3. Domain Not Resolving
```bash
# Check DNS
nslookup emini.riffyx.com
dig emini.riffyx.com

# Check local resolution
curl -H "Host: emini.riffyx.com" http://localhost
```

### Performance Issues

#### 1. High Memory Usage
```bash
# Check container memory
docker stats

# Restart services
docker-compose restart
```

#### 2. Slow Response Times
```bash
# Check nginx logs
docker-compose logs nginx | grep -i error

# Check backend logs
docker-compose logs rag-service | grep -i error
```

## 📈 Scaling

### Horizontal Scaling
```yaml
# docker-compose.override.yml
services:
  rag-service:
    deploy:
      replicas: 3
  frontend:
    deploy:
      replicas: 2
```

### Load Balancing
- Use external load balancer (HAProxy, Nginx)
- Configure sticky sessions if needed
- Monitor backend health

## 🔍 Monitoring Setup

### Basic Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor system resources
htop
iotop
nethogs
```

### Advanced Monitoring
- **Prometheus**: Metrics collection
- **Grafana**: Visualization
- **AlertManager**: Alerting
- **ELK Stack**: Log aggregation

## 📞 Support

### Log Collection
```bash
# Collect all logs
docker-compose logs > deployment-logs.txt

# System information
uname -a > system-info.txt
docker version >> system-info.txt
docker-compose version >> system-info.txt
```

### Health Check Script
```bash
#!/bin/bash
# health-check.sh

echo "🔍 EminiPlayer RAG Health Check"
echo "================================"

# Check domain
echo "Domain: emini.riffyx.com"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://emini.riffyx.com

# Check API
echo "API: /api/health"
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://emini.riffyx.com/api/health

# Check SSL
echo "SSL Certificate:"
echo | openssl s_client -connect emini.riffyx.com:443 -servername emini.riffyx.com 2>/dev/null | openssl x509 -noout -dates

# Check containers
echo "Container Status:"
docker-compose ps
```

---

## 🎯 Quick Start Checklist

- [ ] Server prepared with Docker and Docker Compose
- [ ] Domain `emini.riffyx.com` pointing to server IP
- [ ] Ports 80 and 443 open in firewall
- [ ] Repository cloned and scripts made executable
- [ ] SSL certificates generated (Let's Encrypt or custom)
- [ ] Services deployed and running
- [ ] Domain accessible via HTTPS
- [ ] API endpoints responding
- [ ] Monitoring and logging configured
- [ ] Backup strategy implemented

**Your EminiPlayer RAG system is now live at https://emini.riffyx.com! 🚀**