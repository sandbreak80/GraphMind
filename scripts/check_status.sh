#!/bin/bash
# Quick status checker for ingestion

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
COMPOSE_FILE="$SCRIPT_DIR/docker-compose.yml"

echo "================================"
echo "RAG SERVICE STATUS"
echo "================================"

# Container status
echo ""
echo "Container:"
docker compose -f "$COMPOSE_FILE" ps --format "table {{.Name}}\t{{.Status}}\t{{.Ports}}"

# Database stats
echo ""
echo "Database Stats:"
curl -s http://localhost:8001/stats 2>/dev/null | jq -r 'if .error then "❌ " + .error else "✅ Documents: " + (.total_documents | tostring) + " | BM25: " + (.bm25_indexed | tostring) end'

# Recent activity (last 10 files processed)
echo ""
echo "Recent Activity (last 10):"
docker compose -f "$COMPOSE_FILE" logs --tail=200 rag-service 2>/dev/null | grep -E "✓|✗" | tail -10

# Current processing
echo ""
echo "Currently Processing:"
docker compose -f "$COMPOSE_FILE" logs --tail=5 rag-service 2>/dev/null | grep "Transcribing\|Enriching\|Processing" | tail -3

# Error count
echo ""
echo "Error Summary:"
ERRORS=$(docker compose -f "$COMPOSE_FILE" logs rag-service 2>/dev/null | grep "✗" | wc -l)
SUCCESS=$(docker compose -f "$COMPOSE_FILE" logs rag-service 2>/dev/null | grep "✓" | wc -l)
echo "  ✅ Successful: $SUCCESS"
echo "  ❌ Failed: $ERRORS"

echo ""
echo "================================"
