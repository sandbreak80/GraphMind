# 🤖 Ollama Requirements - TradingAI Research Platform

## Model Specifications

### Required Models
| Model | Size | Parameters | VRAM Usage | Purpose | Performance |
|-------|------|------------|------------|---------|-------------|
| `llama3.2:3b` | 3B | 3.2B | ~2GB | Fast responses, simple queries | <2s response |
| `llama3.1:latest` | 8B | 8B | ~5GB | General purpose, balanced | 3-8s response |
| `qwen2.5-coder:14b` | 14B | 14B | ~8GB | Code analysis, technical docs | 5-12s response |
| `gpt-oss:20b` | 20B | 20B | ~12GB | Complex reasoning, research | 8-20s response |

### Model Capabilities Matrix
| Model | Code | Math | Reasoning | Speed | Quality | Best For |
|-------|------|------|-----------|-------|---------|----------|
| `llama3.2:3b` | ⭐⭐⭐ | ⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ | Quick QA, simple tasks |
| `llama3.1:latest` | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | General chat, analysis |
| `qwen2.5-coder:14b` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | Code generation, technical |
| `gpt-oss:20b` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐⭐ | Research, complex reasoning |

## Installation Requirements

### System Requirements
| Component | Minimum | Recommended | Production |
|-----------|---------|-------------|------------|
| **GPU VRAM** | 12GB | 24GB | 40GB+ |
| **System RAM** | 16GB | 32GB | 64GB+ |
| **Storage** | 50GB | 100GB | 200GB+ |
| **CPU** | 8 cores | 16 cores | 32+ cores |

### Software Dependencies
- **Ollama**: 0.1.0+
- **NVIDIA Driver**: 525.60.13+
- **CUDA**: 12.1+
- **Docker**: 20.10+ (for containerized deployment)

## Installation Commands

### Install Ollama
```bash
# Linux/macOS
curl -fsSL https://ollama.ai/install.sh | sh

# Windows (PowerShell)
winget install Ollama.Ollama

# Docker
docker run -d -v ollama:/root/.ollama -p 11434:11434 --name ollama ollama/ollama
```

### Pull Required Models
```bash
# Pull all models (45GB total)
ollama pull llama3.2:3b
ollama pull llama3.1:latest
ollama pull qwen2.5-coder:14b
ollama pull gpt-oss:20b

# Verify installation
ollama list
```

### Model-Specific Commands
```bash
# Test individual models
ollama run llama3.2:3b "Hello, how are you?"
ollama run llama3.1:latest "Explain quantum computing"
ollama run qwen2.5-coder:14b "Write a Python function to sort a list"
ollama run gpt-oss:20b "Analyze the economic impact of AI on global markets"
```

## Configuration

### Ollama Service Configuration
```bash
# Start Ollama service
ollama serve

# Environment variables
export OLLAMA_HOST=0.0.0.0:11434
export OLLAMA_ORIGINS=*
export OLLAMA_MODELS=/root/.ollama/models

# GPU configuration
export CUDA_VISIBLE_DEVICES=0,1
export NVIDIA_VISIBLE_DEVICES=all
```

### Application Configuration
```python
# config.py
OLLAMA_BASE_URL = "http://ollama:11434"
OLLAMA_MODEL = "llama3.1:latest"
RESEARCH_LLM_MODEL = "gpt-oss:20b"
RESEARCH_TEMPERATURE = 0.7
MAX_TOKENS = 4096
```

## Model Selection Logic

### Query Complexity Detection
```python
def select_model(query: str, mode: str) -> str:
    """Select appropriate model based on query complexity and mode"""
    
    if mode == "qa":
        return "llama3.2:3b"  # Fast, simple responses
    
    elif mode == "chat":
        return "llama3.1:latest"  # Balanced performance
    
    elif mode == "research":
        return "gpt-oss:20b"  # Complex reasoning
    
    elif "code" in query.lower() or "programming" in query.lower():
        return "qwen2.5-coder:14b"  # Code-specific model
    
    elif len(query) > 500 or "analyze" in query.lower():
        return "gpt-oss:20b"  # Complex analysis
    
    else:
        return "llama3.1:latest"  # Default
```

### Performance Optimization
```python
# Parallel model loading
async def load_models():
    """Pre-load models for faster inference"""
    models = ["llama3.2:3b", "llama3.1:latest", "qwen2.5-coder:14b", "gpt-oss:20b"]
    
    for model in models:
        await ollama_client.pull_model(model)
        await ollama_client.warm_up(model)
```

## Memory Management

### GPU Memory Allocation
| Model | VRAM Usage | Peak Usage | Concurrent Users |
|-------|------------|------------|------------------|
| `llama3.2:3b` | 2GB | 3GB | 4-6 users |
| `llama3.1:latest` | 5GB | 7GB | 2-3 users |
| `qwen2.5-coder:14b` | 8GB | 10GB | 1-2 users |
| `gpt-oss:20b` | 12GB | 15GB | 1 user |

### Memory Optimization
```bash
# Monitor GPU memory
nvidia-smi

# Clear GPU memory
ollama stop
ollama serve

# Model unloading (if supported)
ollama unload llama3.2:3b
```

## API Integration

### Ollama API Endpoints
```bash
# List models
curl http://localhost:11434/api/tags

# Generate completion
curl http://localhost:11434/api/generate \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:latest",
    "prompt": "Hello, how are you?",
    "stream": false
  }'

# Chat completion
curl http://localhost:11434/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.1:latest",
    "messages": [
      {"role": "user", "content": "Hello, how are you?"}
    ]
  }'
```

### Python Integration
```python
import requests

class OllamaClient:
    def __init__(self, base_url="http://localhost:11434"):
        self.base_url = base_url
    
    def generate(self, model: str, prompt: str, **kwargs):
        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                **kwargs
            }
        )
        return response.json()
    
    def chat(self, model: str, messages: list, **kwargs):
        response = requests.post(
            f"{self.base_url}/api/chat",
            json={
                "model": model,
                "messages": messages,
                **kwargs
            }
        )
        return response.json()
```

## Troubleshooting

### Common Issues
1. **Model not found**: Ensure model is pulled with `ollama pull <model>`
2. **Out of memory**: Reduce model size or increase GPU memory
3. **Slow responses**: Check GPU utilization and model size
4. **Connection refused**: Ensure Ollama service is running

### Debug Commands
```bash
# Check Ollama status
ollama ps

# View logs
ollama logs

# Test model
ollama run llama3.1:latest "Test prompt"

# Check GPU usage
nvidia-smi

# Monitor system resources
htop
```

### Performance Monitoring
```bash
# Monitor Ollama performance
watch -n 1 'ollama ps'

# Check GPU memory usage
watch -n 1 'nvidia-smi'

# Monitor API responses
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:11434/api/generate
```

## Security Considerations

### Model Security
- Use trusted model sources
- Verify model checksums
- Keep models updated
- Monitor for vulnerabilities

### API Security
- Use authentication tokens
- Implement rate limiting
- Use HTTPS in production
- Monitor API usage

## Backup and Recovery

### Model Backup
```bash
# Backup models directory
tar -czf ollama-models-backup.tar.gz ~/.ollama/models/

# Restore models
tar -xzf ollama-models-backup.tar.gz -C ~/.ollama/
```

### Configuration Backup
```bash
# Backup Ollama configuration
cp ~/.ollama/config.json ollama-config-backup.json

# Restore configuration
cp ollama-config-backup.json ~/.ollama/config.json
```

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Maintainer**: TradingAI Research Platform Team