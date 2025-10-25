# SearXNG Configuration for GraphMind

## Overview
SearXNG is configured for optimal LLM integration with JSON output and proper bot detection bypass.

## Configuration Files

### 1. `/searxng/settings.yml` (Volume Mounted)
```yaml
# Key settings:
- use_default_settings: true
- search.formats: [html, json]
- search.max_page: 10  # Up to 10 pages of results
- server.limiter: false  # Disabled for internal LLM use
- valkey.url: valkey://searxng-redis:6379/0
```

**Location**: `/home/brad/cursor_code/EminiPlayer/searxng/settings.yml`
**Mounted to**: `/etc/searxng/settings.yml` in container

### 2. `app/searxng_client.py` (Built into Image)
Updated to include required HTTP headers:
```python
headers = {
    'User-Agent': 'GraphMind-Research-Platform/2.0',
    'Accept': 'application/json',
    'X-Forwarded-For': '127.0.0.1',  # Required for botdetection
    'X-Real-IP': '127.0.0.1'  # Required for botdetection
}
```

## Why These Headers Are Required

According to [SearXNG documentation](https://docs.searxng.org/admin/searx.limiter.html):
> "A correct setup of the HTTP request headers `X-Forwarded-For` and `X-Real-IP` 
> is essential to be able to assign a request to an IP correctly"

Without these headers, SearXNG's botdetection returns **403 Forbidden** errors.

## Docker Integration

### Volume Mount (docker-compose.graphmind.yml)
```yaml
searxng:
  volumes:
    - ./searxng:/etc/searxng  # Mounts settings.yml
```

### Redis/Valkey Connection
```yaml
searxng-redis:
  image: valkey/valkey:8-alpine
  # Connected via: valkey://searxng-redis:6379/0
```

## Testing

### From Backend Container
```bash
docker exec graphmind-rag python3 -c "
from app.searxng_client import SearXNGClient
client = SearXNGClient(base_url='http://searxng:8080')
results = client.search('test query', num_results=5)
print(f'Found {len(results)} results')
"
```

### Direct API Test
```bash
curl -H "X-Forwarded-For: 127.0.0.1" \
     -H "X-Real-IP: 127.0.0.1" \
     "http://localhost:8080/search?q=test&format=json&pageno=1"
```

## Result Limits

- **Maximum pages**: 10 (configurable via `search.max_page`)
- **Results per page**: ~50 (SearXNG default)
- **Total possible results**: ~500 (10 pages × 50 results)
- **Controlled by client**: `num_results` parameter in `search()` method

## Pagination

Use the `pageno` parameter for pagination:
```python
# Page 1
results = client.search('query', pageno=1)

# Page 2
results = client.search('query', pageno=2)
```

## Status

✅ **Configuration Complete** (October 24, 2025)
- SearXNG container running
- JSON output enabled
- Botdetection bypassed for internal use
- Redis/Valkey connected
- Client code updated with required headers
- Docker image rebuilt with fixes
- Tested and verified working

## Deployment Checklist

- [x] Create `searxng/settings.yml` with proper configuration
- [x] Update `app/searxng_client.py` with required headers
- [x] Rebuild Docker image: `docker compose build graphmind-rag`
- [x] Restart services: `docker compose up -d`
- [x] Verify SearXNG is accessible from backend
- [x] Test JSON API returns results
