"""Configuration for RAG service."""
import os
from pathlib import Path

# Paths - handle both container and host environments
if Path("/workspace").exists():
    # Running in container
    PDF_DIR = Path("/workspace/pdfs")
    CHROMA_DIR = Path("/workspace/chroma_db")
    OUTPUT_DIR = Path("/workspace/outputs")
else:
    # Running on host - use environment variables with fallbacks
    BASE_DIR = Path(__file__).parent.parent
    
    # Use environment variables for paths, with sensible defaults
    DOCUMENTS_DIR = os.getenv("DOCUMENTS_DIR")
    if DOCUMENTS_DIR:
        PDF_DIR = Path(DOCUMENTS_DIR)
    else:
        # Fallback to a generic documents directory
        PDF_DIR = BASE_DIR / "documents"
    
    CHROMA_DIR = Path(os.getenv("CHROMA_DIR", str(BASE_DIR / "chroma_data")))
    OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(BASE_DIR / "outputs")))

OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Ollama
if Path("/workspace").exists():
    # Running in container - use host.docker.internal
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
else:
    # Running on host - use localhost
    OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

# Embeddings
EMBEDDING_MODEL = "BAAI/bge-m3"
RERANKER_MODEL = "BAAI/bge-reranker-large"

# Retrieval Configuration
# Optimized for 90%+ recall with ~8,500 chunks
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "200"))          # Cast wider net
EMBEDDING_TOP_K = int(os.getenv("EMBEDDING_TOP_K", "100"))  # Increased for high recall
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", "10"))      # More final results

# Recall optimization
MIN_SIMILARITY_THRESHOLD = float(os.getenv("MIN_SIMILARITY_THRESHOLD", "0.3"))  # Filter noise

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# Video Processing
VIDEO_FRAME_INTERVAL = int(os.getenv("VIDEO_FRAME_INTERVAL", "30"))  # Extract frame every N seconds
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")  # tiny, base, small, medium, large

# AI Enrichment
AI_ENRICHMENT_ENABLED = os.getenv("AI_ENRICHMENT_ENABLED", "true").lower() == "true"
VIDEO_ENRICHMENT_MODEL = os.getenv("VIDEO_ENRICHMENT_MODEL", "llama3.1:8b")  # Fast + quality
PDF_ENRICHMENT_MODEL = os.getenv("PDF_ENRICHMENT_MODEL", "gpt-oss:20b")  # More capable
CHUNK_ENRICHMENT_MODEL = os.getenv("CHUNK_ENRICHMENT_MODEL", "llama3.2:3b")  # Ultra fast
