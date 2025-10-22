# 🧠 Obsidian MCP Integration Setup Guide

Your EminiPlayer RAG system is now configured for Obsidian integration! Here's how to complete the setup:

## ✅ What's Already Configured

- **Vault Path**: `/home/brad/obsidian-bstoner` → `/workspace/obsidian_vault` (in container)
- **API Key**: `6f5c25819efb4ac5c9b092a8a0f2726d90d32e63b8d5d8aa674f4801fed69254`
- **API URL**: `http://localhost:27123`
- **Docker Volume**: Mounted and ready
- **Endpoints**: `/ask-obsidian` endpoint is live

## 🔧 Next Steps to Complete Setup

### Step 1: Install Obsidian Local REST API Plugin

1. **Open Obsidian** on your system
2. **Go to Settings** → **Community Plugins**
3. **Browse community plugins**
4. **Search for "Local REST API"**
5. **Install and enable** the plugin
6. **Configure the plugin**:
   - Go to **Plugin Options** → **Local REST API**
   - **Enable the API** ✅
   - **Set port to**: `27123` (default)
   - **Generate API token** or use: `6f5c25819efb4ac5c9b092a8a0f2726d90d32e63b8d5d8aa674f4801fed69254`
   - **Enable CORS** ✅ (for Docker access)

### Step 2: Test the Connection

Once the plugin is running, test the connection:

```bash
# Test if Obsidian API is responding
curl http://localhost:27123/health

# Test the Obsidian endpoint
curl -X POST http://localhost:8001/ask-obsidian \
  -H "Content-Type: application/json" \
  -d '{"query": "What trading strategies do I have in my notes?", "mode": "qa", "top_k": 5}'
```

### Step 3: Verify Integration

Run the test script:

```bash
python3 test_obsidian_integration.py
```

## 🚀 Available Endpoints

| Endpoint | Description | Features |
|----------|-------------|----------|
| `/ask-obsidian` | **Personal Knowledge Search** | Searches your Obsidian notes + documents |
| `/ask-enhanced` | **Web-Enhanced Search** | Searches documents + real-time web data |
| `/ask` | **Document Search** | Searches only your PDF documents |

## 🧠 Obsidian Integration Features

### Search Capabilities
- **Personal Notes**: Search through your trading notes
- **Tag Filtering**: Find notes by trading-related tags
- **Note Linking**: Access linked notes for context
- **Recent Notes**: Get recently modified notes
- **Metadata Access**: Access note metadata, tags, and dates

### Trading-Specific Features
- **Trading Terms**: Automatically searches for trading-related terms
- **Strategy Notes**: Finds your personal trading strategies
- **Risk Management**: Locates your risk management notes
- **Market Analysis**: Searches your market analysis notes

### Example Queries
```bash
# Find your trading strategies
curl -X POST http://localhost:8001/ask-obsidian \
  -H "Content-Type: application/json" \
  -d '{"query": "What are my ES futures trading strategies?", "mode": "qa", "top_k": 10}'

# Search for risk management notes
curl -X POST http://localhost:8001/ask-obsidian \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I manage risk in my trades?", "mode": "qa", "top_k": 5}'

# Find recent trading notes
curl -X POST http://localhost:8001/ask-obsidian \
  -H "Content-Type: application/json" \
  -d '{"query": "What did I learn about trading this week?", "mode": "qa", "top_k": 8}'
```

## 🔍 How It Works

1. **Query Processing**: Your query is processed for trading-related terms
2. **Dual Search**: Searches both your documents AND Obsidian notes
3. **Context Combination**: Combines document knowledge with personal notes
4. **Enhanced Answer**: Generates comprehensive answers using both sources
5. **Source Attribution**: Shows which sources (documents vs notes) were used

## 🛠️ Troubleshooting

### Connection Issues
```bash
# Check if Obsidian is running
ps aux | grep obsidian

# Check if the API is responding
curl http://localhost:27123/health

# Check container logs
docker logs emini-rag | grep obsidian
```

### Common Issues
1. **"Connection refused"**: Obsidian Local REST API plugin not running
2. **"No notes found"**: Check vault path and API key
3. **"Permission denied"**: Check file permissions on vault directory

### Debug Commands
```bash
# Check vault mount
docker exec emini-rag ls -la /workspace/obsidian_vault

# Test API connection from container
docker exec emini-rag curl http://host.docker.internal:27123/health

# Check environment variables
docker exec emini-rag env | grep OBSIDIAN
```

## 🎯 Expected Results

Once fully set up, you should see:
- **`total_sources`**: Higher numbers (documents + notes)
- **`obsidian_enabled`**: `true`
- **Enhanced answers**: Combining your personal knowledge with document knowledge
- **Personal context**: References to your specific trading notes and strategies

## 🔐 Security Notes

- The API key is included in docker-compose.yml for convenience
- For production use, consider using environment variables
- The vault is mounted as read-only for security
- API access is restricted to localhost by default

---

**Ready to get started?** Just install the Obsidian Local REST API plugin and you'll have access to your personal trading knowledge through the RAG system! 🚀