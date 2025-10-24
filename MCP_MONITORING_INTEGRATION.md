# 🔌 MCP + Monitoring Integration Plan

## 🎯 **Goal: Add MCP to RAG System with Comprehensive Monitoring**

Leverage Docker's plug-and-play MCP solution to enhance our RAG system with document access, database integration, and comprehensive monitoring.

---

## 🛠️ **Enhanced Tool Stack with MCP**

### **Core Components:**
1. **Docker MCP Gateway** - Central hub for MCP servers
2. **MCP Filesystem Server** - Document access and browsing
3. **MCP Database Servers** - Postgres, SingleStore integration
4. **Langfuse** - LLM observability & tracing
5. **DeepEval** - RAG evaluation metrics
6. **Custom Dashboard** - MCP-integrated monitoring

---

## 🐳 **Docker Compose Integration**

### **Complete docker-compose.yml with MCP**
```yaml
version: '3.8'

services:
  # Existing RAG services
  rag-service:
    build: .
    ports:
      - "8001:8001"
    volumes:
      - ./documents:/workspace/documents:ro
      - ./outputs:/workspace/outputs
    environment:
      - MCP_GATEWAY_URL=http://mcp-gateway:3333
      - LANGFUSE_SECRET_KEY=${LANGFUSE_SECRET_KEY}
      - LANGFUSE_PUBLIC_KEY=${LANGFUSE_PUBLIC_KEY}
      - LANGFUSE_HOST=http://langfuse:3000
    depends_on:
      - mcp-gateway
      - langfuse
      - postgres

  # MCP Gateway - Central hub
  mcp-gateway:
    image: mcp/docker:latest
    container_name: mcp-gateway
    ports:
      - "3333:3333"
    environment:
      - MCP_GATEWAY_LOG_LEVEL=info
      - MCP_GATEWAY_AUTH_ENABLED=false  # For development
    networks:
      - mcp-network

  # MCP Filesystem Server - Document access
  mcp-filesystem:
    image: mcp/filesystem:latest
    container_name: mcp-filesystem
    volumes:
      - ./documents:/data:ro  # Read-only access to documents
      - ./outputs:/outputs:ro  # Read-only access to outputs
    environment:
      - MCP_ROOTS=/data,/outputs
    networks:
      - mcp-network

  # MCP Postgres Server - Database access
  mcp-postgres:
    image: mcp/postgres:latest
    container_name: mcp-postgres
    environment:
      - POSTGRES_CONNECTION_STRING=postgresql://langfuse:langfuse@postgres:5432/langfuse
    depends_on:
      - postgres
    networks:
      - mcp-network

  # MCP Docker Hub Server - Container insights
  mcp-dockerhub:
    image: mcp/server/dockerhub:latest
    container_name: mcp-dockerhub
    environment:
      - DOCKERHUB_TOKEN=${DOCKERHUB_TOKEN}
    networks:
      - mcp-network

  # Langfuse - LLM observability
  langfuse:
    image: langfuse/langfuse:latest
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://langfuse:langfuse@postgres:5432/langfuse
      - NEXTAUTH_SECRET=${NEXTAUTH_SECRET}
      - NEXTAUTH_URL=http://localhost:3000
    depends_on:
      - postgres
    networks:
      - mcp-network

  # PostgreSQL - Database for Langfuse and metadata
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=langfuse
      - POSTGRES_USER=langfuse
      - POSTGRES_PASSWORD=langfuse
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - mcp-network

  # Frontend
  frontend:
    build: ./frontend
    ports:
      - "3001:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8001
      - NEXT_PUBLIC_MCP_GATEWAY_URL=http://localhost:3333
    depends_on:
      - rag-service
      - mcp-gateway

networks:
  mcp-network:
    driver: bridge

volumes:
  postgres_data:
```

---

## 🔌 **MCP Integration Implementation**

