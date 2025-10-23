# EminiPlayer RAG Service - Setup Guide

This guide will help you set up the EminiPlayer RAG service for your own document collection.

## Prerequisites

- Docker with GPU support (nvidia-docker2)
- NVIDIA GPU with CUDA 12.x support (6-8GB VRAM recommended for videos)
- Ollama running locally on host (default: http://localhost:11434)
- Your document collection (PDFs, videos, Excel, Word, text files)

## Initial Setup

### 1. Clone and Configure

```bash
# Clone the repository
git clone <your-repo-url>
cd EminiPlayer

# Copy the environment template
cp .env.template .env

# Edit the environment file
nano .env
```

### 2. Configure Environment Variables

Edit your `.env` file with the following key settings:

```bash
# REQUIRED: Set your documents directory
DOCUMENTS_DIR=/path/to/your/documents

# OPTIONAL: Customize other paths
OUTPUT_DIR=./outputs
CHROMA_DIR=./chroma_data

# OPTIONAL: Adjust Ollama settings
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1

# OPTIONAL: Tune retrieval parameters
BM25_TOP_K=200
EMBEDDING_TOP_K=100
RERANK_TOP_K=10
MIN_SIMILARITY_THRESHOLD=0.3
```

### 3. Install Ollama

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Pull required models
ollama pull llama3.1
ollama pull llama3.1:8b
ollama pull gpt-oss:20b
ollama pull llama3.2:3b
```

### 4. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the service
docker-compose up -d

# Check logs
docker-compose logs -f
```

## Document Organization

### Recommended Structure

Organize your documents in a clear folder structure:

```
/path/to/your/documents/
├── PDFs/
│   ├── Strategy_Guides/
│   ├── Answer_Keys/
│   └── Drills/
├── Videos/
│   ├── Training_Sessions/
│   └── Webinars/
├── Excel/
│   └── Spreadsheets/
└── Word/
    └── Documents/
```

### Supported File Types

- **PDFs**: Strategy guides, answer keys, drills, exercises
- **Videos**: Training sessions, webinars, tutorials (MP4, AVI, MOV)
- **Excel**: Spreadsheets with data, formulas, comments
- **Word**: Documents with structure, tables, headings
- **Text**: Plain text files

## Security Considerations

### Environment Variables

- **Never commit `.env` files** - they're in `.gitignore`
- **Use `.env.template`** as a reference for required variables
- **Set appropriate file permissions** on your `.env` file: `chmod 600 .env`

### Document Access

- The service mounts your documents directory as **read-only**
- Only the configured `DOCUMENTS_DIR` is accessible to the container
- Vector database and outputs are stored in Docker volumes

### Network Security

- The service runs on `localhost:8001` by default
- No external network access required for core functionality
- Ollama connection is local-only

## Troubleshooting

### Common Issues

1. **GPU not detected**
   ```bash
   # Test GPU access
   docker run --rm --gpus all nvidia/cuda:12.1.0-base nvidia-smi
   ```

2. **Ollama connection failed**
   ```bash
   # Check if Ollama is running
   curl http://localhost:11434/api/tags
   ```

3. **Permission denied on documents**
   ```bash
   # Check directory permissions
   ls -la /path/to/your/documents
   ```

4. **Out of memory during processing**
   - Reduce `WHISPER_MODEL_SIZE` to `tiny` or `base`
   - Process fewer files at once
   - Increase system RAM or use smaller models

### Logs and Monitoring

```bash
# Check service status
./check_status.sh

# View detailed logs
docker-compose logs -f rag-service

# Check database stats
curl -s http://localhost:8001/stats | jq
```

## Performance Tuning

### For Large Document Collections

- Increase `BM25_TOP_K` and `EMBEDDING_TOP_K` for better recall
- Adjust `MIN_SIMILARITY_THRESHOLD` to filter noise
- Use larger models for better quality (requires more VRAM)

### For Faster Processing

- Use smaller Whisper models (`tiny`, `base`)
- Reduce `VIDEO_FRAME_INTERVAL` for fewer keyframes
- Process documents in batches

## Next Steps

1. **Ingest your documents**: `curl -X POST http://localhost:8000/ingest`
2. **Test queries**: Use the interactive docs at `http://localhost:8000/docs`
3. **Monitor progress**: Use `./check_status.sh` to track ingestion
4. **Check outputs**: Review generated transcripts and metadata in `outputs/`

## Support

- Check the main `README.md` for detailed API documentation
- Review `QUICKSTART.md` for rapid deployment
- See `AI_ENRICHMENT_GUIDE.md` for advanced features
