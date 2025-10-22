#!/bin/bash

# Simple deployment script for emini.riffyx.com
# Assumes domain already points to port 8001

set -e

echo "🚀 Deploying EminiPlayer RAG Frontend..."

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

# Use docker compose (newer) or docker-compose (older)
if command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    DOCKER_COMPOSE="docker compose"
fi

print_status "Building and starting services..."

# Stop existing containers
print_status "Stopping existing containers..."
$DOCKER_COMPOSE down 2>/dev/null || true

# Build and start services
print_status "Building Docker images..."
$DOCKER_COMPOSE build --no-cache

print_status "Starting services..."
$DOCKER_COMPOSE up -d

# Wait for services to be ready
print_status "Waiting for services to start..."
sleep 30

# Check if services are running
print_status "Checking service health..."

# Check RAG service
if curl -s https://emini.riffyx.com/health > /dev/null; then
    print_success "RAG service is running on https://emini.riffyx.com"
else
    print_error "RAG service is not responding on https://emini.riffyx.com"
    print_status "Checking logs..."
    $DOCKER_COMPOSE logs rag-service
fi

# Check frontend
if curl -s http://localhost:3001 > /dev/null; then
    print_success "Frontend is running on port 3001"
else
    print_error "Frontend is not responding on port 3001"
    print_status "Checking logs..."
    $DOCKER_COMPOSE logs frontend
fi

print_success "Deployment completed!"
echo ""
echo "🌐 Access your application:"
echo "   • Backend API: https://emini.riffyx.com"
echo "   • Frontend: http://localhost:3001 (for development)"
echo "   • Health: https://emini.riffyx.com/health"
echo ""
echo "📊 Service Status:"
$DOCKER_COMPOSE ps
echo ""
echo "📝 Next steps:"
echo "   1. Configure your reverse proxy to route frontend traffic to port 3001"
echo "   2. Or access the frontend directly at http://localhost:3001"
echo "   3. The backend API is already accessible at https://emini.riffyx.com"
echo ""
print_warning "To make the frontend accessible via your domain:"
echo "   - Configure your reverse proxy to serve the frontend on a subdomain or path"
echo "   - Or run the frontend on a different port and proxy it through your existing setup"