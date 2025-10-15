# EminiPlayer RAG Service

A production-ready Dockerized RAG (Retrieval-Augmented Generation) service for ingesting and querying **all EminiPlayer content** including PDFs, videos, Excel, and Word documents with GPU acceleration.

## Features

### 📚 Multi-Format Knowledge Extraction
- **PDF Processing** (68 files): Docling with OCR fallback (OCRmyPDF + Tesseract) and PyMuPDF final fallback
- **Video Transcription** (23 files): GPU-accelerated Whisper for audio + keyframe extraction for visual analysis
- **Excel Spreadsheets** (2 files): Data, formulas, comments across all sheets
- **Word Documents** (1 file): Structure-aware text, tables, headings
- **Text Files**: Plain text chunking

### 🎯 Advanced Retrieval & Analysis
- **Structure-Aware Chunking**: Preserves document structure (headings, sections, timestamps)
- **Hybrid Retrieval**: BM25 prefilter → Embedding KNN → Cross-encoder reranking
- **Local LLM Integration**: Connects to local Ollama for offline operation
- **YAML Spec Extraction**: Extract structured trading strategy specifications
- **GPU Acceleration**: CUDA-enabled for embeddings, reranking, and Whisper transcription
- **Persistent Vector Store**: Chroma with Docker volume persistence

**Total Coverage**: 97 files, ~3.8GB, ~1000+ pages of trading knowledge

## Architecture

```
┌──────────────────────────────────────────────────────┐
│  Input: 97 Files (PDFs, Videos, Excel, Word, Text)  │
└──────────────────┬───────────────────────────────────┘
                   │
        ┌──────────┴──────────┐
        │  Smart File Router  │
        └──────────┬──────────┘
                   │
    ┌──────────────┼──────────────┐
    │              │              │
    ▼              ▼              ▼
┌───────┐    ┌──────────┐   ┌─────────┐
│  PDF  │    │  Video   │   │ Office  │
│Docling│    │ Whisper  │   │ pandas/ │
│ +OCR  │    │+Frames   │   │  docx   │
└───┬───┘    └────┬─────┘   └────┬────┘
    │             │              │
    └─────────────┼──────────────┘
                  │
          ┌───────▼────────┐
          │ Structure-Aware│
          │    Chunking    │
          └───────┬────────┘
                  │
          ┌───────▼────────┐
          │ Chroma VectorDB│
          │ bge-m3 embeddings
          └───────┬────────┘
                  │
          ┌───────▼────────┐
          │ Hybrid Retrieval│
          │ BM25→KNN→Rerank│
          └───────┬────────┘
                  │
          ┌───────▼────────┐
          │  Ollama (Local)│
          │  QA + Spec Gen │
          └────────────────┘
```

## Prerequisites

- Docker with GPU support (nvidia-docker2)
- NVIDIA GPU with CUDA 12.x support (6-8GB VRAM recommended for videos)
- Ollama running locally on host (default: http://localhost:11434)
- Documents directory configured via `DOCUMENTS_DIR` environment variable (see `.env.template`)

> 📋 **New to the project?** See [SETUP.md](SETUP.md) for detailed setup instructions.
> 🔒 **Security concerns?** Review [SECURITY.md](SECURITY.md) for security best practices.

## Quick Start

### 1. Setup Environment

```bash
# Copy the environment template
cp .env.template .env

# Edit .env file with your configuration
# At minimum, set DOCUMENTS_DIR to your document collection path
nano .env
```

### 2. Install Ollama (if not already installed)

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3.1
```

### 3. Build and Run

```bash
# Build the Docker image
docker-compose build

# Start the service
docker-compose up -d

# Check logs
docker-compose logs -f
```

The service will be available at `http://localhost:8000`

### 4. Ingest All Content (PDFs, Videos, Excel, Word, Text)

```bash
curl -X POST http://localhost:8000/ingest \
  -H "Content-Type: application/json" \
  -d '{"force_reindex": false}'
```

**⏱️ Processing Time**: 3-4 hours first run (23 videos with transcription + frame extraction)

Response:
```json
{
  "status": "success",
  "processed_files": 97,
  "total_chunks": 8500,
  "message": "Successfully ingested 97 files"
}
```

**What's being processed**:
- 68 PDFs → Docling + OCR fallback
- 23 Videos → Whisper transcription + keyframe extraction
- 2 Excel files → Data + formulas + comments
- 1 Word doc → Structure-aware text extraction
- 1 Text file → Simple chunking

### 4. Ask Questions (All Formats Searchable!)

**Query PDFs**:
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are the entry rules for the momentum breakout strategy?",
    "mode": "qa",
    "top_k": 5
  }'
```

**Query Videos** (with timestamps!):
```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What did the instructor explain about momentum in the BootCamp videos?",
    "mode": "qa",
    "top_k": 10
  }'
```

Response includes answer with citations:
```json
{
  "query": "...",
  "answer": "In the BootCamp session, the instructor explained...",
  "citations": [
    {
      "text": "[00:15:30 - 00:16:45] The key is to identify momentum shifts...",
      "doc_id": "Mid",
      "page": null,
      "section": "Video @ 00:15:30 - 00:16:45",
      "score": 0.92
    },
    {
      "text": "...",
      "doc_id": "momentum_strategy",
      "page": 12,
      "section": "Entry Rules",
      "score": 0.89
    }
  ],
  "mode": "qa"
}
```

### 5. Extract Strategy Spec

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Extract the opening range breakout strategy",
    "mode": "spec",
    "top_k": 10
  }'
```

