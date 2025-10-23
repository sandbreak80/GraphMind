# EminiPlayer Architecture

## Overview

EminiPlayer is a comprehensive RAG (Retrieval-Augmented Generation) system designed for trading and financial analysis. The system combines document knowledge, web search, and personal notes (Obsidian) to provide intelligent responses to user queries.

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (Next.js)     │    │   (FastAPI)     │    │   Services      │
├─────────────────┤    ├─────────────────┤    ├─────────────────┤
│ • React UI      │    │ • RAG Service   │    │ • Ollama LLM    │
│ • Chat Interface│◄──►│ • Auth System   │◄──►│ • SearXNG       │
│ • Settings      │    │ • Memory System │    │ • Obsidian      │
│ • API Routes    │    │ • Web Search    │    │ • Vector DB     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Components

### Frontend (Next.js)
- **Location**: `frontend/`
- **Port**: 3001 (internal), 3000 (external via Cloudflare)
- **Features**:
  - React-based chat interface
  - Multiple chat modes (RAG, Web, Obsidian, Research)
  - User authentication
  - Settings management
  - API proxy routes

### Backend (FastAPI)
- **Location**: `app/`
- **Port**: 8000 (internal Docker network)
- **Features**:
  - RAG retrieval system
  - Web search integration
  - Obsidian MCP client
  - User authentication (JWT)
  - Memory system
  - Research engine

### External Services
- **Ollama**: Local LLM inference
- **SearXNG**: Web search engine
- **Obsidian**: Personal knowledge base
- **ChromaDB**: Vector database

## Data Flow

### Chat Modes

1. **RAG Only** (`/ask`)
   - Sources: Documents only (PDF, video transcripts, LLM processed)
   - Flow: Query → Document Retrieval → LLM Generation → Response

2. **Web Search Only** (`/ask-enhanced`)
   - Sources: Web search results only
   - Flow: Query → Web Search → LLM Generation → Response

3. **Obsidian Only** (`/ask-obsidian`)
   - Sources: Personal notes only
   - Flow: Query → Obsidian Search → LLM Generation → Response

4. **Comprehensive Research** (`/ask-research`)
   - Sources: Documents + Web search
   - Flow: Query → Document Retrieval + Web Search → Combined Context → LLM Generation → Response

## Deployment Architecture

### Production Setup
- **Frontend**: Exposed via Cloudflare Tunnel
- **Backend**: Internal Docker network only
- **Communication**: Frontend → Next.js API Routes → Backend

### Docker Services
```yaml
services:
  rag-service:    # Backend API
  frontend:       # Next.js frontend
  ollama:         # LLM inference
```

## Security

- **Authentication**: JWT tokens
- **API Security**: Internal network only
- **Data Privacy**: Local processing, no external data sharing
- **CORS**: Configured for frontend-backend communication

## Performance

- **Response Times**: Varies by mode (documented in metrics)
- **Caching**: Vector embeddings cached
- **Scalability**: Horizontal scaling via Docker
- **Memory**: User session memory with persistence

## Monitoring

- **Health Checks**: `/health` endpoint
- **Metrics**: Response times, source counts
- **Logging**: Structured logging throughout
- **Error Handling**: Comprehensive error responses