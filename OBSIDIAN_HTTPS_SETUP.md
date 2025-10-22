# 🔐 Obsidian Local REST API HTTPS Setup Guide

## 🚨 Current Issue
The Obsidian Local REST API is running on HTTPS but only listening on `127.0.0.1:27124` (localhost), which means the Docker container cannot access it from `192.168.50.43:27124`.

## 🔧 Solution: Configure Plugin to Listen on All Interfaces

### Step 1: Open Obsidian Settings
1. **Open Obsidian**
2. **Go to Settings** (gear icon) → **Community Plugins**
3. **Find "Local REST API"** in the list
4. **Click the gear icon** next to it to open plugin settings

### Step 2: Configure Network Binding
In the Local REST API plugin settings, look for:

```
✅ Enable API: ON
Port: 27124
✅ Enable CORS: ON
✅ Enable Authentication: ON
API Key: 6f5c25819efb4ac5c9b092a8a0f2726d90d32e63b8d5d8aa674f4801fed69254
Bind to localhost only: OFF  ← THIS IS CRUCIAL!
```

### Step 3: Verify Configuration
After saving the settings, the plugin should show:
- **Status**: "API is running on https://0.0.0.0:27124"
- **NOT**: "API is running on https://127.0.0.1:27124"

### Step 4: Test the Configuration

#### Test from Host:
```bash
# Test localhost (should work)
curl -k https://127.0.0.1:27124/

# Test network IP (should work after configuration)
curl -k https://192.168.50.43:27124/

# Test with authentication
curl -k -H "Authorization: Bearer 6f5c25819efb4ac5c9b092a8a0f2726d90d32e63b8d5d8aa674f4801fed69254" https://192.168.50.43:27124/
```

#### Test from Container:
```bash
# Test connection from container
docker exec emini-rag python3 -c "
import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
try:
    response = requests.get('https://192.168.50.43:27124/', verify=False, timeout=5)
    print(f'Status: {response.status_code}')
    print(f'Response: {response.text[:200]}')
except Exception as e:
    print(f'Error: {e}')
"
```

### Step 5: Restart Container
Once the API is accessible from the network:

```bash
docker restart emini-rag
```

### Step 6: Test RAG Integration
```bash
# Test the Obsidian RAG endpoint
curl -X POST http://localhost:8001/ask-obsidian \
  -H "Content-Type: application/json" \
  -d '{"query": "What trading strategies do I have in my notes?", "mode": "qa", "top_k": 5}'
```

## 🔍 Troubleshooting

### If "Bind to localhost only" option is not visible:
1. **Update the plugin** to the latest version
2. **Restart Obsidian** after updating
3. **Check plugin documentation** for the correct setting name

### If the API still doesn't work:
1. **Check firewall** - ensure port 27124 is not blocked
2. **Try a different port** (e.g., 27125) if 27124 is blocked
3. **Check if another service** is using port 27124

### If you can't find the network binding option:
The plugin might use different terminology:
- "Listen on all interfaces"
- "Allow external connections"
- "Network access"
- "Bind to 0.0.0.0"

## 🧪 Verification Commands

```bash
# Check what's listening on port 27124
ss -tlnp | grep 27124

# Should show: LISTEN 0 511 0.0.0.0:27124 (not 127.0.0.1:27124)

# Test API endpoints
curl -k https://192.168.50.43:27124/
curl -k -H "Authorization: Bearer 6f5c25819efb4ac5c9b092a8a0f2726d90d32e63b8d5d8aa674f4801fed69254" https://192.168.50.43:27124/

# Test RAG integration
python3 test_obsidian_connection.py
```

## 🎯 Expected Results

Once properly configured:
- **API Status**: "API is running on https://0.0.0.0:27124"
- **Network Test**: `curl https://192.168.50.43:27124/` returns JSON
- **Container Test**: Connection from container succeeds
- **RAG Integration**: `/ask-obsidian` endpoint works with your notes

## 🔐 Security Note

Binding to `0.0.0.0` makes the API accessible from any device on your network. For production use:
- Use a firewall to restrict access
- Consider using a VPN
- Regularly rotate API keys
- Monitor access logs

---

**The key is finding and disabling the "Bind to localhost only" option in the Obsidian Local REST API plugin settings!** 🎯