"""FastAPI application for EminiPlayer RAG service."""
import logging
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models import IngestRequest, IngestResponse, AskRequest, AskResponse, Citation
from app.ingest import PDFIngestor
from app.retrieval import HybridRetriever
from app.spec_extraction import SpecExtractor
from app.web_search import create_web_search_provider, EnhancedRAGWithWebSearch
from app.mcp_integration import create_mcp_client, EnhancedRAGWithMCP
from app.searxng_client import create_searxng_client, EnhancedRAGWithSearXNG
from app.obsidian_mcp_client import create_obsidian_client, EnhancedRAGWithObsidian

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
ingestor: PDFIngestor
retriever: HybridRetriever
spec_extractor: SpecExtractor
enhanced_rag: Optional[EnhancedRAGWithWebSearch] = None
mcp_rag: Optional[EnhancedRAGWithMCP] = None
searxng_rag: Optional[EnhancedRAGWithSearXNG] = None
obsidian_rag: Optional[EnhancedRAGWithObsidian] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    global ingestor, retriever, spec_extractor, enhanced_rag, mcp_rag, searxng_rag, obsidian_rag
    
    logger.info("Initializing high-performance RAG service...")
    ingestor = PDFIngestor()
    retriever = HybridRetriever()
    spec_extractor = SpecExtractor(retriever)
    
    # Initialize SearXNG integration (primary web search)
    import os
    searxng_url = os.getenv("SEARXNG_URL", "http://192.168.50.236:8888")
    searxng_client = create_searxng_client(searxng_url)
    if searxng_client:
        searxng_rag = EnhancedRAGWithSearXNG(retriever, searxng_client)
        logger.info(f"SearXNG integration enabled at {searxng_url}")
    
    # Initialize enhanced RAG with web search (fallback)
    web_search_provider = create_web_search_provider()
    if web_search_provider:
        enhanced_rag = EnhancedRAGWithWebSearch(retriever, web_search_provider)
        logger.info("Web search integration enabled")
    
    # Initialize MCP integration
    mcp_server_url = os.getenv("MCP_SERVER_URL")
    mcp_api_key = os.getenv("MCP_API_KEY")
    mcp_client = create_mcp_client(mcp_server_url, mcp_api_key)
    if mcp_client:
        mcp_rag = EnhancedRAGWithMCP(retriever, mcp_client)
        logger.info("MCP integration enabled")
    
    # Initialize Obsidian MCP integration
    obsidian_vault_path = os.getenv("OBSIDIAN_VAULT_PATH")
    obsidian_api_url = os.getenv("OBSIDIAN_API_URL", "https://localhost:27124")
    obsidian_api_key = os.getenv("OBSIDIAN_API_KEY")
    obsidian_client = create_obsidian_client(obsidian_vault_path, obsidian_api_url, obsidian_api_key)
    if obsidian_client:
        obsidian_rag = EnhancedRAGWithObsidian(retriever, obsidian_client)
        logger.info(f"Obsidian MCP integration enabled at {obsidian_vault_path}")
    
    logger.info("High-performance RAG service initialized successfully")
    
    yield
    
    logger.info("Shutting down...")


