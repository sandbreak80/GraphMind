# Phase 1: TradingAI → GraphMind Transformation

## 🎯 **Strategic Shift: From Trading-Specific to Open RAG Framework**

**Goal**: Transform our TradingAI Research Platform into a world-class, self-hosted, community-ready RAG framework that can serve any domain.

---

## 🧭 **1. Strategic Transformation Overview**

### **Current State**
- **Domain-Bound**: Optimized specifically for trading data and financial analysis
- **Trading-Specific**: Market data, trading strategies, financial terminology
- **Single Use Case**: Focused on trading research and analysis

### **Target State**
- **Domain-Agnostic**: Modular framework supporting any research domain
- **Plugin Architecture**: Extensible system for different use cases
- **Community-Ready**: Open-source, self-hosted, contributor-friendly

---

## 🔄 **2. Core Architecture Transformation**

### **A. Domain Decoupling Strategy**

| Current Module | Transform To | Rationale |
|---|---|---|
| "TradingAI Research Mode" | `DomainAdapters` plugin system | Let users register their own domains (finance, law, health, etc.) |
| "Market Data / News Feeds" | Optional data connectors | Avoid bundling commercial APIs, make them optional |
| "Trading Strategy Analyzer" | Demo plugin | Keep as sample use case, don't bake into core |
| "Trading-specific prompts" | Domain-agnostic prompt templates | Generic research prompts with domain injection |

### **B. Package & Folder Restructuring**

#### **Current Structure**
```
app/
├── trading_analysis.py
├── market_data_provider.py
├── strategy_analyzer.py
└── trading_specific/
```

#### **New Structure**
```
app/
├── core/
│   ├── retrieval.py
│   ├── embeddings.py
│   └── reranking.py
├── adapters/
│   ├── base_adapter.py
│   ├── finance_adapter.py (demo)
│   └── domain_registry.py
├── connectors/
│   ├── pdf_connector.py
│   ├── obsidian_connector.py
│   └── web_connector.py
└── examples/
    ├── finance_demo/
    ├── legal_demo/
    └── health_demo/
```

### **C. Configuration System**

#### **Environment Variables**
```yaml
# .env.example
# Core Settings
RESEARCH_AI_DOMAIN=finance  # or 'legal', 'health', 'custom'
RESEARCH_AI_TITLE="GraphMind Research Assistant"

# Data Sources (Optional)
ENABLE_OBSIDIAN=true
ENABLE_WEB_SEARCH=true
ENABLE_PDF_INGESTION=true

# Domain-Specific (Optional)
FINANCE_MODE=false
LEGAL_MODE=false
HEALTH_MODE=false
```

#### **Domain Configuration**
```yaml
# config/domains/finance.yaml
name: "Finance Research"
description: "Financial analysis and trading research"
prompts:
  system: "You are a financial research assistant..."
  web_search: "Search for current financial news..."
connectors:
  - obsidian
  - web_search
  - pdf_ingestion
```

---

## 🧩 **3. Pluggable Data Sources Architecture**

### **A. Connector Registry System**

```python
# app/connectors/base_connector.py
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseConnector(ABC):
    """Base class for all data connectors"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.enabled = config.get('enabled', True)
    
    @abstractmethod
    async def connect(self) -> bool:
        """Test connection to data source"""
        pass
    
    @abstractmethod
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search the data source"""
        pass
    
    @abstractmethod
    async def get_metadata(self) -> Dict[str, Any]:
        """Get connector metadata"""
        pass

# app/connectors/registry.py
class ConnectorRegistry:
    """Registry for managing data connectors"""
    
    def __init__(self):
        self.connectors: Dict[str, BaseConnector] = {}
    
    def register(self, name: str, connector: BaseConnector):
        """Register a new connector"""
        self.connectors[name] = connector
    
    def get_connector(self, name: str) -> BaseConnector:
        """Get a connector by name"""
        return self.connectors.get(name)
    
    def list_connectors(self) -> List[str]:
        """List all registered connectors"""
        return list(self.connectors.keys())
```

### **B. Built-in Connectors**

