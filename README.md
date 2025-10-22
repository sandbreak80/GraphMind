# EminiPlayer - Advanced RAG Trading System

A comprehensive Retrieval-Augmented Generation (RAG) system designed for trading strategy development, featuring multi-format document processing, video transcription, web search integration, and Obsidian note integration.

## 🚀 Features

### Recent Improvements (Latest Version)
- **🧠 Intelligent Search System**: LLM-powered query generation for enhanced web search
- **Enhanced Text Input**: Large text area supporting very long prompts without truncation
- **Real-time Character Counter**: Visual feedback for long content
- **Improved UI/UX**: Better user experience with auto-resizing text areas
- **Robust Error Handling**: Graceful error handling and user feedback
- **Authentication System**: Secure JWT-based authentication
- **Source Citation Display**: Clear source attribution with relevance scores
- **Responsive Design**: Optimized for various screen sizes

### Core RAG Capabilities
- **Multi-Format Document Processing**: PDFs, Word docs, Excel files, text files
- **Video Transcription**: MP4/WEBM support with GPU-accelerated Whisper
- **LLM-Enhanced Processing**: AI-powered content enrichment and summarization
- **Hybrid Retrieval**: BM25 + Embedding search + Cross-encoder reranking
- **Vector Database**: ChromaDB with persistent storage

### Integration Features
- **🧠 Intelligent Web Search**: LLM-powered query generation for enhanced search results
- **Web Search**: SearXNG integration for real-time information
- **Obsidian Integration**: Access personal notes via MCP protocol
- **Ollama Integration**: Local LLM support with multiple models
- **Modern Web UI**: Next.js frontend with chat interface

### Performance Optimizations
- **GPU Acceleration**: NVIDIA CUDA support for embeddings and LLM
- **Batch Processing**: Optimized for high-throughput processing
- **Caching**: Aggressive caching for improved performance
- **Memory Management**: Optimized for large document collections

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   Services      │
│   Port: 3001    │    │   Port: 8001    │    │                 │
└─────────────────┘    └─────────────────┘    │ • Ollama        │
                              │                │ • SearXNG       │
                              ▼                │ • Obsidian      │
                       ┌─────────────────┐    │ • ChromaDB      │
                       │   RAG Engine    │    └─────────────────┘
                       │                 │
                       │ • Document      │
                       │   Processing    │
                       │ • Embeddings    │
                       │ • Retrieval     │
                       │ • Reranking     │
                       └─────────────────┘
```

## 📋 Prerequisites

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **RAM**: 32GB+ (100GB recommended for large datasets)
- **CPU**: 8+ cores (24 cores recommended)
- **GPU**: NVIDIA GPU with CUDA support (RTX 4070+ recommended)
- **Storage**: 100GB+ free space

### Software Requirements
- Docker & Docker Compose
- NVIDIA Container Toolkit
- Git

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/EminiPlayer.git
cd EminiPlayer
```

### 2. Configure Environment
```bash
cp .env.template .env
# Edit .env with your configuration
```

### 3. Start Services
```bash
# Start all services
docker compose up -d

# Check status
docker compose ps
```

### 4. Access the System
- **Frontend**: http://localhost:3001
- **Backend API**: http://localhost:8001
- **API Documentation**: http://localhost:8001/docs

## 📚 Documentation

### Core Components
- [Setup Guide](SETUP.md) - Detailed installation instructions
- [Frontend Setup](FRONTEND_SETUP.md) - Web interface configuration
- [Production Deployment](PRODUCTION_DEPLOYMENT.md) - Production deployment guide

### Integration Guides
- [Intelligent Search Guide](INTELLIGENT_SEARCH_GUIDE.md) - LLM-powered query generation
- [Obsidian Setup](OBSIDIAN_SETUP_GUIDE.md) - Personal notes integration
- [SearXNG Integration](OBSIDIAN_API_SETUP.md) - Web search setup

### Technical Documentation
- [System Overview](FINAL_SYSTEM_OVERVIEW.md) - Complete system architecture
- [Metadata Best Practices](METADATA_BEST_PRACTICES.md) - Data organization
- [Security Guide](SECURITY.md) - Security considerations

## 🔧 Configuration

### Environment Variables

#### Core Settings
```bash
# Collection Configuration
COLLECTION_NAME=emini_docs

# Retrieval Configuration (optimized for performance)
BM25_TOP_K=20
EMBEDDING_TOP_K=20
RERANK_TOP_K=5

# LLM Configuration
OLLAMA_BASE_URL=http://host.docker.internal:11434
OLLAMA_MODEL=qwen2.5-coder:14b
MAX_TOKENS=8000
TEMPERATURE=0.1
```

#### Integration Settings
```bash
# Web Search
SEARXNG_URL=http://192.168.50.236:8888/search

# Obsidian Integration
OBSIDIAN_API_URL=https://192.168.50.43:27124
OBSIDIAN_API_KEY=your_api_key_here
OBSIDIAN_VAULT_PATH=/workspace/obsidian_vault
```

### Docker Compose Services

#### rag-service
- **Image**: Custom Python FastAPI application
- **Port**: 8001
- **Volumes**: 
  - `./app:/workspace/app`
  - `./chroma_db:/workspace/chroma_db`
  - `./rag_docs_zone:/workspace/rag_docs_zone:ro`
  - `./obsidian_vault:/workspace/obsidian_vault:ro`

#### frontend
- **Image**: Custom Next.js application
- **Port**: 3001
- **Environment**: `NEXT_PUBLIC_API_URL=http://localhost:8001`

## 📊 Usage

### API Endpoints