app = FastAPI(
    title="EminiPlayer RAG Service",
    description="RAG service for EminiPlayer PDFs with spec extraction",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://localhost:3000", "https://emini.riffyx.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {"status": "online", "service": "EminiPlayer RAG"}


@app.post("/ingest", response_model=IngestResponse)
async def ingest_pdfs(request: IngestRequest):
    """
    Ingest PDFs from /workspace/pdfs directory.
    
    Uses Docling with OCR fallback, chunks documents, and indexes into Chroma.
    """
    try:
        logger.info(f"Starting ingestion (force_reindex={request.force_reindex})")
        result = ingestor.ingest_all(force_reindex=request.force_reindex)
        
        return IngestResponse(
            status="success",
            processed_files=result["processed_files"],
            total_chunks=result["total_chunks"],
            message=f"Successfully ingested {result['processed_files']} PDFs"
        )
    except Exception as e:
        logger.error(f"Ingestion error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    """
    Answer questions with citations or extract YAML spec.
    
    - mode="qa": Returns answer with citations
    - mode="spec": Extracts strategy spec as YAML
    """
    try:
        if request.mode == "spec":
            result = spec_extractor.extract_spec(
                query=request.query,
                top_k=request.top_k
            )
            return AskResponse(
                query=request.query,
                answer=result["answer"],
                citations=result["citations"],
                mode="spec",
                spec_file=result.get("spec_file")
            )
        else:
            result = retriever.answer_query(
                query=request.query,
                top_k=request.top_k
            )
            return AskResponse(
                query=request.query,
                answer=result["answer"],
                citations=result["citations"],
                mode="qa"
            )
    except Exception as e:
        logger.error(f"Query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask-enhanced", response_model=AskResponse)
async def ask_enhanced_question(request: AskRequest):
    """Ask a question with enhanced web search and real-time data via SearXNG."""
    try:
        # Use SearXNG if available, otherwise fall back to standard search
        if searxng_rag:
            result = searxng_rag.search_with_web_context(request.query, include_web=True)
            
            # Generate answer using enhanced context
            doc_context = "\n".join([r['text'] for r in result["document_results"]])
            web_context = "\n".join([r['content'] for r in result["web_results"]])
            
            combined_context = f"DOCUMENT CONTEXT:\n{doc_context}\n\nREAL-TIME WEB CONTEXT:\n{web_context}"
            
            # Generate answer using production LLM
            answer = retriever._generate_answer(request.query, combined_context)
            
            # Combine citations
            doc_citations = [
                Citation(
                    text=r['text'][:200] + "...",
                    doc_id=r['metadata'].get('doc_id', 'unknown'),
                    page=r['metadata'].get('page'),
                    section=r['metadata'].get('section'),
                    score=r['rerank_score']
                )
                for r in result["document_results"]
            ]
            
            web_citations = [
                Citation(
                    text=r['content'][:200] + "...",
                    doc_id=f"web_{i}",
                    page=None,
                    section=r['title'],
                    score=r['score']
                )
                for i, r in enumerate(result["web_results"])
            ]
            
            all_citations = doc_citations + web_citations
            
            return AskResponse(
                query=request.query,
                answer=answer,
                citations=all_citations,
                mode="enhanced",
                web_enabled=True,
                total_sources=result["total_sources"]
            )
        else:
            # Fallback to standard search
            result = retriever.answer_query(
                query=request.query,
                top_k=request.top_k
            )
            return AskResponse(
                query=request.query,
                answer=result["answer"],
                citations=result["citations"],
                mode="qa",
                web_enabled=False
            )
            
    except Exception as e:
        logger.error(f"Enhanced ask failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask-obsidian", response_model=AskResponse)
async def ask_obsidian_question(request: AskRequest):
    """Ask a question with enhanced personal knowledge from Obsidian notes."""
    try:
        # Use Obsidian if available, otherwise fall back to standard search
        if obsidian_rag:
            result = await obsidian_rag.search_with_personal_knowledge(request.query, include_obsidian=True)
            
            # Generate answer using enhanced context
            doc_context = "\n".join([r['text'] for r in result["document_results"]])
            obsidian_context = "\n".join([r['text'] for r in result["obsidian_results"]])
            
            combined_context = f"DOCUMENT CONTEXT:\n{doc_context}\n\nPERSONAL KNOWLEDGE (OBSIDIAN):\n{obsidian_context}"
            
            # Generate answer using production LLM
            answer = retriever._generate_answer(request.query, combined_context)
            
            # Combine citations
            doc_citations = [
                Citation(
                    text=r['text'][:200] + "...",
                    doc_id=r['metadata'].get('doc_id', 'unknown'),
                    page=r['metadata'].get('page'),
                    section=r['metadata'].get('section'),
                    score=r['rerank_score']
                )
                for r in result["document_results"]
            ]
            
            obsidian_citations = [
                Citation(
                    text=r['text'][:200] + "...",
                    doc_id=r['metadata'].get('doc_id', 'unknown'),
                    page=None,
                    section=r['metadata'].get('title', 'Obsidian Note'),
                    score=r['score']
                )
                for r in result["obsidian_results"]
            ]
            
            all_citations = doc_citations + obsidian_citations
            
            return AskResponse(
                query=request.query,
                answer=answer,
                citations=all_citations,
                mode="obsidian",
                web_enabled=False,
                total_sources=result["total_sources"]
            )
        else:
            # Fallback to standard search
            result = retriever.answer_query(
                query=request.query,
                top_k=request.top_k
            )
            return AskResponse(
                query=request.query,
                answer=result["answer"],
                citations=result["citations"],
                mode="qa",
                web_enabled=False
            )
            
    except Exception as e:
        logger.error(f"Obsidian ask failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats")
async def get_stats():
    """Get database statistics."""
    try:
        stats = retriever.get_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Stats error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/ollama/models")
async def get_ollama_models():
    """Get available Ollama models."""
    try:
        import requests
        import os
        
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        response = requests.get(f"{ollama_url}/api/tags", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return JSONResponse(content=data)
        else:
            # Return a default set of models if Ollama is not available
            default_models = {
                "models": [
                    {
                        "name": "qwen2.5-coder:14b",
                        "size": 8000000000,
                        "modified_at": "2024-01-01T00:00:00Z",
                        "digest": "sha256:default",
                        "details": {
                            "format": "gguf",
                            "family": "qwen",
                            "families": ["qwen"],
                            "parameter_size": "14B",
                            "quantization_level": "Q4_K_M"
                        }
                    },
                    {
                        "name": "llama3.1:latest",
                        "size": 4000000000,
                        "modified_at": "2024-01-01T00:00:00Z",
                        "digest": "sha256:default",
                        "details": {
                            "format": "gguf",
                            "family": "llama",
                            "families": ["llama"],
                            "parameter_size": "8B",
                            "quantization_level": "Q4_K_M"
                        }
                    }
                ]
            }
            return JSONResponse(content=default_models)
            
    except Exception as e:
        logger.error(f"Ollama models error: {e}")
        # Return default models on error
        default_models = {
            "models": [
                {
                    "name": "qwen2.5-coder:14b",
                    "size": 8000000000,
                    "modified_at": "2024-01-01T00:00:00Z",
                    "digest": "sha256:default",
                    "details": {
                        "format": "gguf",
                        "family": "qwen",
                        "families": ["qwen"],
                        "parameter_size": "14B",
                        "quantization_level": "Q4_K_M"
                    }
                }
            ]
        }
        return JSONResponse(content=default_models)


@app.post("/ollama/generate")
async def generate_with_ollama(request: dict):
    """Generate text using Ollama."""
    try:
        import requests
        import os
        
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")
        response = requests.post(
            f"{ollama_url}/api/generate",
            json=request,
            timeout=30
        )
        
        if response.status_code == 200:
            return JSONResponse(content=response.json())
        else:
            raise HTTPException(status_code=response.status_code, detail="Ollama generation failed")
            
    except Exception as e:
        logger.error(f"Ollama generate error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(content={"status": "healthy", "service": "eminiplayer-rag"})