Response:
```json
{
  "query": "...",
  "answer": "Strategy spec extracted and saved to /workspace/outputs/strategy_spec_...",
  "citations": [...],
  "mode": "spec",
  "spec_file": "/workspace/outputs/strategy_spec_opening_range_20251014_120530.yaml"
}
```

## API Endpoints

### `GET /`
Health check endpoint.

### `POST /ingest`
Ingest all PDFs from the mounted directory.

**Request Body:**
```json
{
  "force_reindex": false
}
```

### `POST /ask`
Answer questions or extract specs.

**Request Body:**
```json
{
  "query": "Your question here",
  "mode": "qa",  // "qa" or "spec"
  "top_k": 5
}
```

### `GET /stats`
Get database statistics.

## Configuration

Environment variables in `docker-compose.yml`:

```yaml
environment:
  # LLM
  - OLLAMA_BASE_URL=http://host.docker.internal:11434
  - OLLAMA_MODEL=llama3.1
  
  # Video Processing
  - WHISPER_MODEL_SIZE=base              # tiny, base, small, medium, large
  - VIDEO_FRAME_INTERVAL=30              # Extract keyframe every N seconds
  
  # GPU
  - CUDA_VISIBLE_DEVICES=0
```

**Whisper Model Sizes**:
- `tiny` - Fastest, ~1GB VRAM, good quality
- `base` - **Default**, balanced speed/quality
- `small` - Better accuracy, ~2GB VRAM
- `medium` - High accuracy, ~5GB VRAM
- `large` - Best accuracy, ~10GB VRAM

## Volume Mounts

- `${DOCUMENTS_DIR:-./documents}` → `/workspace/pdfs` (read-only, your document files)
- `chroma-data` → `/workspace/chroma_db` (persistent vector store)
- `${OUTPUT_DIR:-./outputs}` → `/workspace/outputs` (transcripts, frames, specs, markdown exports)

**Check outputs after ingestion**:
```bash
ls -lh outputs/                    # Transcripts and markdown exports
ls -lh outputs/frames/             # Extracted video keyframes
```

## Models Used

- **Embeddings**: BAAI/bge-m3 (multilingual, 1024-dim)
- **Reranker**: BAAI/bge-reranker-large (cross-encoder)
- **LLM**: Ollama (configurable model, default llama3.1)

## Retrieval Pipeline

1. **BM25 Prefilter** (top 50): Fast keyword-based retrieval
2. **Embedding KNN** (top 20): Semantic similarity search
3. **Reranking** (top 5): Cross-encoder for final ranking

## Chunking Strategy

- Structure-aware chunking preserving:
  - Headings and section titles
  - Page numbers
  - Document IDs
- Chunk size: 800 chars
- Overlap: 100 chars

## Troubleshooting

### GPU Not Detected
```bash
# Check NVIDIA runtime
docker run --rm --gpus all nvidia/cuda:12.1.0-base nvidia-smi
```

### Ollama Connection Issues
```bash
# Test from container
docker exec -it emini-rag curl http://host.docker.internal:11434/api/tags
```

### Video Transcription Slow or Out of Memory
```bash
# Reduce Whisper model size
# In docker-compose.yml, set:
- WHISPER_MODEL_SIZE=tiny

# Or reduce frame extraction frequency
- VIDEO_FRAME_INTERVAL=60
```

### Ingestion Failures
Check logs for specific file failures:
```bash
docker-compose logs | grep -E "Failed|✗"

# Check what processed successfully
docker-compose logs | grep "✓"
```

### "No documents found" when querying
Make sure ingestion completed:
```bash
curl -s http://localhost:8000/stats | jq
# Should show total_documents > 0
```

## Development

### Local Development (without Docker)

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OLLAMA_BASE_URL=http://localhost:11434
export OLLAMA_MODEL=llama3.1

# Run service
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Code Structure

```
.
├── app/
│   ├── main.py                # FastAPI application (~120 LOC)
│   ├── config.py              # Configuration (~30 LOC)
│   ├── models.py              # Pydantic models (~70 LOC)
│   ├── ingest.py              # Multi-format ingestion (~250 LOC)
│   ├── document_processor.py  # Excel, Word, Text (~200 LOC)
│   ├── video_processor.py     # Whisper + frames (~250 LOC)
│   ├── retrieval.py           # Hybrid retrieval (~260 LOC)
│   └── spec_extraction.py     # YAML spec extraction (~200 LOC)
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── README.md
└── MULTIFORMAT_GUIDE.md       # Detailed multi-format docs
```

Total app code: ~1380 LOC

## Performance

### Ingestion Times
- **PDFs**: ~2-5 seconds each (5-60s with OCR)
- **Videos**: ~5-15 minutes each (transcription + frames)
- **Excel/Word**: ~2-5 seconds each
- **Total (97 files)**: 3-4 hours first run (includes Whisper model download)

### Query Performance
- **Query**: ~1-3 seconds (retrieval + LLM generation)
- **Spec Extraction**: ~3-5 seconds (more context retrieved)

### Resource Usage
- **GPU Memory**: 
  - Idle: ~2GB
  - PDF Ingestion: ~4-6GB
  - Video Transcription: ~6-8GB
- **RAM**: 8-16GB
- **Disk**: ~3.8GB input + ~1-2GB outputs (transcripts, frames)

## License

MIT

## Support

For issues or questions, check the logs:
```bash
docker-compose logs -f rag-service
```
