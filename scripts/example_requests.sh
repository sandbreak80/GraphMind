#!/bin/bash
# Example API requests for EminiPlayer RAG Service

BASE_URL="http://localhost:8000"

echo "=== Health Check ==="
curl -s ${BASE_URL}/ | jq

echo -e "\n=== Check Stats ==="
curl -s ${BASE_URL}/stats | jq

echo -e "\n=== Ingest PDFs ==="
curl -s -X POST ${BASE_URL}/ingest \
  -H "Content-Type: application/json" \
  -d '{"force_reindex": false}' | jq

echo -e "\n=== Ask Question (QA Mode) ==="
curl -s -X POST ${BASE_URL}/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the key indicators for momentum trading?",
    "mode": "qa",
    "top_k": 5
  }' | jq

echo -e "\n=== Extract Strategy Spec ==="
curl -s -X POST ${BASE_URL}/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Extract the opening range breakout strategy",
    "mode": "spec",
    "top_k": 10
  }' | jq

echo -e "\n=== Done ==="