### **1. MCP Client Integration**
```python
# app/mcp_client.py
import asyncio
import json
from typing import Dict, List, Any
import websockets
import aiohttp

class MCPClient:
    def __init__(self, gateway_url: str = "ws://mcp-gateway:3333"):
        self.gateway_url = gateway_url
        self.connection = None
    
    async def connect(self):
        """Connect to MCP Gateway"""
        try:
            self.connection = await websockets.connect(self.gateway_url)
            print(f"Connected to MCP Gateway at {self.gateway_url}")
        except Exception as e:
            print(f"Failed to connect to MCP Gateway: {e}")
            self.connection = None
    
    async def list_servers(self) -> List[Dict]:
        """List available MCP servers"""
        if not self.connection:
            await self.connect()
        
        if self.connection:
            await self.connection.send(json.dumps({
                "jsonrpc": "2.0",
                "id": 1,
                "method": "servers/list"
            }))
            response = await self.connection.recv()
            return json.loads(response)
        return []
    
    async def browse_documents(self, path: str = "/data") -> List[Dict]:
        """Browse documents using filesystem MCP server"""
        if not self.connection:
            await self.connect()
        
        if self.connection:
            await self.connection.send(json.dumps({
                "jsonrpc": "2.0",
                "id": 2,
                "method": "filesystem/list_directory",
                "params": {"path": path}
            }))
            response = await self.connection.recv()
            return json.loads(response)
        return []
    
    async def read_document(self, path: str) -> str:
        """Read document content using filesystem MCP server"""
        if not self.connection:
            await self.connect()
        
        if self.connection:
            await self.connection.send(json.dumps({
                "jsonrpc": "2.0",
                "id": 3,
                "method": "filesystem/read_file",
                "params": {"path": path}
            }))
            response = await self.connection.recv()
            result = json.loads(response)
            return result.get("result", {}).get("content", "")
        return ""
    
    async def query_database(self, query: str) -> List[Dict]:
        """Query database using postgres MCP server"""
        if not self.connection:
            await self.connect()
        
        if self.connection:
            await self.connection.send(json.dumps({
                "jsonrpc": "2.0",
                "id": 4,
                "method": "postgres/query",
                "params": {"query": query}
            }))
            response = await self.connection.recv()
            result = json.loads(response)
            return result.get("result", [])
        return []
    
    async def get_docker_info(self) -> Dict:
        """Get Docker Hub information"""
        if not self.connection:
            await self.connect()
        
        if self.connection:
            await self.connection.send(json.dumps({
                "jsonrpc": "2.0",
                "id": 5,
                "method": "dockerhub/list_images",
                "params": {"limit": 10}
            }))
            response = await self.connection.recv()
            result = json.loads(response)
            return result.get("result", {})
        return {}
    
    async def close(self):
        """Close MCP connection"""
        if self.connection:
            await self.connection.close()
```

