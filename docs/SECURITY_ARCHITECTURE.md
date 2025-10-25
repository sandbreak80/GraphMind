# GraphMind Security Architecture

## 🔒 Security-First Design

GraphMind follows a **zero-trust security model** where only the frontend is exposed externally, and all backend services communicate internally via Docker networks.

## 🌐 Network Architecture

### **Public Access (Internet)**
- ✅ **Frontend Only**: `https://emini.riffyx.com`
- ❌ **API**: NOT exposed externally
- ❌ **Backend Services**: NOT exposed externally

### **Internal Docker Network (`graphmind-network`)**
- 🔒 **GraphMind RAG API**: `http://graphmind-rag:8000`
- 🔒 **ChromaDB**: `http://chromadb:8000`
- 🔒 **Redis**: `redis://redis:6379`
- 🔒 **Ollama**: `http://ollama:11434`
- 🔒 **SearXNG**: `http://searxng:8080`
- 🔒 **MCP Servers**: `http://obsidian-mcp:8081`, `http://docker-mcp:8082`, `http://filesystem-mcp:8083`
- 🔒 **Monitoring**: `http://prometheus:9090`, `http://grafana:3000`

## 🛡️ Security Benefits

### **1. Minimal Attack Surface**
- Only frontend exposed to internet
- No direct access to backend services
- No API endpoints accessible externally

### **2. Internal Communication**
- All backend services communicate via Docker network
- Frontend → API → Backend services (all internal)
- No external network calls between services

### **3. Network Isolation**
- Docker network provides isolation
- Services can only communicate with each other
- No external network access for backend services

### **4. Single Entry Point**
- Nginx as reverse proxy
- All requests go through frontend
- Centralized security controls

## 🔧 Communication Flow

```
Internet → Nginx → Frontend → API → Backend Services
    ↓         ↓        ↓        ↓         ↓
  HTTPS    Proxy   React   FastAPI   Internal
```

### **Request Flow:**
1. **User** → `https://emini.riffyx.com`
2. **Nginx** → Proxies to Frontend
3. **Frontend** → Calls API internally (`http://graphmind-rag:8000`)
4. **API** → Calls backend services internally
5. **Response** → Back through the chain

## 🚫 What's NOT Exposed

### **External Ports (Blocked)**
- ❌ Port 8000 (GraphMind RAG API)
- ❌ Port 8001 (ChromaDB)
- ❌ Port 6379 (Redis)
- ❌ Port 11434 (Ollama)
- ❌ Port 8080 (SearXNG)
- ❌ Port 8081-8083 (MCP Servers)
- ❌ Port 9090 (Prometheus)
- ❌ Port 3001 (Grafana)

### **External URLs (Blocked)**
- ❌ `https://emini.riffyx.com/api`
- ❌ `https://emini.riffyx.com/search`
- ❌ `https://emini.riffyx.com/ollama`
- ❌ `https://emini.riffyx.com/mcp/*`
- ❌ `https://emini.riffyx.com/monitoring/*`

## ✅ What IS Exposed

### **Public Access (Allowed)**
- ✅ `https://emini.riffyx.com` - Frontend only
- ✅ `https://emini.riffyx.com/health` - Health check

### **Internal Access (Docker Network)**
- ✅ All backend services communicate internally
- ✅ Frontend can call API internally
- ✅ API can call all backend services internally

## 🔐 Security Features

### **1. Network Security**
- Docker network isolation
- No external port exposure
- Internal service communication only

### **2. Application Security**
- Frontend handles all user interactions
- API validates all requests internally
- Backend services process data securely

### **3. Data Security**
- No direct database access from internet
- No direct API access from internet
- All data flows through secure internal channels

## 🚀 Deployment Security

### **Production Deployment**
1. **SSL/TLS**: HTTPS only for frontend
2. **Firewall**: Block all ports except 80/443
3. **Docker Network**: Isolated internal network
4. **No External Access**: Backend services internal only

### **Development Deployment**
1. **Local Access**: Frontend accessible locally
2. **Internal Services**: All backend services internal
3. **No External Exposure**: Same security model as production

## 📋 Security Checklist

- ✅ Frontend only exposed externally
- ✅ API internal only
- ✅ Backend services internal only
- ✅ Docker network isolation
- ✅ No external port exposure
- ✅ Single entry point (Nginx)
- ✅ Internal service communication
- ✅ No direct database access
- ✅ **SECURE BY DEFAULT**

## 🔍 Monitoring & Logging

### **Security Monitoring**
- Nginx access logs for all requests
- Internal service communication logs
- No external access to backend services
- Health checks for all services

### **Audit Trail**
- All requests logged at Nginx level
- Internal API calls logged
- Backend service interactions logged
- No external access attempts possible

This architecture ensures maximum security while maintaining full functionality through internal service communication.
