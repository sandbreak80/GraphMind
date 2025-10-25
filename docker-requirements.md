# 🐳 Docker Requirements - TradingAI Research Platform

## Base Images

### Backend Service
```dockerfile
FROM nvidia/cuda:12.1.0-runtime-ubuntu22.04
```
- **Purpose**: CUDA-enabled base for GPU processing
- **CUDA Version**: 12.1.0
- **OS**: Ubuntu 22.04 LTS
- **Size**: ~2.5GB

### Frontend Service
```dockerfile
FROM node:18-alpine
```
- **Purpose**: Lightweight Node.js runtime for Next.js frontend
- **Node Version**: 18.x
- **OS**: Alpine Linux
- **Size**: ~150MB

## System Dependencies

### Ubuntu Packages (Backend)
```bash
# Core Python environment
python3.10
python3-pip

# OCR and document processing
tesseract-ocr
tesseract-ocr-eng
ocrmypdf
poppler-utils

# Video/audio processing
ffmpeg
libavcodec-dev
libavformat-dev
libavutil-dev
libswscale-dev
libavdevice-dev
libavfilter-dev
libswresample-dev

# Graphics and display
libgl1-mesa-glx
libglib2.0-0
libsm6
libxext6
libxrender-dev

# Development tools
pkg-config
```

### Alpine Packages (Frontend)
```bash
# C library compatibility
libc6-compat
```

## Container Configuration

### Environment Variables
```bash
# CUDA Configuration
TORCH_CUDA_ARCH_LIST="7.0 7.5 8.0 8.6 8.9 9.0+PTX"

# Python Configuration
PYTHONUNBUFFERED=1
DEBIAN_FRONTEND=noninteractive

# Application Configuration
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1:latest
RESEARCH_LLM_MODEL=gpt-oss:20b
RESEARCH_TEMPERATURE=0.7
MAX_TOKENS=4096
```

### Port Mappings
| Service | Container Port | Host Port | Purpose |
|---------|----------------|-----------|---------|
| **Backend** | 8000 | 8001 | FastAPI API server |
| **Frontend** | 3000 | 3001 | Next.js web server |
| **Ollama** | 11434 | 11434 | LLM inference server |

### Volume Mounts
| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./outputs` | `/workspace/outputs` | Generated files |
| `./chroma_db` | `/workspace/chroma_db` | Vector database |
| `./pdfs` | `/workspace/pdfs` | Document storage |

## Docker Compose Configuration

### Services
```yaml
services:
  tradingai-rag:
    build: ./config
    ports:
      - "8001:8000"
    environment:
      - OLLAMA_BASE_URL=http://ollama:11434
    depends_on:
      - ollama
    volumes:
      - ./outputs:/workspace/outputs
      - ./chroma_db:/workspace/chroma_db
      - ./pdfs:/workspace/pdfs

  tradingai-frontend:
    build: ./frontend
    ports:
      - "3001:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8001
    depends_on:
      - tradingai-rag

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
```

## Build Requirements

### Prerequisites
- **Docker**: 20.10+
- **Docker Compose**: v2.0+ (uses `docker compose` command)
- **NVIDIA Container Toolkit**: Latest
- **Git**: For cloning repository

### Build Commands
```bash
# Build all services
docker compose build

# Build specific service
docker compose build tradingai-rag
docker compose build tradingai-frontend

# Build with no cache
docker compose build --no-cache

# Build with progress
docker compose build --progress=plain
```

## Runtime Requirements

### Hardware
- **GPU**: NVIDIA with 24GB+ VRAM (recommended)
- **RAM**: 32GB+ system memory
- **Storage**: 100GB+ free space
- **CPU**: 8+ cores

### Software
- **Docker Engine**: 20.10+
- **NVIDIA Container Toolkit**: Latest
- **Docker Compose**: v2.0+ (uses `docker compose` command)

## Container Health Checks

### Backend Health Check
```bash
curl http://localhost:8001/health
# Expected: {"status":"healthy","service":"tradingai-research-platform"}
```

### Frontend Health Check
```bash
curl http://localhost:3001/api/health
# Expected: {"status":"healthy","service":"tradingai-research-platform"}
```

### Ollama Health Check
```bash
curl http://localhost:11434/api/tags
# Expected: List of available models
```

## Troubleshooting

### Common Issues
1. **GPU not detected**: Ensure NVIDIA Container Toolkit is installed
2. **Port conflicts**: Check ports 3001, 8001, 11434 are available
3. **Memory issues**: Increase Docker memory limits
4. **Build failures**: Check internet connection and Docker daemon

### Debug Commands
```bash
# Check container status
docker compose ps

# View logs
docker compose logs -f tradingai-rag
docker compose logs -f tradingai-frontend
docker compose logs -f ollama

# Execute commands in container
docker compose exec tradingai-rag bash
docker compose exec tradingai-frontend sh

# Check resource usage
docker stats

# Clean up
docker compose down -v
docker system prune -a
```

## Security Considerations

### Container Security
- Run containers as non-root user
- Use specific image tags (not `latest`)
- Scan images for vulnerabilities
- Limit container privileges

### Network Security
- Use internal networks for service communication
- Expose only necessary ports
- Use HTTPS in production
- Implement proper authentication

## Performance Optimization

### Resource Limits
```yaml
services:
  tradingai-rag:
    deploy:
      resources:
        limits:
          memory: 16G
          cpus: '8'
        reservations:
          memory: 8G
          cpus: '4'
```

### GPU Configuration
```yaml
services:
  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Maintainer**: TradingAI Research Platform Team