### **2. Enhanced RAG with MCP Integration**
```python
# app/mcp_enhanced_rag.py
from app.mcp_client import MCPClient
from app.retrieval import HybridRetriever
from app.langfuse_client import LangfuseClient
from app.rag_evaluator import RAGEvaluator

class MCPEnhancedRAG:
    def __init__(self, retriever: HybridRetriever):
        self.retriever = retriever
        self.mcp_client = MCPClient()
        self.langfuse_client = LangfuseClient()
        self.rag_evaluator = RAGEvaluator()
    
    async def process_query_with_mcp(self, query: str, model: str) -> Dict[str, Any]:
        """Process query with MCP-enhanced context"""
        
        # 1. Get MCP context (documents, database, etc.)
        mcp_context = await self._gather_mcp_context(query)
        
        # 2. Perform hybrid retrieval
        retrieval_results = self.retriever.retrieve(query)
        
        # 3. Combine MCP context with retrieval results
        enhanced_context = self._combine_contexts(retrieval_results, mcp_context)
        
        # 4. Generate response
        response = await self._generate_response(query, enhanced_context, model)
        
        # 5. Evaluate RAG quality
        evaluation = self.rag_evaluator.evaluate_rag_response(
            query, 
            enhanced_context, 
            response
        )
        
        # 6. Track with Langfuse
        self.langfuse_client.track_rag_query(
            query=query,
            model=model,
            response=response,
            retrieval_results=retrieval_results,
            mcp_context=mcp_context,
            evaluation=evaluation
        )
        
        return {
            "response": response,
            "retrieval_results": retrieval_results,
            "mcp_context": mcp_context,
            "evaluation": evaluation
        }
    
    async def _gather_mcp_context(self, query: str) -> Dict[str, Any]:
        """Gather context from MCP servers"""
        context = {
            "documents": [],
            "database_results": [],
            "docker_info": {}
        }
        
        try:
            # Browse documents
            documents = await self.mcp_client.browse_documents()
            context["documents"] = documents[:5]  # Limit to 5 most relevant
            
            # Query database for relevant metadata
            db_query = f"SELECT * FROM document_metadata WHERE content_type LIKE '%{query}%' LIMIT 5"
            db_results = await self.mcp_client.query_database(db_query)
            context["database_results"] = db_results
            
            # Get Docker info (for system context)
            docker_info = await self.mcp_client.get_docker_info()
            context["docker_info"] = docker_info
            
        except Exception as e:
            print(f"MCP context gathering failed: {e}")
        
        return context
    
    def _combine_contexts(self, retrieval_results: List[Dict], mcp_context: Dict) -> str:
        """Combine retrieval and MCP context"""
        combined = []
        
        # Add retrieval results
        for result in retrieval_results:
            combined.append(f"Retrieved: {result['text']}")
        
        # Add MCP document context
        for doc in mcp_context.get("documents", []):
            if doc.get("type") == "file":
                combined.append(f"Document: {doc.get('name', 'Unknown')}")
        
        # Add database context
        for db_result in mcp_context.get("database_results", []):
            combined.append(f"Database: {db_result}")
        
        return "\n\n".join(combined)
```