#### **1. PDF Connector**
```python
# app/connectors/pdf_connector.py
class PDFConnector(BaseConnector):
    """PDF document connector"""
    
    async def connect(self) -> bool:
        # Test PDF processing capabilities
        pass
    
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        # Search PDF documents
        pass
```

#### **2. Obsidian Connector**
```python
# app/connectors/obsidian_connector.py
class ObsidianConnector(BaseConnector):
    """Obsidian vault connector"""
    
    async def connect(self) -> bool:
        # Test Obsidian vault access
        pass
    
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        # Search Obsidian notes
        pass
```

#### **3. Web Search Connector**
```python
# app/connectors/web_connector.py
class WebConnector(BaseConnector):
    """Web search connector"""
    
    async def connect(self) -> bool:
        # Test web search API
        pass
    
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        # Perform web search
        pass
```

---

## 🎨 **4. Rebranding Strategy**

### **A. New Brand Identity**

#### **Recommended Name: "GraphMind"**
- **Short & Memorable**: Easy to remember and type
- **Descriptive**: Clearly indicates knowledge graph + AI
- **Domain-Agnostic**: Works for any research domain
- **Technical**: Appeals to developers and researchers

#### **Alternative Names Considered**
- **Ragna**: RAG + AI (too technical)
- **Recall**: Memory-focused (too narrow)
- **Quanta**: Quantum-inspired (too abstract)
- **InsightHub**: Business-focused (too corporate)
- **Athena**: Greek mythology (too specific)

### **B. Branding Elements**

#### **Tagline**
```
"GraphMind — A self-hosted, multi-modal RAG research assistant 
built with Ollama, Chroma, and Next.js"
```

