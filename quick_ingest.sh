#!/bin/bash

echo "🚀 Quick ingestion using existing API endpoint..."
echo "   - This will use the existing ingestion system"
echo "   - Should be much faster than 4 hours"
echo "   - Will process PDFs and existing transcripts"

# Check if the API is ready
echo "1. Checking API status..."
if curl -s http://localhost:8001/health > /dev/null; then
    echo "✅ API is ready"
else
    echo "❌ API not ready, waiting..."
    sleep 10
fi

# Run ingestion via API
echo "2. Starting ingestion via API..."
curl -X POST http://localhost:8001/ingest \
  -H "Content-Type: application/json" \
  -d '{"recursive": true, "force_reindex": false}' \
  --max-time 300

echo ""
echo "3. Checking final status..."
curl -s http://localhost:8001/stats | jq .

echo ""
echo "🎉 Quick ingestion complete!"
echo "   - Used existing API endpoint"
echo "   - Should have processed documents quickly"
echo "   - Check the stats above for results"