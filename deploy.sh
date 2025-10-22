#!/bin/bash

# EminiPlayer RAG Deployment Script for emini.riffyx.com
# This script sets up the complete system with frontend, backend, and nginx

set -e

echo "🚀 Deploying EminiPlayer RAG to emini.riffyx.com..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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
if [ "$EUID" -eq 0 ]; then
    print_error "Please do not run this script as root"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_status "Setting up SSL certificates..."

# Generate SSL certificates if they don't exist
if [ ! -f "nginx/ssl/cert.pem" ] || [ ! -f "nginx/ssl/key.pem" ]; then
    print_warning "SSL certificates not found. Generating self-signed certificates..."
    ./nginx/generate-ssl.sh
    print_warning "Using self-signed certificates. For production, replace with real certificates."
else
    print_success "SSL certificates found."
fi

print_status "Building and starting services..."

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build and start services
print_status "Building Docker images..."
docker-compose build --no-cache

print_status "Starting services..."
docker-compose up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check if services are running
print_status "Checking service health..."

# Check RAG service
if curl -s http://localhost:8001/health > /dev/null; then
    print_success "RAG service is running on port 8001"
else
    print_error "RAG service is not responding on port 8001"
    print_status "Checking logs..."
    docker-compose logs rag-service
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    print_success "Frontend is running on port 3000"
else
    print_error "Frontend is not responding on port 3000"
    print_status "Checking logs..."
    docker-compose logs frontend
fi

# Check nginx
if curl -s http://localhost > /dev/null; then
    print_success "Nginx is running on port 80"
else
    print_error "Nginx is not responding on port 80"
    print_status "Checking logs..."
    docker-compose logs nginx
fi

print_success "Deployment completed!"
echo ""
echo "🌐 Access your application:"
echo "   • Frontend: https://emini.riffyx.com"
echo "   • API: https://emini.riffyx.com/api"
echo "   • Health: https://emini.riffyx.com/api/health"
echo ""
echo "📊 Service Status:"
docker-compose ps
echo ""
echo "📝 Useful commands:"
echo "   • View logs: docker-compose logs -f"
echo "   • Stop services: docker-compose down"
echo "   • Restart services: docker-compose restart"
echo "   • Update services: docker-compose pull && docker-compose up -d"
echo ""
print_warning "Remember to:"
echo "   1. Configure your DNS to point emini.riffyx.com to this server"
echo "   2. Replace self-signed certificates with real ones for production"
echo "   3. Configure firewall to allow ports 80 and 443"
echo "   4. Set up proper SSL certificates (Let's Encrypt recommended)"