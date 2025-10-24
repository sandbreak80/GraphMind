# 📋 Requirements Documentation - TradingAI Research Platform

## 🐍 Python Dependencies

### **Core Web Framework & API**
| Library | Version | Purpose |
|---------|---------|---------|
| `fastapi` | >=0.104 | Modern, fast web framework for building APIs |
| `uvicorn[standard]` | >=0.24 | ASGI server for FastAPI |
| `pydantic` | >=2.5 | Data validation and settings management |
| `python-multipart` | latest | Handle multipart form data |

### **Authentication & Security**
| Library | Version | Purpose |
|---------|---------|---------|
| `python-jose[cryptography]` | >=3.3.0 | JWT token handling and encryption |
| `python-magic` | latest | File type detection |

### **Document Processing**
| Library | Version | Purpose |
|---------|---------|---------|
| `docling` | >=1.8 | Advanced PDF processing and parsing |
| `ocrmypdf` | >=15.4 | OCR for PDF files |
| `PyMuPDF` | >=1.23 | PDF manipulation and text extraction |
| `pdf2image` | latest | Convert PDF pages to images |
| `openpyxl` | latest | Excel file processing |
| `python-docx` | latest | Word document processing |
| `pandas` | >=2.1.4 | Data manipulation and analysis |

### **Video & Media Processing**
| Library | Version | Purpose |
|---------|---------|---------|
| `faster-whisper` | >=0.10 | Fast Whisper speech-to-text |
| `opencv-python` | latest | Computer vision and video processing |
| `ffmpeg-python` | latest | Video/audio processing wrapper |
| `pytesseract` | latest | OCR for video frames |
| `pillow` | latest | Image processing |

### **AI/ML & Vector Processing**
| Library | Version | Purpose |
|---------|---------|---------|
| `chromadb` | >=0.4 | Vector database for embeddings |
| `sentence-transformers` | latest | Text embeddings and similarity |
| `torch` | latest | PyTorch deep learning framework |
| `transformers` | latest | Hugging Face transformers library |
| `numpy` | >=1.26.4,<2.0 | Numerical computing |
| `rank-bm25` | latest | BM25 text ranking algorithm |

### **Web & Network**
| Library | Version | Purpose |
|---------|---------|---------|
| `requests` | >=2.32.3 | HTTP client library |
| `httpx` | latest | Modern async HTTP client |
| `aiohttp` | >=3.8.0 | Async HTTP client/server |
| `crawl4ai` | >=0.7.4 | Web crawling and content extraction |

### **Utilities**
| Library | Version | Purpose |
|---------|---------|---------|
| `pyyaml` | latest | YAML file processing |
| `tqdm` | latest | Progress bars |

### **Testing & Development**
| Library | Version | Purpose |
|---------|---------|---------|
| `pytest` | latest | Testing framework |
| `pytest-cov` | latest | Coverage plugin for pytest |

## 🐳 Docker Dependencies

### **Base Images**
| Image | Version | Purpose |
|-------|---------|---------|
| `nvidia/cuda` | 12.1.0-runtime-ubuntu22.04 | CUDA-enabled base for GPU processing |
| `node` | 18-alpine | Lightweight Node.js for frontend |

### **System Dependencies (Ubuntu Packages)**
| Package | Purpose |
|---------|---------|
| `python3.10` | Python interpreter |
| `python3-pip` | Python package manager |
| `tesseract-ocr` | OCR engine |
| `tesseract-ocr-eng` | English language pack |
| `ocrmypdf` | OCR for PDFs |
| `poppler-utils` | PDF utilities |
| `ffmpeg` | Video/audio processing |
| `libgl1-mesa-glx` | OpenGL libraries |
| `libglib2.0-0` | GLib library |
| `libsm6` | X11 session management |
| `libxext6` | X11 extension library |
| `libxrender-dev` | X11 rendering library |
| `pkg-config` | Package configuration |
| `libavcodec-dev` | FFmpeg codec library |
| `libavformat-dev` | FFmpeg format library |
| `libavutil-dev` | FFmpeg utility library |
| `libswscale-dev` | FFmpeg scaling library |
| `libavdevice-dev` | FFmpeg device library |
| `libavfilter-dev` | FFmpeg filter library |
| `libswresample-dev` | FFmpeg resampling library |

### **Frontend Dependencies (Alpine)**
| Package | Purpose |
|---------|---------|
| `libc6-compat` | C library compatibility |

## 🤖 Ollama Dependencies

### **Required Models**
| Model | Size | Purpose | GPU Memory |
|-------|------|---------|------------|
| `llama3.2:3b` | 3B | Fast responses, simple queries | ~2GB |
| `llama3.1:latest` | 8B | General purpose, balanced performance | ~5GB |
| `qwen2.5-coder:14b` | 14B | Code analysis, technical queries | ~8GB |
| `gpt-oss:20b` | 20B | Complex reasoning, research mode | ~12GB |

### **Model Capabilities**
| Model | Best For | Response Time | Quality |
|-------|----------|---------------|---------|
| `llama3.2:3b` | Quick QA, simple tasks | <2s | Good |
| `llama3.1:latest` | General chat, analysis | 3-8s | Very Good |
| `qwen2.5-coder:14b` | Code generation, technical docs | 5-12s | Excellent |
| `gpt-oss:20b` | Research, complex reasoning | 8-20s | Outstanding |

