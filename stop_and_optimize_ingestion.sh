#!/bin/bash

echo "🛑 Stopping current ingestion and starting optimized version..."

# Stop the current container to stop the long-running ingestion
echo "1. Stopping current RAG container..."
docker compose stop rag-service

# Wait a moment
sleep 5

# Start the container again (this will stop the current ingestion)
echo "2. Starting RAG container..."
docker compose up -d rag-service

# Wait for the container to be ready
echo "3. Waiting for container to be ready..."
sleep 30

# Check if the container is running
if docker ps | grep -q emini-rag; then
    echo "✅ Container is running"
    
    # Run the optimized ingestion
    echo "4. Running optimized ingestion (PDFs only)..."
    docker exec emini-rag python3 /workspace/app/ingest_optimized.py
    
    echo "5. Checking final status..."
    curl -s http://localhost:8001/stats | jq .
    
    echo "🎉 Optimized ingestion complete!"
    echo "   - PDFs processed quickly"
    echo "   - Videos skipped to prevent 4-hour runs"
    echo "   - System ready for testing"
else
    echo "❌ Container failed to start"
    exit 1
fi