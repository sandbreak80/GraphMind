# GraphMind - Open RAG Framework

GraphMind is an advanced open-source Retrieval-Augmented Generation (RAG) framework designed for intelligent knowledge retrieval and research.

## Key Features

### 1. Multi-Source Intelligence
- **RAG Mode**: Search through your ingested document knowledge base
- **Web Search Mode**: Real-time web search using SearXNG
- **Obsidian Mode**: Integration with personal Obsidian knowledge vaults
- **Comprehensive Research**: Combines all sources for deep research

### 2. Advanced Retrieval System
- **BM25**: Keyword-based retrieval for precise matching
- **Dense Embeddings**: Semantic search using sentence transformers
- **Cross-Encoder Reranking**: BAAI/bge-reranker-large for relevance scoring
- **Hybrid Approach**: Combines multiple retrieval methods

### 3. Multi-Format Document Support
- PDF documents with OCR support
- Video transcription using Whisper
- Excel, Word, PowerPoint files
- Text, Markdown, HTML, and more
- 80+ file formats supported

### 4. LLM Integration
- Ollama for local LLM inference
- Multiple model support (DeepSeek, Llama, etc.)
- Configurable parameters (temperature, top_k, max_tokens)
- Model auto-selection based on query complexity

### 5. Modern Architecture
- Docker containerized deployment
- Nginx reverse proxy
- ChromaDB vector database
- Redis caching for performance
- Prometheus & Grafana monitoring

## Technical Stack

- **Frontend**: Next.js 14, React, Tailwind CSS, TypeScript
- **Backend**: FastAPI, Python 3.10+
- **Vector Database**: ChromaDB
- **Search Engine**: SearXNG (privacy-respecting)
- **LLM Runtime**: Ollama
- **Caching**: Redis
- **Monitoring**: Prometheus + Grafana

## Use Cases

1. **Research Platform**: Combine documents, notes, and web search for comprehensive research
2. **Knowledge Management**: Index and search through large document collections
3. **Personal AI Assistant**: Integrate with your Obsidian notes for personalized responses
4. **Information Retrieval**: Fast and accurate document search with citations

## Performance

- Response times: 2-10 seconds depending on mode
- Concurrent request handling
- GPU acceleration support for Whisper and embeddings
- Efficient caching layer

## Security

- JWT-based authentication
- Zero-trust internal networking
- Only frontend exposed externally
- All backend services internal-only
- Rate limiting and request validation