### **Ollama Configuration**
```bash
# Minimum system requirements
GPU: NVIDIA with 24GB+ VRAM (recommended)
RAM: 32GB+ system memory
Storage: 100GB+ free space

# Ollama service configuration
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.1:latest
RESEARCH_LLM_MODEL=gpt-oss:20b
RESEARCH_TEMPERATURE=0.7
MAX_TOKENS=4096
```

## 🏗️ System Requirements

### **Hardware Requirements**
| Component | Minimum | Recommended | Production |
|-----------|---------|-------------|------------|
| **GPU** | 12GB VRAM | 24GB VRAM | 40GB+ VRAM |
| **RAM** | 16GB | 32GB | 64GB+ |
| **Storage** | 50GB SSD | 200GB NVMe | 1TB+ NVMe |
| **CPU** | 8 cores | 16 cores | 32+ cores |

### **Software Requirements**
| Software | Version | Purpose |
|----------|---------|---------|
| **Docker** | 20.10+ | Containerization |
| **Docker Compose** | 2.0+ | Multi-container orchestration |
| **NVIDIA Container Toolkit** | Latest | GPU support in containers |
| **Ollama** | 0.1.0+ | Local LLM inference |
| **Python** | 3.10+ | Backend runtime |
| **Node.js** | 18+ | Frontend runtime |

## 📦 Installation Commands

### **Python Dependencies**
```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install individually
pip install fastapi uvicorn pydantic python-multipart
pip install python-jose[cryptography] python-magic
pip install docling ocrmypdf PyMuPDF pdf2image
pip install openpyxl python-docx pandas
pip install faster-whisper opencv-python ffmpeg-python pytesseract pillow
pip install chromadb sentence-transformers
pip install torch transformers numpy rank-bm25
pip install requests httpx aiohttp crawl4ai
pip install pyyaml tqdm pytest pytest-cov
```

### **Docker Setup**
```bash
# Build all services
docker compose build

# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f
```

### **Ollama Setup**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Start Ollama service
ollama serve

# Pull required models
ollama pull llama3.2:3b
ollama pull llama3.1:latest
ollama pull qwen2.5-coder:14b
ollama pull gpt-oss:20b

# Verify models
ollama list
```

## 🔧 Development Dependencies

### **Additional Tools**
| Tool | Purpose |
|------|---------|
| **Git** | Version control |
| **Make** | Build automation |
| **curl** | API testing |
| **jq** | JSON processing |
| **psutil** | System monitoring |
| **nvidia-smi** | GPU monitoring |

### **Development Scripts**
```bash
# Run tests
make test

# Run QA suite
python test_comprehensive_suite_v2.py

# Performance testing
python test_parallel_performance.py

# Resource monitoring
python test_simple_resource_usage.py
```

## 📊 Dependency Statistics

### **Total Count**
- **Python Libraries**: 55+ packages
- **System Dependencies**: 20+ Ubuntu packages
- **Ollama Models**: 4 models (45GB total)
- **Docker Images**: 2 base images
- **Total Dependencies**: 80+ components

### **Size Estimates**
| Component | Size | Notes |
|-----------|------|-------|
| **Python packages** | ~2GB | Excluding models |
| **Ollama models** | ~45GB | All 4 models |
| **System packages** | ~500MB | Ubuntu dependencies |
| **Docker images** | ~3GB | Base images + layers |
| **Total** | ~50GB | Complete installation |

## 🚀 Quick Start

### **1. Clone Repository**
```bash
git clone <repository-url>
cd EminiPlayer
```

### **2. Install Dependencies**
```bash
# Install Python packages
pip install -r requirements.txt

# Install Ollama models
ollama pull llama3.1:latest
ollama pull qwen2.5-coder:14b
```

### **3. Start Services**
```bash
# Using Docker Compose
docker compose up -d

# Or manually
docker build -t tradingai-rag ./config
docker build -t tradingai-frontend ./frontend
docker run -d --name ollama -p 11434:11434 ollama/ollama
docker run -d --name tradingai-rag -p 8001:8000 tradingai-rag
docker run -d --name tradingai-frontend -p 3001:3000 tradingai-frontend
```

### **4. Verify Installation**
```bash
# Check health
curl http://localhost:3001/api/health
curl http://localhost:8001/health

# Test API
curl -X POST http://localhost:3001/api/auth/login \
  -d "username=admin&password=admin123"
```

## 🔍 Troubleshooting

### **Common Issues**
1. **GPU Memory**: Ensure sufficient VRAM for Ollama models
2. **Port Conflicts**: Check ports 3001, 8001, 11434 are available
3. **Model Loading**: Verify Ollama models are downloaded
4. **Dependencies**: Ensure all Python packages are installed
5. **Permissions**: Check Docker and file permissions

### **Debug Commands**
```bash
# Check GPU usage
nvidia-smi

# Check running processes
ps aux | grep ollama

# Check Docker containers
docker ps -a

# Check logs
docker logs tradingai-rag
docker logs tradingai-frontend
docker logs ollama
```

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Maintainer**: TradingAI Research Platform Team