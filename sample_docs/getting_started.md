# Getting Started with GraphMind

## Quick Start

### 1. Deploy with Docker Compose

```bash
docker compose -f docker-compose.graphmind.yml up -d
```

### 2. Access the Interface

Open your browser to:
- Local: `http://localhost` or `http://localhost:3000`
- Production: Your configured domain

### 3. Login

Default credentials:
- Username: `admin`
- Password: `admin123`

**⚠️ Change these credentials immediately in production!**

### 4. Upload Documents

1. Navigate to "Documents" in the sidebar
2. Click "Upload Documents"
3. Select your PDF, TXT, or other supported files
4. Click "Ingest All" to process documents

### 5. Start Chatting

Choose your mode:
- **RAG Only**: Search your uploaded documents
- **Web Search Only**: Real-time web information
- **Obsidian Only**: Search your personal notes (requires configuration)
- **Comprehensive Research**: Deep research combining all sources

## Configuration

### Environment Variables

Key variables in `.env`:

```bash
# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
FRONTEND_DOMAIN=localhost

# Backend
OLLAMA_BASE_URL=http://ollama:11434
CHROMA_URL=http://chromadb:8000
REDIS_URL=redis://redis:6379
SEARXNG_URL=http://searxng:8080

# Security
JWT_SECRET_KEY=your-secret-key-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
```

### Ollama Models

The system auto-downloads these models:
- `deepseek-r1:latest` - Latest DeepSeek model
- `deepseek-r1:14b` - 14B parameter model
- `deepseek-r1:7b` - 7B parameter model
- `llama3.2:latest` - Latest Llama 3.2
- `llama3.1:latest` - Latest Llama 3.1

### Obsidian Integration

1. Install the "Local REST API" plugin in Obsidian
2. Configure the API in Obsidian settings
3. Go to GraphMind Settings → Obsidian Integration
4. Enter your Obsidian API URL and key
5. Test the connection

## Tips & Tricks

### Document Ingestion

- **Force Reindex**: Use this if you need to completely rebuild the index
- **Append Mode**: Default mode that adds new documents without removing existing ones
- **Supported Formats**: PDF, TXT, MD, DOCX, XLSX, PPTX, HTML, CSV, JSON, and 70+ more

### Search Modes

- **RAG Mode**: Best for precise answers from your documents
- **Web Search**: Best for current events and real-time information
- **Obsidian Mode**: Best for personal knowledge and notes
- **Research Mode**: Best for comprehensive analysis requiring multiple sources

### Performance Tuning

In the settings, you can adjust:
- `bm25_top_k`: Number of keyword search results (default: 30)
- `embedding_top_k`: Number of semantic search results (default: 30)
- `rerank_top_k`: Final number of sources after reranking (default: 8)
- `web_search_results`: Number of web search results (default: 6)
- `web_pages_to_parse`: Number of web pages to parse (default: 4)

Higher values = more comprehensive but slower responses.

## Troubleshooting

### No response from chat
- Check that Ollama container is running: `docker ps | grep ollama`
- Check Ollama logs: `docker logs graphmind-ollama`
- Verify models are downloaded: `docker exec graphmind-ollama ollama list`

### No documents found
- Verify documents were uploaded to `/data/documents/`
- Run ingestion: Documents page → "Ingest All"
- Check ChromaDB: `docker logs graphmind-chromadb`

### Slow responses
- Reduce retrieval parameters in settings
- Check system resources (RAM, CPU, GPU)
- Monitor with Grafana dashboard

### Authentication errors
- Verify JWT secret is set in `.env`
- Check token expiration settings
- Clear browser cache and re-login

## Next Steps

1. Upload your document collection
2. Experiment with different modes
3. Configure Obsidian integration (optional)
4. Customize system prompts
5. Monitor performance with Grafana

For more information, see the documentation in `/docs/`.

