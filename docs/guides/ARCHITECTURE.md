# EminiPlayer Architecture Documentation

## Overview
EminiPlayer is a RAG (Retrieval-Augmented Generation) system for trading strategies with Obsidian integration, hosted locally using Docker containers and exposed to the internet via Cloudflare tunnels.

## Architecture

### Hosting Setup
- **Location**: Local network with Docker containers
- **Exposure**: Cloudflare tunnels expose services to production URLs
- **Backend Communication**: Docker containers communicate using internal Docker network

### Service Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Local Network                           │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   Frontend      │    │   Nginx         │    │   Backend   │ │
│  │   (Next.js)     │    │   (Reverse      │    │   (FastAPI) │ │
│  │   Port: 3000    │◄───┤   Proxy)        │◄───┤   Port: 8000│ │
│  │                 │    │   Port: 80/443  │    │             │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
│           │                       │                       │     │
│           │                       │                       │     │
│           ▼                       ▼                       ▼     │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │   Host Port     │    │   Host Port     │    │   Host Port │ │
│  │   3001:3000     │    │   80:80,443:443 │    │   8001:8000 │ │
│  └─────────────────┘    └─────────────────┘    └─────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │   Cloudflare Tunnels    │
                    │                         │
                    │  Frontend:              │
                    │  https://emini.riffyx.com/ │
                    │                         │
                    │  Backend API:           │
                    │  https://emini.riffyx.com/api/ │
                    └─────────────────────────┘
                                │
                                ▼
                    ┌─────────────────────────┐
                    │      Internet Users     │
                    │                         │
                    │  Access frontend at:    │
                    │  https://emini.riffyx.com/ │
                    │                         │
                    │  API calls go to:       │
                    │  https://emini.riffyx.com/api/ │
                    └─────────────────────────┘
```

### API Flow

1. **User Access**: Users visit `https://emini.riffyx.com/` (exposed via Cloudflare tunnel)
2. **Frontend**: Next.js application serves the UI
3. **API Calls**: Frontend makes API calls to `/api/` (relative paths)
4. **Next.js API Routes**: Next.js API routes proxy requests to `rag-service:8000`
5. **Backend**: FastAPI service processes requests and returns responses

### Docker Services

#### Frontend Service
- **Container**: `emini-frontend`
- **Image**: Next.js application
- **Port Mapping**: `3001:3000`
- **Environment**: `NEXT_PUBLIC_API_URL=http://rag-service:8000`

#### Backend Service
- **Container**: `emini-rag`
- **Image**: FastAPI application
- **Port Mapping**: `8001:8000`
- **Environment**: Various LLM and retrieval configurations

#### Nginx Service
- **Container**: `emini-nginx` (if using nginx container)
- **Port Mapping**: `80:80, 443:443`
- **Configuration**: Reverse proxy for frontend and API

### API Endpoints

#### Backend Endpoints (Internal)
- `http://rag-service:8000/health` - Health check
- `http://rag-service:8000/auth/login` - Authentication
- `http://rag-service:8000/ask` - Chat/RAG queries
- `http://rag-service:8000/ask-enhanced` - Enhanced queries
- `http://rag-service:8000/ask-obsidian` - Obsidian queries

#### Exposed Endpoints (External)
- `https://emini.riffyx.com/` - Frontend application
- `https://emini.riffyx.com/api/health` - Health check (proxied)
- `https://emini.riffyx.com/api/auth/login` - Authentication (proxied)
- `https://emini.riffyx.com/api/ask` - Chat/RAG queries (proxied)
- `https://emini.riffyx.com/api/ask-enhanced` - Enhanced queries (proxied)
- `https://emini.riffyx.com/api/ask-obsidian` - Obsidian queries (proxied)

### Frontend API Configuration

The frontend uses a centralized API URL determination system:

```typescript
export const getApiUrl = () => {
  if (typeof window !== 'undefined') {
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
      // Development: Use local backend
      return 'http://localhost:8001'
    } else {
      // Production: Use relative API paths (proxied by Next.js)
      return '/api'
    }
  }
  // Docker: Use internal service name
  return 'http://rag-service:8000'
}
```

### Next.js API Routes

The frontend uses Next.js API routes to proxy requests to the backend:

- `/api/health` → `rag-service:8000/health`
- `/api/auth/login` → `rag-service:8000/auth/login`
- `/api/auth/me` → `rag-service:8000/auth/me`
- `/api/ask` → `rag-service:8000/ask`
- `/api/ask-enhanced` → `rag-service:8000/ask-enhanced`
- `/api/ask-obsidian` → `rag-service:8000/ask-obsidian`
- `/api/ollama/models` → `rag-service:8000/ollama/models`
- `/api/generate-chat-title` → `rag-service:8000/generate-chat-title`

### Cloudflare Tunnel Configuration

The Cloudflare tunnel should be configured to expose:
- **Frontend**: Port 3001 → `https://emini.riffyx.com/`
- **Backend API**: NOT exposed (internal only)

### Common Issues

1. **API Calls Failing**: Frontend is trying to call non-existent API endpoints
2. **CORS Issues**: Backend CORS configuration needs to include the frontend domain
3. **Environment Variable Issues**: Using `NEXT_PUBLIC_` variables in server-side code
4. **Docker Network Issues**: Containers can't communicate with each other

### Troubleshooting

1. **Check Backend Health**: `curl http://localhost:8001/health`
2. **Check Frontend**: `curl http://localhost:3001`
3. **Check API Endpoint**: `curl http://localhost:3001/api/health`
4. **Check Docker Services**: `docker compose ps`
5. **Check Logs**: `docker logs emini-rag` or `docker logs emini-frontend`
6. **Test Internal Communication**: `docker exec emini-frontend wget -qO- http://rag-service:8000/health`

### Development vs Production

#### Development
- Frontend: `http://localhost:3001`
- Backend: `http://localhost:8001`
- API calls: Direct to backend

#### Production
- Frontend: `https://emini.riffyx.com/`
- Backend: Internal only (not exposed)
- API calls: Through Next.js API routes to internal backend

### Security Considerations

1. **CORS**: Backend allows requests from `https://emini.riffyx.com`
2. **Authentication**: JWT tokens for API access
3. **Rate Limiting**: Can be implemented in Next.js API routes
4. **SSL**: HTTPS termination at Cloudflare level
5. **Backend Security**: Backend is not exposed externally, only accessible through frontend

### File Structure

```
EminiPlayer/
├── app/                    # Backend FastAPI application
├── frontend/               # Next.js frontend application
├── nginx/                  # Nginx configuration
├── docker-compose.yml      # Docker services configuration
├── Dockerfile              # Backend Docker image
└── ARCHITECTURE.md         # This documentation
```

### Key Configuration Files

- `frontend/lib/api.ts` - API URL configuration
- `frontend/lib/store.ts` - State management
- `frontend/app/api/*/route.ts` - Next.js API routes (proxies to backend)
- `app/main.py` - Backend API endpoints
- `docker-compose.yml` - Service definitions

### Notes

- The backend is NOT exposed externally - only the frontend is exposed via Cloudflare tunnel
- The frontend must be accessible on port 3001 for Cloudflare tunnel
- All API calls from the frontend go through Next.js API routes
- Internal Docker communication uses service names, not localhost
- Next.js API routes act as a proxy between the frontend and backend