#### **Logo Concept**
- **Graph Node**: Central node with connected edges
- **Color Scheme**: Blue (#3B82F6) + Purple (#8B5CF6) + Green (#10B981)
- **Typography**: Modern, clean, technical

#### **Repository Structure**
```
graphmind/                    # Main repository
├── README.md                 # Updated with new branding
├── docs/                     # Documentation
├── examples/                 # Domain examples
├── config/                   # Configuration templates
└── docker/                   # Docker configurations
```

---

## 🔧 **5. Technical Implementation Plan**

### **A. Phase 1: Rebrand & Cleanup (Week 1)**

#### **1. Repository Rename**
```bash
# Rename repository
git remote set-url origin https://github.com/username/graphmind.git
```

#### **2. Code Refactoring**
- [ ] Remove trading-specific terminology
- [ ] Rename classes and functions
- [ ] Update import statements
- [ ] Refactor domain-specific logic

#### **3. Documentation Update**
- [ ] Update README.md with new branding
- [ ] Create new logo and assets
- [ ] Update all documentation references
- [ ] Create migration guide

### **B. Phase 2: Core Framework (Week 2-3)**

#### **1. Modular Architecture**
- [ ] Create `app/core/` for core functionality
- [ ] Create `app/adapters/` for domain adapters
- [ ] Create `app/connectors/` for data sources
- [ ] Implement plugin system

#### **2. Configuration System**
- [ ] YAML-based domain configuration
- [ ] Environment variable management
- [ ] Connector registry
- [ ] Domain adapter system

#### **3. CLI Interface**
```python
# researchai CLI
researchai init          # Initialize new project
researchai up            # Start services
researchai ingest ./docs # Ingest documents
researchai chat          # Start chat interface
researchai config        # Manage configuration
```

### **C. Phase 3: Documentation & Examples (Week 4)**

#### **1. Documentation Site**
- [ ] MkDocs Material setup
- [ ] Convert existing docs
- [ ] Add architecture diagrams
- [ ] Create user guides

#### **2. Example Domains**
- [ ] Finance demo (current system)
- [ ] Legal research demo
- [ ] Health research demo
- [ ] Academic research demo

---

## 🚀 **6. Deployment & Packaging**

### **A. Docker Compose Profiles**

#### **Core Profile** (`docker-compose.core.yml`)
```yaml
services:
  graphmind-core:
    build: .
    ports: ["8000:8000"]
    environment:
      - PROFILE=core
    depends_on:
      - chromadb
      - redis
      - ollama
```

#### **Full Profile** (`docker-compose.full.yml`)
```yaml
services:
  graphmind-full:
    build: .
    ports: ["8000:8000"]
    environment:
      - PROFILE=full
    depends_on:
      - chromadb
      - redis
      - ollama
      - searxng
      - prometheus
      - grafana
```

#### **Dev Profile** (`docker-compose.dev.yml`)
```yaml
services:
  graphmind-dev:
    build: .
    ports: ["8000:8000"]
    environment:
      - PROFILE=dev
      - HOT_RELOAD=true
    volumes:
      - ./examples:/app/examples
    depends_on:
      - chromadb
      - redis
      - ollama
```

### **B. CLI Installer**

#### **Installation Script**
```bash
#!/bin/bash
# install.sh
echo "Installing GraphMind..."

# Check dependencies
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo "Docker is required but not installed."
        exit 1
    fi
}

# Download and setup
download_graphmind() {
    git clone https://github.com/username/graphmind.git
    cd graphmind
    cp .env.example .env
}

# Initialize
init_graphmind() {
    docker-compose -f docker-compose.core.yml up -d
    echo "GraphMind is running at http://localhost:8000"
}
```

---

## 📋 **7. Open Source Governance**

### **A. License & Legal**
- [ ] **LICENSE**: Apache 2.0 (permissive, commercial-friendly)
- [ ] **CONTRIBUTING.md**: Setup instructions, style guide, PR checklist
- [ ] **CODE_OF_CONDUCT.md**: Contributor Covenant
- [ ] **Issue Templates**: Bug, Feature, Documentation

### **B. Community Infrastructure**
- [ ] **GitHub Discussions**: Community forum
- [ ] **Discord Server**: Real-time chat
- [ ] **Documentation Site**: MkDocs Material
- [ ] **Example Gallery**: Community-contributed examples

### **C. CI/CD Pipeline**
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          docker-compose -f docker-compose.dev.yml up -d
          pytest tests/
      - name: Build Docker image
        run: |
          docker build -t graphmind:latest .
```

---

## 🎯 **8. Success Metrics**

### **A. Technical Metrics**
- [ ] **Modularity**: 90%+ code reuse across domains
- [ ] **Performance**: <15s response time p95
- [ ] **Reliability**: 99.9% uptime
- [ ] **Scalability**: Support 100+ concurrent users

### **B. Community Metrics**
- [ ] **GitHub Stars**: 1000+ within 6 months
- [ ] **Contributors**: 50+ active contributors
- [ ] **Examples**: 20+ domain examples
- [ ] **Documentation**: 95%+ coverage

### **C. Adoption Metrics**
- [ ] **Downloads**: 10,000+ Docker pulls
- [ ] **Forks**: 500+ repository forks
- [ ] **Issues**: Active community engagement
- [ ] **Discussions**: Regular community interaction

---

## 🚀 **9. Next Steps**

### **Immediate (This Week)**
1. **Repository Rename**: Update repository name and URLs
2. **Code Refactoring**: Remove trading-specific terminology
3. **Documentation Update**: Create new README and branding
4. **License Setup**: Add Apache 2.0 license

### **Short-term (Next 2 Weeks)**
1. **Modular Architecture**: Implement plugin system
2. **CLI Development**: Create researchai CLI
3. **Docker Profiles**: Set up different deployment profiles
4. **Example Domains**: Create finance, legal, health demos

### **Long-term (Next Month)**
1. **Community Launch**: Public announcement and launch
2. **Documentation Site**: Full MkDocs Material site
3. **Contributor Onboarding**: Guide and templates
4. **Ecosystem Growth**: Third-party connectors and adapters

---

**Status**: 🚀 **PHASE 1 TRANSFORMATION ACTIVE**  
**Target**: Transform TradingAI → GraphMind (Open RAG Framework)  
**Timeline**: 4 weeks to community-ready release  
**Next Review**: Weekly progress updates