#### Core RAG Endpoints
- `POST /ask` - Standard RAG query
- `POST /ask-enhanced` - Enhanced RAG with intelligent web search
- `POST /ask-obsidian` - RAG with Obsidian integration
- `POST /generate-search-queries` - Generate intelligent search queries
- `POST /ingest` - Document ingestion
- `GET /stats` - System statistics

#### Ollama Integration
- `GET /ollama/models` - List available models
- `POST /ollama/generate` - Generate text with Ollama

#### Utility Endpoints
- `GET /health` - Health check
- `GET /` - API information

### 🧠 Intelligent Search System

The system now features **LLM-powered query generation** that transforms user prompts into targeted, context-aware web searches:

#### How It Works
1. **Prompt Analysis**: LLM analyzes user intent and extracts entities
2. **Query Generation**: Creates 3-5 targeted search queries per prompt
3. **Multi-Query Search**: Executes searches across different angles
4. **Result Synthesis**: Combines and ranks results by relevance

#### Example
```
User: "What's the current market sentiment for ES futures?"

Generated Queries:
- "ES futures market sentiment today"
- "E-mini S&P 500 market analysis current conditions"  
- "ES futures trading sentiment indicators"
- "S&P 500 futures market outlook today"
```

#### Benefits
- **3-5x More Relevant Results**: Context-aware search strategies
- **Comprehensive Coverage**: Multiple search angles per question
- **Entity Recognition**: Automatically detects symbols, dates, concepts
- **Conversation Context**: Considers previous chat history

### Frontend Interface

The web interface provides:
- **Chat Interface**: Interactive conversation with the RAG system
- **Model Selection**: Choose from available Ollama models
- **Feature Toggles**: Enable/disable RAG, web search, and Obsidian
- **Settings Panel**: Configure API endpoints and preferences
- **Chat History**: Persistent conversation history
- **Enhanced Text Input**: Large text area supporting long prompts (up to 50,000 characters)
- **Real-time Character Counter**: Shows character count for long prompts
- **Auto-resize Textarea**: Automatically expands for long content
- **Source Citations**: Displays source documents with relevance scores
- **Authentication**: Secure login system with JWT tokens

## 🔍 Document Processing

### Supported Formats
- **PDFs**: Using Docling for structure-aware extraction
- **Videos**: MP4/WEBM with Whisper transcription
- **Office Docs**: Word, Excel, PowerPoint
- **Text Files**: Markdown, plain text

### Processing Pipeline
1. **Document Ingestion**: Multi-format document processing
2. **Content Extraction**: Structure-aware chunking
3. **AI Enrichment**: LLM-powered metadata generation
4. **Embedding Generation**: BAAI/bge-m3 embeddings
5. **Vector Storage**: ChromaDB with persistent storage

### Video Processing
- **Transcription**: GPU-accelerated Whisper
- **LLM Enhancement**: AI-powered content enrichment
- **Caching**: Processed transcripts cached to avoid reprocessing

## 🚀 Performance Optimization

### Retrieval Optimization
- **Hybrid Search**: BM25 + Embedding + Reranking
- **Batch Processing**: Optimized batch sizes for embeddings
- **Caching**: Aggressive caching for models and embeddings
- **Memory Management**: Efficient memory usage for large datasets

### GPU Acceleration
- **CUDA Support**: NVIDIA GPU acceleration
- **Model Optimization**: Optimized model loading and inference
- **Batch Processing**: GPU-optimized batch processing

## 🔒 Security

### Authentication
- **API Keys**: Secure API key management
- **CORS**: Configured cross-origin resource sharing
- **HTTPS**: SSL/TLS support for production

### Data Privacy
- **Local Processing**: All processing done locally
- **No External APIs**: No data sent to external services
- **Secure Storage**: Encrypted storage for sensitive data

## 🐛 Troubleshooting

### Common Issues

#### Text Input Truncation (RESOLVED)
- **Issue**: Long prompts were being cut off in the text input
- **Solution**: Enhanced text area with no character limits and auto-resize functionality
- **Status**: ✅ Fixed in latest version

#### UI Error Messages (RESOLVED)
- **Issue**: "Sorry, I encountered an error" messages appearing
- **Solution**: Improved error handling and API request formatting
- **Status**: ✅ Fixed in latest version

#### Collection Not Found
```bash
# Check collection status
curl http://localhost:8001/stats

# Recreate collection
docker exec emini-rag python3 -c "
from app.ingest import PDFIngestor
ingestor = PDFIngestor()
ingestor.chroma_client.delete_collection('emini_docs')
ingestor.collection = ingestor.chroma_client.create_collection('emini_docs')
"
```

#### Performance Issues
```bash
# Check system resources
docker stats

# Monitor logs
docker logs emini-rag --tail 50

# Restart services
docker compose restart
```

#### Frontend Issues
```bash
# Check frontend logs
docker logs emini-frontend --tail 50

# Rebuild frontend
docker compose build frontend
docker compose up -d frontend
```

### Logs and Monitoring
- **Backend Logs**: `docker logs emini-rag`
- **Frontend Logs**: `docker logs emini-frontend`
- **System Stats**: `docker stats`
- **API Health**: `curl http://localhost:8001/health`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Docling**: Advanced PDF processing
- **ChromaDB**: Vector database
- **Ollama**: Local LLM inference
- **SearXNG**: Privacy-focused search
- **Obsidian**: Personal knowledge management
- **FastAPI**: Modern Python web framework
- **Next.js**: React framework

## 📞 Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the troubleshooting guide

---

**EminiPlayer** - Building the future of AI-powered trading strategy development.