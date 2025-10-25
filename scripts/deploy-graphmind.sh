#!/bin/bash
# GraphMind Deployment Script
# Deploys the complete GraphMind stack with all services

set -e

echo "🧠 Deploying GraphMind Complete Stack..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker &> /dev/null || ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p documents memory config/domains obsidian_vault
mkdir -p nginx/ssl monitoring/prometheus monitoring/grafana/dashboards
mkdir -p monitoring/grafana/provisioning/dashboards
mkdir -p monitoring/grafana/provisioning/datasources

# Set up environment
echo "⚙️ Setting up environment..."
if [ ! -f .env ]; then
    cp env.graphmind .env
    echo "✅ Created .env file from template"
fi

# Generate SSL certificates (self-signed for development)
echo "🔐 Generating SSL certificates..."
if [ ! -f nginx/ssl/cert.pem ]; then
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=US/ST=State/L=City/O=Organization/CN=emini.riffyx.com"
    echo "✅ Generated self-signed SSL certificates"
fi

# Create Prometheus configuration
echo "📊 Setting up Prometheus..."
cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'graphmind-rag'
    static_configs:
      - targets: ['graphmind-rag:8000']
  
  - job_name: 'searxng'
    static_configs:
      - targets: ['searxng:8080']
  
  - job_name: 'ollama'
    static_configs:
      - targets: ['ollama:11434']
EOF

# Create Grafana datasource configuration
echo "📈 Setting up Grafana..."
cat > monitoring/grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

# Pull required images
echo "🐳 Pulling Docker images..."
docker compose -f docker-compose.graphmind.yml pull

# Start services
echo "🚀 Starting GraphMind services..."
docker compose -f docker-compose.graphmind.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
services=("graphmind-rag" "graphmind-frontend" "chromadb" "redis" "ollama" "searxng" "obsidian-mcp" "docker-mcp" "filesystem-mcp")

for service in "${services[@]}"; do
    if docker compose -f docker-compose.graphmind.yml ps | grep -q "$service.*Up"; then
        echo "✅ $service is running"
    else
        echo "❌ $service is not running"
    fi
done

echo ""
echo "🎉 GraphMind deployment complete!"
echo ""

# Run deployment validation tests
echo "🧪 Running deployment validation tests..."
echo "========================================"

if [ -f "scripts/validate-deployment.sh" ]; then
    if bash scripts/validate-deployment.sh; then
        echo ""
        echo "✅ Deployment validation tests PASSED!"
    else
        echo ""
        echo "❌ Deployment validation tests FAILED!"
        echo "Please check the test output above for issues."
        echo ""
        echo "🔧 Troubleshooting:"
        echo "  - Check Docker services: docker compose -f docker-compose.graphmind.yml ps"
        echo "  - Check logs: docker compose -f docker-compose.graphmind.yml logs"
        echo "  - Restart services: docker compose -f docker-compose.graphmind.yml restart"
        echo ""
        echo "⚠️ Some functionality may not be working correctly."
    fi
else
    echo "⚠️ Deployment validation script not found. Skipping tests."
fi

echo ""
echo "🌐 Public URLs:"
echo "  - Frontend: https://emini.riffyx.com"
echo ""
echo "🔒 Internal Services (NOT exposed externally):"
echo "  - GraphMind RAG API: Internal only"
echo "  - ChromaDB: Internal only"
echo "  - Redis: Internal only"
echo "  - Ollama: Internal only"
echo "  - SearXNG: Internal only"
echo "  - MCP Servers: Internal only"
echo "  - Prometheus: Internal only"
echo "  - Grafana: Internal only"
echo ""
echo "📋 Management Commands:"
echo "  - View logs: docker compose -f docker-compose.graphmind.yml logs -f"
echo "  - Stop services: docker compose -f docker-compose.graphmind.yml down"
echo "  - Restart services: docker compose -f docker-compose.graphmind.yml restart"
echo "  - Update services: docker compose -f docker-compose.graphmind.yml pull && docker compose -f docker-compose.graphmind.yml up -d"
echo "  - Run tests: bash scripts/validate-deployment.sh"
echo "  - Full test suite: bash scripts/run-deployment-tests.sh"
echo ""
echo "📝 Note: This script requires Docker Compose v2.0+ (uses 'docker compose' command)"
echo ""
echo "🔧 Next Steps:"
echo "  1. Add documents to ./documents directory"
echo "  2. Set up Obsidian vault in ./obsidian_vault directory"
echo "  3. Configure domain settings in .env file"
echo "  4. Access the frontend at https://emini.riffyx.com"
echo "  5. Run comprehensive tests: bash scripts/run-deployment-tests.sh"