### **3. MCP-Enhanced API Endpoints**
```python
# Add to app/main.py
from app.mcp_client import MCPClient
from app.mcp_enhanced_rag import MCPEnhancedRAG

# Global instances
mcp_client = MCPClient()
mcp_enhanced_rag = MCPEnhancedRAG(retriever)

@app.get("/mcp/servers")
async def list_mcp_servers():
    """List available MCP servers"""
    servers = await mcp_client.list_servers()
    return {"servers": servers}

@app.get("/mcp/documents")
async def browse_mcp_documents(path: str = "/data"):
    """Browse documents via MCP"""
    documents = await mcp_client.browse_documents(path)
    return {"documents": documents}

@app.get("/mcp/database")
async def query_mcp_database(query: str):
    """Query database via MCP"""
    results = await mcp_client.query_database(query)
    return {"results": results}

@app.post("/ask/mcp")
async def ask_question_with_mcp(request: AskRequest, current_user: dict = Depends(get_current_user)):
    """Ask question with MCP-enhanced context"""
    try:
        result = await mcp_enhanced_rag.process_query_with_mcp(
            query=request.query,
            model=request.model
        )
        
        return AskResponse(
            answer=result["response"],
            citations=result["retrieval_results"],
            mcp_context=result["mcp_context"],
            evaluation=result["evaluation"]
        )
        
    except Exception as e:
        logger.error(f"MCP-enhanced query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

---

## 📊 **MCP-Enhanced Monitoring Dashboard**

### **Frontend Integration**
```typescript
// frontend/components/MCPMonitoringDashboard.tsx
export default function MCPMonitoringDashboard() {
  const [mcpServers, setMcpServers] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    // Fetch MCP servers
    fetch('/api/mcp/servers')
      .then(res => res.json())
      .then(data => setMcpServers(data.servers));
    
    // Fetch documents
    fetch('/api/mcp/documents')
      .then(res => res.json())
      .then(data => setDocuments(data.documents));
    
    // Fetch metrics
    fetch('/api/monitoring/summary')
      .then(res => res.json())
      .then(setMetrics);
  }, []);

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">MCP-Enhanced RAG Monitoring</h1>
      
      {/* MCP Status */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">MCP Servers</h3>
          <p className="text-3xl font-bold text-blue-600">
            {mcpServers.length}
          </p>
          <p className="text-sm text-gray-600 mt-2">
            Active MCP servers
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Documents</h3>
          <p className="text-3xl font-bold text-green-600">
            {documents.length}
          </p>
          <p className="text-sm text-gray-600 mt-2">
            Available via MCP
          </p>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-2">Gateway Status</h3>
          <p className="text-3xl font-bold text-purple-600">
            {mcpServers.length > 0 ? 'Online' : 'Offline'}
          </p>
          <p className="text-sm text-gray-600 mt-2">
            MCP Gateway
          </p>
        </div>
      </div>

      {/* MCP Tools */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Document Browser</h3>
          <div className="max-h-64 overflow-y-auto">
            {documents.map((doc, index) => (
              <div key={index} className="flex justify-between items-center py-2 border-b">
                <span className="text-sm">{doc.name}</span>
                <span className="text-xs text-gray-500">{doc.type}</span>
              </div>
            ))}
          </div>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">MCP Servers</h3>
          <div className="space-y-2">
            {mcpServers.map((server, index) => (
              <div key={index} className="flex justify-between items-center py-2 border-b">
                <span className="text-sm">{server.name}</span>
                <span className="text-xs text-green-600">Active</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* External Tools */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">Langfuse Tracing</h3>
          <p className="text-gray-600 mb-4">
            View detailed traces including MCP context and enhanced retrieval.
          </p>
          <a 
            href="http://localhost:3000" 
            target="_blank" 
            rel="noopener noreferrer"
            className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
          >
            Open Langfuse Dashboard
          </a>
        </div>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h3 className="text-lg font-semibold mb-4">MCP Gateway</h3>
          <p className="text-gray-600 mb-4">
            Access MCP Gateway directly for debugging and configuration.
          </p>
          <a 
            href="http://localhost:3333" 
            target="_blank" 
            rel="noopener noreferrer"
            className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600"
          >
            Open MCP Gateway
          </a>
        </div>
      </div>
    </div>
  );
}
```

---

## 🎯 **Implementation Timeline**

### **Week 1: MCP Setup**
- [ ] Add MCP services to docker-compose.yml
- [ ] Implement MCPClient class
- [ ] Set up MCP Gateway and filesystem server
- [ ] Test MCP document access

### **Week 2: Integration & Monitoring**
- [ ] Integrate MCP with RAG system
- [ ] Add Langfuse tracing with MCP context
- [ ] Implement DeepEval evaluation
- [ ] Create MCP-enhanced API endpoints

### **Week 3: Dashboard & Testing**
- [ ] Build MCP monitoring dashboard
- [ ] Test end-to-end MCP integration
- [ ] Set up baseline measurements
- [ ] Document MCP usage

---

## 🚀 **Key Benefits of MCP Integration**

### **Enhanced Document Access**
- **Real-time browsing** of document repository
- **Structured access** to different document types
- **Metadata integration** from database queries

### **Improved Context Quality**
- **Multi-source context** (retrieval + MCP)
- **Dynamic document selection** based on query
- **Database-driven insights** for better responses

### **Better Monitoring**
- **MCP-aware tracing** in Langfuse
- **Document access metrics** via MCP
- **Enhanced evaluation** with MCP context

### **Operational Benefits**
- **Plug-and-play** Docker integration
- **Secure document access** (read-only by default)
- **Scalable architecture** for additional MCP servers

This gives us a powerful, monitored RAG system with MCP integration that's perfect for our local Docker setup!