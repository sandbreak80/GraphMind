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

# Collection Configuration
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "tradingai_docs")

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

# High-Performance Retrieval Configuration (100GB RAM + 24 CPU cores + 2x GPU)
# Optimized settings for balanced performance and recall
BM25_TOP_K = int(os.getenv("BM25_TOP_K", "30"))          # Balanced for high-end hardware
EMBEDDING_TOP_K = int(os.getenv("EMBEDDING_TOP_K", "30"))  # Balanced for high-end hardware
RERANK_TOP_K = int(os.getenv("RERANK_TOP_K", "8"))      # Balanced for comprehensive results

# Memory-Intensive Caching Configuration
ENABLE_AGGRESSIVE_CACHING = os.getenv("ENABLE_AGGRESSIVE_CACHING", "true").lower() == "true"
CACHE_EMBEDDINGS = os.getenv("CACHE_EMBEDDINGS", "true").lower() == "true"
CACHE_BM25_INDEX = os.getenv("CACHE_BM25_INDEX", "true").lower() == "true"
CACHE_RERANKER = os.getenv("CACHE_RERANKER", "true").lower() == "true"

# Parallel Processing Configuration (24 cores)
MAX_WORKERS = int(os.getenv("MAX_WORKERS", "20"))  # Leave 4 cores for system
BATCH_SIZE = int(os.getenv("BATCH_SIZE", "32"))    # Large batches for parallel processing
EMBEDDING_BATCH_SIZE = int(os.getenv("EMBEDDING_BATCH_SIZE", "64"))  # Parallel embedding generation

# Recall optimization
MIN_SIMILARITY_THRESHOLD = float(os.getenv("MIN_SIMILARITY_THRESHOLD", "0.3"))  # Filter noise

# Chunking
CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

# Video Processing
VIDEO_FRAME_INTERVAL = int(os.getenv("VIDEO_FRAME_INTERVAL", "30"))  # Extract frame every N seconds
WHISPER_MODEL_SIZE = os.getenv("WHISPER_MODEL_SIZE", "base")  # tiny, base, small, medium, large

# AI Enrichment - Production Trading Bot Configuration
AI_ENRICHMENT_ENABLED = os.getenv("AI_ENRICHMENT_ENABLED", "true").lower() == "true"
VIDEO_ENRICHMENT_MODEL = os.getenv("VIDEO_ENRICHMENT_MODEL", "qwen2.5-coder:14b")  # Best for trading analysis
PDF_ENRICHMENT_MODEL = os.getenv("PDF_ENRICHMENT_MODEL", "gpt-oss:20b")  # Most capable for complex analysis
CHUNK_ENRICHMENT_MODEL = os.getenv("CHUNK_ENRICHMENT_MODEL", "llama3.1:latest")  # Balanced performance

# High-Performance LLM Configuration (100GB RAM + 24 CPU cores)
PRODUCTION_LLM_MODEL = os.getenv("PRODUCTION_LLM_MODEL", "llama3.1:latest")  # Best for RAG and strategy evaluation
RESEARCH_LLM_MODEL = os.getenv("RESEARCH_LLM_MODEL", "gpt-oss:20b")  # Best for research and analysis
MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8000"))  # Massive responses with 100GB RAM
TEMPERATURE = float(os.getenv("TEMPERATURE", "0.1"))  # Lower for consistent trading rules
RESEARCH_TEMPERATURE = float(os.getenv("RESEARCH_TEMPERATURE", "0.3"))  # Higher for creative research
TOP_P = float(os.getenv("TOP_P", "0.9"))  # Focused responses
TIMEOUT = int(os.getenv("LLM_TIMEOUT", "300"))  # Extended timeout for complex analysis

# Ollama Performance Optimization
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "32768"))  # Large context window
OLLAMA_NUM_GPU = int(os.getenv("OLLAMA_NUM_GPU", "2"))  # Use both GPUs
OLLAMA_NUM_THREAD = int(os.getenv("OLLAMA_NUM_THREAD", "20"))  # Use most CPU cores
OLLAMA_NUM_BATCH = int(os.getenv("OLLAMA_NUM_BATCH", "512"))  # Large batch processing
OLLAMA_NUM_PREDICT = int(os.getenv("OLLAMA_NUM_PREDICT", "8000"))  # Max tokens
OLLAMA_TOP_K = int(os.getenv("OLLAMA_TOP_K", "40"))  # More diverse sampling
OLLAMA_TOP_P = float(os.getenv("OLLAMA_TOP_P", "0.9"))  # Focused responses
OLLAMA_REPEAT_PENALTY = float(os.getenv("OLLAMA_REPEAT_PENALTY", "1.1"))  # Reduce repetition
OLLAMA_TEMPERATURE = float(os.getenv("OLLAMA_TEMPERATURE", "0.1"))  # Consistent responses
