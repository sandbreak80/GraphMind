# Quick Start Guide

## 5-Minute Setup

### 1. Prerequisites Check

```bash
# Check Docker
docker --version

# Check NVIDIA GPU
nvidia-smi

# Check Ollama
curl http://localhost:11434/api/tags
```

### 2. Start Ollama (if needed)

```bash
# Pull a model
ollama pull llama3.1

# Keep Ollama running in background
```

### 3. Build & Launch

```bash
# Build the image
make build

# Start the service
make up

# Watch the logs
make logs
```

### 4. Ingest Your PDFs

```bash
# Trigger ingestion
make ingest

# Wait for completion (check logs)
# Processing time: ~2-5 seconds per PDF
```

### 5. Test Queries

```bash
# Test a question
make test-query

# Extract a strategy spec
make extract-spec

# Check stats
make stats
```

## Common Operations

### View Outputs
```bash
ls -lh outputs/
```

### Reingest Everything
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"force_reindex": true}'
```

### Custom Query
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "YOUR QUESTION HERE",
    "mode": "qa",
    "top_k": 5
  }' | jq
```

### Extract Specific Strategy
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Extract [STRATEGY NAME]",
    "mode": "spec",
    "top_k": 10
  }' | jq
```

## Troubleshooting

### "No documents found"
→ Run `make ingest` first

### "Connection refused" to Ollama
→ Check Ollama is running: `ollama list`

### GPU not working
→ Test: `docker run --rm --gpus all nvidia/cuda:12.1.0-base nvidia-smi`

### Slow ingestion
→ First run downloads models (~2GB), subsequent runs are faster

## File Locations

- **Documents**: `${DOCUMENTS_DIR:-./documents}` (host) → `/workspace/pdfs` (container)
- **Vector DB**: Docker volume `chroma-data`
- **Outputs**: `${OUTPUT_DIR:-./outputs}` (host) → `/workspace/outputs` (container)
- **Logs**: `docker-compose logs -f`

## API Documentation

Interactive docs: http://localhost:8000/docs (FastAPI auto-generated)

## Performance Tips

1. **First ingestion**: Allow 5-10 minutes for model downloads
2. **GPU memory**: Service uses ~4-6GB VRAM
3. **Query speed**: Typically 1-3 seconds per query
4. **Batch operations**: Ingest runs in parallel where possible

## Stopping the Service

```bash
# Stop containers
make down

# Stop and remove volumes (clean slate)
make clean
```

## Next Steps

1. Browse http://localhost:8000/docs for interactive API docs
2. Check `example_requests.sh` for more examples
3. Review `outputs/` for extracted specs
4. Monitor logs for any issues

Happy querying! 🚀
