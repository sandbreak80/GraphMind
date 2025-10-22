# 🔧 Obsidian Local REST API Setup Guide

The Obsidian Local REST API plugin needs to be properly configured to work with your EminiPlayer RAG system.

## 🚨 Current Issue
- Obsidian is running on port 27124
- Port is listening but API is not responding
- Container can't connect to the API

## 📋 Step-by-Step Setup

### Step 1: Install the Plugin
1. **Open Obsidian**
2. **Go to Settings** (gear icon) → **Community Plugins**
3. **Browse community plugins**
4. **Search for "Local REST API"**
5. **Install** the plugin
6. **Enable** the plugin

### Step 2: Configure the Plugin
1. **Go to Settings** → **Community Plugins** → **Local REST API**
2. **Click the gear icon** next to "Local REST API"
3. **Configure the following settings**:

```
✅ Enable API: ON
Port: 27124
✅ Enable CORS: ON
✅ Enable Authentication: OFF (for now)
Bind to localhost only: OFF (IMPORTANT!)
```

### Step 3: Verify Configuration
The plugin should show:
- **Status**: "API is running on http://0.0.0.0:27124"
- **NOT**: "API is running on http://127.0.0.1:27124"

### Step 4: Test the API
Run this test to verify it's working:

```bash
# Test from host
curl http://127.0.0.1:27124/

# Test from host with IP
curl http://192.168.50.43:27124/

# Test API endpoints
curl http://127.0.0.1:27124/notes
curl http://127.0.0.1:27124/search?query=test
```

### Step 5: Update Docker Configuration
Once the API is working, restart the container:

```bash
docker restart emini-rag
```

## 🔍 Troubleshooting

### If API is not responding:
1. **Check plugin status** in Obsidian settings
2. **Restart Obsidian** after configuration changes
3. **Check firewall** - make sure port 27124 is not blocked
4. **Try different port** (e.g., 27125) if 27124 is blocked

### If "Bind to localhost only" is ON:
- **Turn it OFF** - this prevents Docker container access
- The API must bind to `0.0.0.0` to be accessible from containers

### If authentication is required:
- **Turn OFF authentication** for now
- Or update the API key in docker-compose.yml

## 🧪 Test Commands

```bash
# Test API from host
python3 test_obsidian_api.py

# Test from container (after restart)
docker exec emini-rag python3 -c "
import requests
try:
    response = requests.get('http://192.168.50.43:27124/', timeout=5)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text[:200]}')
except Exception as e:
    print(f'Error: {e}')
"

# Test the RAG integration
curl -X POST http://localhost:8001/ask-obsidian \
  -H "Content-Type: application/json" \
  -d '{"query": "What trading strategies do I have in my notes?", "mode": "qa", "top_k": 5}'
```

## 📊 Expected Results

Once properly configured, you should see:
- **API Status**: "API is running on http://0.0.0.0:27124"
- **Test Response**: JSON data from the API
- **RAG Integration**: Enhanced search results with your personal notes

## 🔐 Security Note

For production use, consider:
- Enabling authentication
- Using a more secure API key
- Restricting access to specific IPs
- Using HTTPS instead of HTTP

---

**Need help?** Check the Obsidian Local REST API plugin documentation or try a different port if 27124 is blocked.