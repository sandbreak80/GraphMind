# Obsidian MCP Integration Setup

This guide will help you set up Obsidian MCP integration with your EminiPlayer RAG system.

## Your Configuration
- **Vault Path**: `/home/brad/obsidian-bstoner`
- **API Key**: `6f5c25819efb4ac5c9b092a8a0f2726d90d32e63b8d5d8aa674f4801fed69254`
- **API URL**: `http://localhost:27123`

## Prerequisites

1. **Obsidian installed** on your system
2. **Obsidian Local REST API plugin** installed and enabled
3. **Node.js** installed for running the MCP server

## Step 1: Install Obsidian Local REST API Plugin

1. Open Obsidian
2. Go to Settings → Community Plugins
3. Browse community plugins
4. Search for "Local REST API"
5. Install and enable the plugin
6. Go to the plugin settings and:
   - Enable the API
   - Set port to `27123` (default)
   - Generate an API token (or use the one provided: `6f5c25819efb4ac5c9b092a8a0f2726d90d32e63b8d5d8aa674f4801fed69254`)

## Step 2: Install Obsidian MCP Server

Choose one of these MCP servers:

### Option A: obsidian-mcp-server (Recommended)
```bash
# Install the comprehensive Obsidian MCP server
npm install -g @cyanheads/obsidian-mcp-server

# Run the server with your vault path
obsidian-mcp-server --vault-path "/home/brad/obsidian-bstoner" --port 27124
```

### Option B: mcp-obsidian (Alternative)
```bash
# Install the simpler MCP server
npm install -g mcp-obsidian

# Run the server with your vault path
mcp-obsidian --vault-path "/home/brad/obsidian-bstoner" --port 27124
```

## Step 3: Configure Environment Variables

The docker-compose.yml has been updated with your Obsidian configuration:

```yaml
environment:
  - OBSIDIAN_VAULT_PATH=/home/brad/obsidian-bstoner
  - OBSIDIAN_API_URL=http://host.docker.internal:27123
  - OBSIDIAN_API_KEY=6f5c25819efb4ac5c9b092a8a0f2726d90d32e63b8d5d8aa674f4801fed69254
volumes:
  - /home/brad/obsidian-bstoner:/workspace/obsidian_vault:ro
```

## Step 4: Ready to Use

Your configuration is already set up! The system will automatically:
- Mount your Obsidian vault at `/home/brad/obsidian-bstoner`
- Connect to the Obsidian API at `http://localhost:27123`
- Use your provided API key for authentication

## Step 5: Test the Integration

1. Start the Obsidian MCP server
2. Start your EminiPlayer RAG system
3. Test the new endpoint:

```bash
curl -X POST http://localhost:8001/ask-obsidian \
  -H "Content-Type: application/json" \
  -d '{"query": "What trading strategies do I have in my notes?", "mode": "qa", "top_k": 10}'
```

## Available Endpoints

- **`/ask-obsidian`**: Enhanced search with personal Obsidian notes
- **`/ask-enhanced`**: Enhanced search with web context (SearXNG)
- **`/ask`**: Standard document-only search

## Features

The Obsidian integration provides:

1. **Personal Knowledge Search**: Search through your personal trading notes
2. **Tag-based Filtering**: Find notes by trading-related tags
3. **Note Linking**: Access linked notes for context
4. **Recent Notes**: Get recently modified notes
5. **Metadata Access**: Access note metadata, tags, and modification dates
6. **Caching**: 5-minute TTL for improved performance

## Troubleshooting

1. **Connection Issues**: Ensure the Obsidian Local REST API plugin is running
2. **Vault Path**: Make sure the vault path is correct and accessible
3. **API Key**: Verify the API key is correct in the plugin settings
4. **Port Conflicts**: Ensure ports 27123 and 27124 are available

## Security Note

The API key is included in the docker-compose.yml for convenience. For production use, consider:
1. Using environment variables
2. Restricting API access to localhost only
3. Using a more secure authentication method