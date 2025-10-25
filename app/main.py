"""FastAPI application for TradingAI Research Platform."""
import logging
import time
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Form, Depends, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.models import IngestRequest, IngestResponse, AskRequest, AskResponse, Citation
from app.auth import auth_manager, get_current_user, require_admin
from app.ingest import PDFIngestor
from app.retrieval import HybridRetriever
from app.spec_extraction import SpecExtractor
from app.web_search import create_web_search_provider, EnhancedRAGWithWebSearch
from app.mcp_integration import create_mcp_client, EnhancedRAGWithMCP
from app.searxng_client import create_searxng_client, EnhancedRAGWithSearXNG
from app.obsidian_mcp_client import create_obsidian_client, EnhancedRAGWithObsidian
from app.query_generator import IntelligentQueryGenerator, EnhancedWebSearch
from app.research_engine import ComprehensiveResearchSystem
from app.web_parser import WebPageParser, EnhancedWebSearch as ParsedWebSearch
from app.memory_system import UserMemory, MemoryAwareRAG
from app.system_prompt_manager import system_prompt_manager
from app.user_prompt_manager import user_prompt_manager
from app.monitoring import monitor
from app.caching import query_cache, redis_query_cache
from app.model_selector import model_selector
from app.retrieval_optimizer import retrieval_optimizer
from app.query_analyzer import query_analyzer
from app.advanced_retrieval import AdvancedHybridRetriever
from app.query_expansion import query_expander
from app.advanced_reranking import advanced_reranker
from app.context_compression import context_compressor
from app.metadata_enhancement import metadata_enhancer

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
query_generator: Optional[IntelligentQueryGenerator] = None
enhanced_web_search: Optional[EnhancedWebSearch] = None
comprehensive_research: Optional[ComprehensiveResearchSystem] = None
user_memory: Optional[UserMemory] = None
memory_aware_rag: Optional[MemoryAwareRAG] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    global ingestor, retriever, advanced_retriever, spec_extractor, enhanced_rag, mcp_rag, searxng_rag, obsidian_rag, query_generator, enhanced_web_search, comprehensive_research, user_memory, memory_aware_rag
    
    logger.info("Initializing high-performance RAG service...")
    ingestor = PDFIngestor()
    retriever = HybridRetriever()
    
    # Initialize advanced retriever
    import chromadb
    from sentence_transformers import SentenceTransformer
    import os
    
    chroma_url = os.getenv("CHROMA_URL", "http://chromadb:8000")
    chroma_client = chromadb.HttpClient(host=chroma_url.split("://")[1].split(":")[0], port=int(chroma_url.split(":")[-1]))
    embedding_model = SentenceTransformer('BAAI/bge-m3')
    advanced_retriever = AdvancedHybridRetriever(chroma_client, embedding_model)
    
    # Load existing documents for advanced processing
    await advanced_retriever.load_existing_documents()
    logger.info("Advanced hybrid retriever initialized with existing documents")
    
    spec_extractor = SpecExtractor(retriever)
    
    # Initialize intelligent query generator
    query_generator = IntelligentQueryGenerator()
    logger.info("Intelligent query generator initialized")
    
    # Initialize SearXNG integration (primary web search)
    import os
    searxng_url = os.getenv("SEARXNG_URL", "http://searxng:8080")
    searxng_client = create_searxng_client(searxng_url)
    if searxng_client:
        searxng_rag = EnhancedRAGWithSearXNG(retriever, searxng_client)
        enhanced_web_search = EnhancedWebSearch(searxng_client, query_generator)
        comprehensive_research = ComprehensiveResearchSystem(retriever, searxng_client, query_generator)
        logger.info(f"SearXNG integration enabled at {searxng_url}")
        logger.info("Enhanced web search with intelligent query generation enabled")
        logger.info("Comprehensive research system enabled")
    
    # Initialize user memory system
    user_memory = UserMemory()
    memory_aware_rag = MemoryAwareRAG(retriever, user_memory)
    logger.info("User memory system enabled")
    
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
    title="TradingAI Research Platform API",
    description="Comprehensive AI research platform with RAG, web search, Obsidian integration, and intelligent query generation",
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
    return {"status": "online", "service": "TradingAI Research Platform"}


# Authentication endpoints
@app.post("/auth/login")
async def login(username: str = Form(...), password: str = Form(...)):
    """Login endpoint to get access token."""
    user = auth_manager.authenticate_user(username, password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect username or password"
        )
    
    access_token = auth_manager.create_access_token(data={"sub": user["username"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "username": user["username"],
            "is_admin": user["is_admin"]
        }
    }

@app.get("/auth/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    return {
        "username": current_user["username"],
        "is_admin": current_user["is_admin"],
        "created_at": current_user["created_at"]
    }

@app.post("/auth/change-password")
async def change_password(
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """Change user password."""
    current_password = request.get("current_password")
    new_password = request.get("new_password")
    
    if not current_password or not new_password:
        raise HTTPException(
            status_code=400,
            detail="Current password and new password are required"
        )
    
    if len(new_password) < 6:
        raise HTTPException(
            status_code=400,
            detail="New password must be at least 6 characters long"
        )
    
    success = auth_manager.change_password(
        current_user["username"],
        current_password,
        new_password
    )
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Current password is incorrect"
        )
    
    return {
        "success": True,
        "message": "Password changed successfully"
    }

@app.post("/upload")
async def upload_document(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload a document to the documents directory for ingestion."""
    try:
        from pathlib import Path
        
        # Save to documents directory
        documents_dir = Path("/workspace/documents")
        documents_dir.mkdir(exist_ok=True, parents=True)
        
        # Generate unique filename
        filename = f"{int(time.time())}_{file.filename}"
        file_path = documents_dir / filename
        
        # Save file
        content = await file.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        
        logger.info(f"Uploaded document: {filename} to {file_path}")
        return {
            "success": True,
            "message": f"Document uploaded successfully: {filename}",
            "filename": filename,
            "path": str(file_path)
        }
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ingest", response_model=IngestResponse)
async def ingest_pdfs(request: IngestRequest, current_user: dict = Depends(get_current_user)):
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
async def ask_question(request: AskRequest, current_user: dict = Depends(get_current_user)):
    """
    Answer questions with citations or extract YAML spec.
    
    - mode="qa": Returns answer with citations
    - mode="spec": Extracts strategy spec as YAML
    """
    start_time = time.time()
    
    try:
        # Smart model selection (can be disabled for testing)
        if request.disable_model_override:
            selected_model = request.model
            logger.info(f"Model override disabled - using requested: {selected_model}")
        else:
            # Use query analyzer for more intelligent model selection
            analysis = query_analyzer.analyze(request.query)
            selected_model = analysis.suggested_model
            if request.model != selected_model:
                logger.info(f"Model auto-selected: {selected_model} (requested: {request.model}) - complexity: {analysis.complexity_level}")
        
        # Check cache first (only for qa mode)
        if request.mode == "qa":
            cached_response = redis_query_cache.get(
                query=request.query,
                model=selected_model,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                mode=request.mode
            )
            
            if cached_response:
                logger.info("Cache hit - returning cached response")
                response_time = time.time() - start_time
                monitor.track_query(
                    query=request.query,
                    model=selected_model,
                    response_time=response_time,
                    query_type="cached",
                    success=True
                )
                # Extract the actual response from the cached data
                actual_response = cached_response.get('response', cached_response)
                return AskResponse(**actual_response)
        
        if request.mode == "spec":
            result = await spec_extractor.extract_spec(
                query=request.query,
                top_k=request.top_k
            )
            response_time = time.time() - start_time
            monitor.track_query(
                query=request.query,
                model=selected_model,
                response_time=response_time,
                query_type="spec",
                success=True
            )
            return AskResponse(
                query=request.query,
                answer=result["answer"],
                citations=result["citations"],
                sources=result["citations"],  # Frontend compatibility
                mode="spec",
                spec_file=result.get("spec_file")
            )
        else:
            # Convert conversation history to the format expected by retrieval
            conversation_history = None
            if request.conversation_history:
                conversation_history = [
                    {"role": msg.role, "content": msg.content} 
                    for msg in request.conversation_history
                ]
            
            # Use memory-aware RAG if available
            if memory_aware_rag:
                # Get optimized retrieval parameters based on query complexity
                analysis = query_analyzer.analyze(request.query)
                retrieval_params = analysis.suggested_retrieval_params
                
                # Use dynamic parameters or fall back to request parameters
                doc_results = await retriever.retrieve_async(
                    request.query, 
                    top_k=retrieval_params.get('top_k', request.top_k),
                    bm25_top_k=retrieval_params.get('bm25_top_k', request.bm25_top_k),
                    embedding_top_k=retrieval_params.get('embedding_top_k', request.embedding_top_k),
                    rerank_top_k=retrieval_params.get('rerank_top_k', request.rerank_top_k)
                )
                combined_context = "\n".join([r['text'] for r in doc_results])
                
                # Get system prompt for RAG mode
                user_id = current_user.get("username", "anonymous")
                system_prompt = user_prompt_manager.get_prompt_with_fallback(
                    user_id, "rag_only", system_prompt_manager.get_prompt("rag_only")
                )
                
                # Generate with memory
                answer = memory_aware_rag.generate_with_memory(
                    user_id, 
                    request.query, 
                    combined_context, 
                    conversation_history,
                    selected_model,  # Use selected model
                    request.temperature,
                    request.max_tokens,
                    request.top_k_sampling
                )
                
                # Create citations with proper source formatting
                citations = []
                for r in doc_results:
                    # Get document type for better source display
                    doc_type = r['metadata'].get('doc_type', 'Document')
                    file_name = r['metadata'].get('file_name', 'Unknown')
                    
                    # Format source based on document type
                    if doc_type == 'video_transcript':
                        source_display = f"Video: {file_name}"
                    elif doc_type == 'pdf':
                        source_display = f"PDF: {file_name}"
                    elif doc_type == 'text_document':
                        source_display = f"Document: {file_name}"
                    elif doc_type == 'llm_processed':
                        source_display = f"AI Processed: {file_name}"
                    else:
                        source_display = f"{doc_type.title()}: {file_name}"
                    
                    citations.append(Citation(
                        text=r['text'][:200] + "...",
                        doc_id=r['metadata'].get('doc_id') or r['metadata'].get('file_name', 'unknown'),
                        page=r['metadata'].get('page'),
                        section=source_display,
                        score=r['rerank_score']
                    ))
                
                result = {
                    "answer": answer,
                    "citations": citations,
                    "sources": citations  # Frontend compatibility
                }
            else:
                # Get optimized retrieval parameters based on query complexity
                analysis = query_analyzer.analyze(request.query)
                retrieval_params = analysis.suggested_retrieval_params
                
                result = retriever.answer_query(
                    query=request.query,
                    top_k=retrieval_params.get('top_k', request.top_k),
                    conversation_history=conversation_history,
                    model=selected_model,  # Use selected model
                    bm25_top_k=retrieval_params.get('bm25_top_k', request.bm25_top_k),
                    embedding_top_k=retrieval_params.get('embedding_top_k', request.embedding_top_k),
                    rerank_top_k=retrieval_params.get('rerank_top_k', request.rerank_top_k)
                )
                
                # Fix source formatting for non-memory-aware RAG
                if 'citations' in result and result['citations']:
                    formatted_citations = []
                    for citation in result['citations']:
                        # Get document type for better source display
                        doc_type = getattr(citation, 'doc_type', 'Document')
                        file_name = citation.doc_id
                        
                        # Format source based on document type
                        if 'video' in doc_type.lower() or 'transcript' in doc_type.lower():
                            source_display = f"Video: {file_name}"
                        elif 'pdf' in doc_type.lower():
                            source_display = f"PDF: {file_name}"
                        elif 'text' in doc_type.lower():
                            source_display = f"Document: {file_name}"
                        elif 'llm' in doc_type.lower():
                            source_display = f"AI Processed: {file_name}"
                        else:
                            source_display = f"{doc_type.title()}: {file_name}"
                        
                        # Create new citation with proper source
                        formatted_citations.append(Citation(
                            text=citation.text,
                            doc_id=citation.doc_id,
                            page=citation.page,
                            section=source_display,
                            score=citation.score
                        ))
                    
                    result['citations'] = formatted_citations
                    result['sources'] = formatted_citations
            
            # Cache the response - convert Citation objects to dicts for JSON serialization
            def serialize_citations(citations):
                if isinstance(citations, list):
                    return [citation.dict() if hasattr(citation, 'dict') else citation for citation in citations]
                return citations
            
            response_data = {
                "query": request.query,
                "answer": result["answer"],
                "citations": serialize_citations(result["citations"]),
                "sources": serialize_citations(result.get("sources", result["citations"])),  # Frontend compatibility
                "mode": "qa"
            }
            redis_query_cache.set(
                query=request.query,
                model=selected_model,
                response=response_data,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                mode=request.mode
            )
            
            # Track performance
            response_time = time.time() - start_time
            monitor.track_query(
                query=request.query,
                model=selected_model,
                response_time=response_time,
                query_type="normal",
                success=True
            )
            
            return AskResponse(
                query=request.query,
                answer=result["answer"],
                citations=result["citations"],
                sources=result.get("sources", result["citations"]),  # Frontend compatibility
                mode="qa"
            )
    except Exception as e:
        response_time = time.time() - start_time
        monitor.track_query(
            query=request.query,
            model=request.model,
            response_time=response_time,
            query_type="error",
            success=False
        )
        logger.error(f"Query error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask-enhanced", response_model=AskResponse)
async def ask_enhanced_question(request: AskRequest, current_user: dict = Depends(get_current_user)):
    """Ask a question with enhanced web search using intelligent query generation."""
    try:
        # Use enhanced web search with intelligent query generation if available
        if enhanced_web_search:
            # Prepare conversation history
            conversation_history = None
            if request.conversation_history:
                conversation_history = [
                    {"role": msg.role, "content": msg.content} 
                    for msg in request.conversation_history
                ]
            
            # Perform intelligent web search
            web_search_result = enhanced_web_search.search_with_intelligent_queries(
                request.query, 
                conversation_history,
                web_search_results=request.web_search_results,
                web_pages_to_parse=request.web_pages_to_parse
            )
            
            # Debug logging
            logger.info(f"Web search result type: {type(web_search_result)}")
            logger.info(f"Web search result keys: {web_search_result.keys() if isinstance(web_search_result, dict) else 'Not a dict'}")
            if "results" in web_search_result:
                logger.info(f"Results type: {type(web_search_result['results'])}")
                logger.info(f"Results length: {len(web_search_result['results'])}")
                if web_search_result['results']:
                    logger.info(f"First result type: {type(web_search_result['results'][0])}")
                    logger.info(f"First result: {web_search_result['results'][0]}")
            
            # WEB SEARCH ONLY MODE - No document retrieval
            # Generate answer using ONLY web context (no documents)
            web_results = web_search_result.get("results", [])
            web_context = "\n".join([
                r.get('content', '') if isinstance(r, dict) else str(r) 
                for r in web_results
            ])
            
            combined_context = f"REAL-TIME WEB CONTEXT:\n{web_context}"
            
            # Get system prompt for web search mode
            user_id = current_user.get("username", "anonymous")
            system_prompt = user_prompt_manager.get_prompt_with_fallback(
                user_id, "web_search_only", system_prompt_manager.get_prompt("web_search_only")
            )
            
            # Generate answer using production LLM
            answer = retriever._generate_answer(
                request.query, 
                combined_context, 
                conversation_history, 
                request.model, 
                system_prompt,
                request.temperature,
                request.max_tokens,
                request.top_k_sampling
            )
            
            # Only web citations (no document citations)
            web_results = web_search_result.get("results", [])
            logger.info(f"Processing {len(web_results)} web results for citations")
            
            web_citations = []
            for i, r in enumerate(web_results):
                try:
                    logger.info(f"Processing result {i}: type={type(r)}, content={str(r)[:100]}...")
                    if isinstance(r, dict):
                        citation = Citation(
                            text=r.get('content', r.get('title', ''))[:200] + "...",
                            doc_id=f"web_{i}",
                            page=None,
                            section=r.get('title', 'Web Source'),
                            score=r.get('score', 0.5)
                        )
                        web_citations.append(citation)
                    else:
                        logger.warning(f"Result {i} is not a dict: {type(r)}")
                except Exception as e:
                    logger.error(f"Error processing result {i}: {e}")
                    continue
            
            all_citations = web_citations
            
            return AskResponse(
                query=request.query,
                answer=answer,
                citations=all_citations,
                mode="enhanced",
                web_enabled=True,
                total_sources=len(web_search_result["results"]),
                search_metadata={
                    "generated_queries": web_search_result.get("generated_queries", []),
                    "entities_found": web_search_result.get("entities_found", []),
                    "total_queries": web_search_result.get("total_queries", 0),
                    "successful_queries": web_search_result.get("successful_queries", 0)
                }
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


@app.post("/generate-search-queries")
async def generate_search_queries(request: AskRequest, current_user: dict = Depends(get_current_user)):
    """Generate intelligent search queries for a given prompt."""
    try:
        if not query_generator:
            raise HTTPException(status_code=503, detail="Query generator not available")
        
        # Prepare conversation history
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content} 
                for msg in request.conversation_history
            ]
        
        # Generate search queries
        search_queries = query_generator.generate_search_queries(request.query, conversation_history)
        
        return {
            "query": request.query,
            "generated_queries": [
                {
                    "query": sq.query,
                    "intent": sq.intent,
                    "entities": sq.entities,
                    "search_type": sq.search_type,
                    "priority": sq.priority,
                    "context": sq.context
                }
                for sq in search_queries
            ],
            "total_queries": len(search_queries)
        }
        
    except Exception as e:
        logger.error(f"Query generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask-research", response_model=AskResponse)
async def ask_research_question(request: AskRequest, current_user: dict = Depends(get_current_user)):
    """Ask a question with comprehensive research capabilities."""
    try:
        # Use comprehensive research system if available
        if comprehensive_research:
            # Prepare conversation history
            conversation_history = None
            if request.conversation_history:
                conversation_history = [
                    {"role": msg.role, "content": msg.content} 
                    for msg in request.conversation_history
                ]
            
            # Conduct comprehensive research
            research_result = await comprehensive_research.conduct_comprehensive_research(
                request.query, 
                conversation_history
            )
            
            # Generate answer using research-specific LLM
            answer = comprehensive_research.research_engine.generate_research_response(
                request.query, 
                research_result, 
                conversation_history
            )
            
            # Combine citations
            doc_citations = [
                Citation(
                    text=r['text'][:200] + "...",
                    doc_id=r['metadata'].get('doc_id') or r['metadata'].get('file_name', 'unknown'),
                    page=r['metadata'].get('page'),
                    section=r['metadata'].get('section') or r['metadata'].get('doc_type', 'unknown'),
                    score=r['rerank_score']
                )
                for r in research_result["document_results"]
            ]
            
            web_citations = [
                Citation(
                    text=r.get('content', r.get('title', ''))[:200] + "...",
                    doc_id=f"web_{i}",
                    page=None,
                    section=r.get('title', 'Web Source'),
                    score=r.get('score', 0.5)
                )
                for i, r in enumerate(research_result["web_results"])
            ]
            
            all_citations = doc_citations + web_citations
            
            return AskResponse(
                query=request.query,
                answer=answer,
                citations=all_citations,
                mode="research",
                web_enabled=True,
                total_sources=len(research_result["document_results"]) + len(research_result["web_results"]),
                search_metadata={
                    "research_queries": research_result.get('research_queries', []),
                    "research_metadata": research_result.get('research_metadata', {}),
                    "total_queries": research_result.get('research_metadata', {}).get('total_queries', 0),
                    "successful_queries": research_result.get('research_metadata', {}).get('successful_queries', 0)
                }
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
        logger.error(f"Research query failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test-research-models")
async def test_research_models(request: AskRequest, current_user: dict = Depends(get_current_user)):
    """Test different LLM models for research tasks."""
    try:
        if not comprehensive_research:
            raise HTTPException(status_code=503, detail="Research system not available")
        
        # Prepare conversation history
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content} 
                for msg in request.conversation_history
            ]
        
        # Conduct research
        research_result = await comprehensive_research.conduct_comprehensive_research(
            request.query, 
            conversation_history
        )
        
        # Test different models
        models_to_test = [
            ("gpt-oss:20b", "GPT-OSS 20B - Best for complex analysis"),
            ("deepseek-r1:14b", "DeepSeek R1 14B - Great for research"),
            ("gemma3:12b", "Gemma3 12B - Good for writing"),
            ("llama3.1:latest", "Llama3.1 8B - Balanced performance"),
            ("qwen2.5-coder:14b", "Qwen2.5 Coder 14B - Current RAG model")
        ]
        
        results = {}
        
        for model_name, description in models_to_test:
            try:
                # Create temporary Ollama client for this model
                from app.ollama_client import OllamaClient
                temp_ollama = OllamaClient(default_model=model_name)
                
                # Generate response
                response = comprehensive_research.research_engine.generate_research_response(
                    request.query, 
                    research_result, 
                    conversation_history
                )
                
                results[model_name] = {
                    "description": description,
                    "response": response[:500] + "..." if len(response) > 500 else response,
                    "length": len(response),
                    "status": "success"
                }
                
            except Exception as e:
                results[model_name] = {
                    "description": description,
                    "error": str(e),
                    "status": "failed"
                }
        
        return {
            "query": request.query,
            "research_data_available": len(research_result.get("document_results", [])) + len(research_result.get("web_results", [])),
            "model_comparisons": results
        }
        
    except Exception as e:
        logger.error(f"Model testing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# System Prompt Management Endpoints
@app.get("/system-prompts")
async def get_system_prompts(current_user: dict = Depends(get_current_user)):
    """Get all available system prompts."""
    try:
        prompts = system_prompt_manager.list_prompts()
        return {"prompts": prompts}
    except Exception as e:
        logger.error(f"Failed to get system prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/system-prompts/{mode}")
async def get_system_prompt(mode: str, current_user: dict = Depends(get_current_user)):
    """Get system prompt for a specific mode."""
    try:
        prompt_info = system_prompt_manager.get_prompt_info(mode)
        return prompt_info
    except Exception as e:
        logger.error(f"Failed to get system prompt for {mode}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/system-prompts/{mode}")
async def update_system_prompt(mode: str, request: dict, current_user: dict = Depends(get_current_user)):
    """Update system prompt for a mode."""
    try:
        prompt = request.get("prompt", "")
        version = request.get("version", "latest")
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # Validate prompt
        validation = system_prompt_manager.validate_prompt(prompt)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=f"Invalid prompt: {validation['issues']}")
        
        success = system_prompt_manager.update_prompt(mode, prompt, version)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update prompt")
        
        return {"message": "Prompt updated successfully", "validation": validation}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update system prompt for {mode}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/system-prompts/{mode}/reset")
async def reset_system_prompt(mode: str, current_user: dict = Depends(get_current_user)):
    """Reset system prompt to default."""
    try:
        success = system_prompt_manager.reset_to_default(mode)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to reset prompt")
        
        return {"message": "Prompt reset to default successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset system prompt for {mode}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# User Prompt Management Endpoints
@app.get("/user-prompts")
async def get_user_prompts(current_user: dict = Depends(get_current_user)):
    """Get user's custom prompts."""
    try:
        user_id = current_user.get("username", "anonymous")
        prompts = user_prompt_manager.get_user_prompts(user_id)
        return {"prompts": prompts}
    except Exception as e:
        logger.error(f"Failed to get user prompts: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/user-prompts/{mode}")
async def get_user_prompt(mode: str, current_user: dict = Depends(get_current_user)):
    """Get user's custom prompt for a specific mode."""
    try:
        user_id = current_user.get("username", "anonymous")
        prompt = user_prompt_manager.get_user_prompt(user_id, mode)
        if prompt:
            return {"prompt": prompt}
        else:
            # Return default system prompt if no custom prompt exists
            default_prompt = system_prompt_manager.get_prompt(mode)
            return {"prompt": default_prompt, "is_default": True}
    except Exception as e:
        logger.error(f"Failed to get user prompt for {mode}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/user-prompts/{mode}")
async def set_user_prompt(mode: str, request: dict, current_user: dict = Depends(get_current_user)):
    """Set user's custom prompt for a mode."""
    try:
        user_id = current_user.get("username", "anonymous")
        prompt = request.get("prompt", "")
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        # Validate prompt
        validation = system_prompt_manager.validate_prompt(prompt)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=f"Invalid prompt: {validation['issues']}")
        
        success = user_prompt_manager.set_user_prompt(user_id, mode, prompt)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to save user prompt")
        
        return {"message": "User prompt saved successfully", "validation": validation}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save user prompt for {mode}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/user-prompts/{mode}")
async def reset_user_prompt(mode: str, current_user: dict = Depends(get_current_user)):
    """Reset user's custom prompt to default."""
    try:
        user_id = current_user.get("username", "anonymous")
        success = user_prompt_manager.reset_user_prompt(user_id, mode)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to reset user prompt")
        
        return {"message": "User prompt reset to default successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to reset user prompt for {mode}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-chat-title")
async def generate_chat_title(request: dict, current_user: dict = Depends(get_current_user)):
    """Generate a meaningful chat title using LLM."""
    try:
        message = request.get("message", "")
        if not message:
            return {"title": "New Chat"}
        
        # Use llama3.2 for title generation
        from app.ollama_client import OllamaClient
        ollama = OllamaClient(default_model="llama3.2:latest")
        
        prompt = f"""Generate a concise, descriptive title for a chat conversation that starts with this message:

"{message}"

Requirements:
- Keep it under 40 characters
- Be specific and meaningful
- Focus on the main topic or question
- Use title case
- No quotes or special characters

Title:"""

        title = ollama.generate(
            prompt=prompt,
            model="llama3.2:latest",
            temperature=0.3,
            max_tokens=50,
            timeout=30
        )
        
        # Clean up the title
        title = title.strip().replace('"', '').replace("'", '')
        if len(title) > 40:
            title = title[:37] + "..."
        
        return {"title": title or "New Chat"}
        
    except Exception as e:
        logger.error(f"Chat title generation failed: {e}")
        return {"title": "New Chat"}


@app.get("/memory/profile/{user_id}")
async def get_user_profile(user_id: str, current_user: dict = Depends(get_current_user)):
    """Get user memory profile."""
    try:
        if not user_memory:
            raise HTTPException(status_code=503, detail="Memory system not available")
        
        profile = user_memory.get_user_profile(user_id)
        return profile
        
    except Exception as e:
        logger.error(f"Failed to get user profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/memory/preference/{user_id}")
async def store_user_preference(user_id: str, request: dict, current_user: dict = Depends(get_current_user)):
    """Store a user preference."""
    try:
        if not user_memory:
            raise HTTPException(status_code=503, detail="Memory system not available")
        
        key = request.get("key")
        value = request.get("value")
        
        if not key or value is None:
            raise HTTPException(status_code=400, detail="Key and value are required")
        
        success = user_memory.store_preference(user_id, key, value)
        return {"success": success}
        
    except Exception as e:
        logger.error(f"Failed to store preference: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/insights/{user_id}")
async def get_user_insights(user_id: str, category: str = "general", limit: int = 10, current_user: dict = Depends(get_current_user)):
    """Get user insights."""
    try:
        if not user_memory:
            raise HTTPException(status_code=503, detail="Memory system not available")
        
        insights = user_memory.get_key_insights(user_id, category, limit)
        return {"insights": insights}
        
    except Exception as e:
        logger.error(f"Failed to get insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/memory/clear/{category}")
async def clear_memory_category(category: str, current_user: dict = Depends(get_current_user)):
    """Clear all insights for a specific category."""
    try:
        if not user_memory:
            raise HTTPException(status_code=503, detail="Memory system not available")
        
        user_id = current_user.get("username", "anonymous")
        success = user_memory.clear_category(user_id, category)
        
        if success:
            return {"message": f"Cleared all insights for category: {category}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to clear category")
        
    except Exception as e:
        logger.error(f"Failed to clear category {category}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ask-obsidian", response_model=AskResponse)
async def ask_obsidian_question(request: AskRequest, current_user: dict = Depends(get_current_user)):
    """Ask a question with enhanced personal knowledge from Obsidian notes."""
    try:
        # Use Obsidian if available, otherwise fall back to standard search
        if obsidian_rag:
            # OBSIDIAN ONLY MODE - No document retrieval
            result = await obsidian_rag.search_obsidian_only(request.query)
            
            # Generate answer using ONLY Obsidian context (no documents)
            obsidian_context = "\n".join([r['text'] for r in result["obsidian_results"]])
            
            combined_context = f"PERSONAL KNOWLEDGE (OBSIDIAN):\n{obsidian_context}"
            
            # Prepare conversation history
            conversation_history = None
            if request.conversation_history:
                conversation_history = [
                    {"role": msg.role, "content": msg.content} 
                    for msg in request.conversation_history
                ]
            
            # Get system prompt for Obsidian mode
            user_id = current_user.get("username", "anonymous")
            system_prompt = user_prompt_manager.get_prompt_with_fallback(
                user_id, "obsidian_only", system_prompt_manager.get_prompt("obsidian_only")
            )
            
            # Generate answer using production LLM
            answer = retriever._generate_answer(
                request.query, 
                combined_context, 
                conversation_history, 
                request.model, 
                system_prompt,
                request.temperature,
                request.max_tokens,
                request.top_k_sampling
            )
            
            # Only Obsidian citations (no document citations)
            obsidian_citations = [
                Citation(
                    text=r['text'][:200] + "...",
                    doc_id=r['metadata'].get('doc_id') or r['metadata'].get('file_name', 'unknown'),
                    page=None,
                    section=r['metadata'].get('title', 'Obsidian Note'),
                    score=r['score']
                )
                for r in result["obsidian_results"]
            ]
            
            all_citations = obsidian_citations
            
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
async def get_stats(current_user: dict = Depends(get_current_user)):
    """Get database statistics."""
    try:
        stats = retriever.get_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Stats error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Monitoring endpoints
@app.get("/monitoring/performance")
async def get_performance_metrics():
    """Get current performance metrics."""
    return monitor.get_summary()

@app.get("/monitoring/cache")
async def get_cache_metrics():
    """Get cache statistics."""
    return redis_query_cache.get_stats()

@app.post("/monitoring/cache/clear")
async def clear_cache():
    """Clear all cached queries."""
    success = redis_query_cache.clear()
    return {"success": success, "message": "Cache cleared" if success else "Failed to clear cache"}

@app.post("/analyze-query")
async def analyze_query(query: str = Form(...)):
    """Analyze query complexity and get recommendations."""
    analysis = query_analyzer.get_detailed_analysis(query)
    return analysis

@app.post("/advanced-search")
async def advanced_search(query: str = Form(...), top_k: int = 10):
    """Advanced hybrid search with semantic chunking."""
    try:
        results = await advanced_retriever.retrieve_advanced(query, top_k)
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "stats": advanced_retriever.get_retrieval_stats()
        }
    except Exception as e:
        logger.error(f"Advanced search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/expand-query")
async def expand_query(query: str = Form(...), expansion_level: str = "medium"):
    """Expand query with synonyms and context awareness."""
    try:
        expanded_query = await query_expander.expand_query_async(query, expansion_level)
        return {
            "original_query": expanded_query.original_query,
            "expanded_queries": expanded_query.expanded_queries,
            "synonyms": expanded_query.synonyms,
            "context_terms": expanded_query.context_terms,
            "trading_terms": expanded_query.trading_terms,
            "technical_terms": expanded_query.technical_terms,
            "confidence_score": expanded_query.confidence_score,
            "expansion_strategy": expanded_query.expansion_strategy,
            "stats": query_expander.get_expansion_stats()
        }
    except Exception as e:
        logger.error(f"Query expansion error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rerank-results")
async def rerank_results(query: str = Form(...), results: str = Form(...), 
                        rerank_strategy: str = "comprehensive", top_k: int = 10):
    """Rerank results using advanced scoring methods."""
    try:
        import json
        results_data = json.loads(results)
        
        reranked = advanced_reranker.rerank_results(
            query, results_data, top_k, rerank_strategy
        )
        
        # Convert RerankResult objects to dictionaries
        reranked_dicts = []
        for result in reranked:
            reranked_dicts.append({
                "text": result.text,
                "metadata": result.metadata,
                "final_score": result.final_score,
                "individual_scores": result.individual_scores,
                "ranking_factors": result.ranking_factors,
                "confidence": result.confidence
            })
        
        return {
            "query": query,
            "reranked_results": reranked_dicts,
            "count": len(reranked_dicts),
            "rerank_strategy": rerank_strategy,
            "stats": advanced_reranker.get_reranking_stats()
        }
    except Exception as e:
        logger.error(f"Reranking error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/compress-context")
async def compress_context(text: str = Form(...), target_ratio: float = 0.3, 
                          method: str = "hybrid", max_length: int = 1000):
    """Compress context using advanced summarization techniques."""
    try:
        compressed = await context_compressor.compress_context(
            text, target_ratio, method, max_length
        )
        
        return {
            "original_text": compressed.original_text,
            "compressed_text": compressed.compressed_text,
            "summary": compressed.summary,
            "key_points": compressed.key_points,
            "compression_ratio": compressed.compression_ratio,
            "quality_score": compressed.quality_score,
            "compression_method": compressed.compression_method,
            "metadata": compressed.metadata,
            "stats": context_compressor.get_compression_stats()
        }
    except Exception as e:
        logger.error(f"Context compression error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/extract-metadata")
async def extract_metadata(document_id: str = Form(...), title: str = Form(...), 
                          text: str = Form(...), source: str = "unknown"):
    """Extract enhanced metadata from document."""
    try:
        enhanced_metadata = await metadata_enhancer.extract_enhanced_metadata(
            document_id, title, text, source
        )
        
        return {
            "document_id": enhanced_metadata.document_id,
            "title": enhanced_metadata.title,
            "content_type": enhanced_metadata.content_type,
            "trading_domain": enhanced_metadata.trading_domain,
            "complexity_level": enhanced_metadata.complexity_level,
            "key_concepts": enhanced_metadata.key_concepts,
            "trading_strategies": enhanced_metadata.trading_strategies,
            "technical_indicators": enhanced_metadata.technical_indicators,
            "risk_factors": enhanced_metadata.risk_factors,
            "time_frames": enhanced_metadata.time_frames,
            "market_conditions": enhanced_metadata.market_conditions,
            "quality_indicators": enhanced_metadata.quality_indicators,
            "sentiment": enhanced_metadata.sentiment,
            "confidence_scores": enhanced_metadata.confidence_scores,
            "extraction_timestamp": enhanced_metadata.extraction_timestamp,
            "version": enhanced_metadata.version,
            "stats": metadata_enhancer.get_extraction_stats()
        }
    except Exception as e:
        logger.error(f"Metadata extraction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/filter-documents")
async def filter_documents(documents: str = Form(...), filters: str = Form(...)):
    """Filter documents based on metadata criteria."""
    try:
        import json
        documents_data = json.loads(documents)
        filters_data = json.loads(filters)
        
        filtered_docs = metadata_enhancer.filter_by_metadata(documents_data, filters_data)
        
        return {
            "original_count": len(documents_data),
            "filtered_count": len(filtered_docs),
            "filtered_documents": filtered_docs,
            "filters_applied": filters_data
        }
    except Exception as e:
        logger.error(f"Document filtering error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/monitoring/recent")
async def get_recent_queries(count: int = 10):
    """Get recent query response times."""
    return {"recent_times": monitor.get_recent_queries(count)}

@app.get("/monitoring/retrieval")
async def get_retrieval_optimization():
    """Get retrieval optimization profiles and statistics."""
    return {
        "profiles": retrieval_optimizer.compare_profiles(),
        "optimizer_available": True
    }


@app.get("/ollama/models")
async def get_ollama_models():
    """Get available Ollama models."""
    try:
        import requests
        import os
        
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
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
        
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://ollama:11434")
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


@app.get("/documents")
async def list_documents(current_user: dict = Depends(get_current_user)):
    """List all uploaded and ingested documents."""
    try:
        import chromadb
        import os
        from pathlib import Path
        from datetime import datetime
        
        documents_dir = Path("/workspace/documents")
        documents_dir.mkdir(exist_ok=True, parents=True)
        
        # Get files from filesystem
        files_list = []
        if documents_dir.exists():
            for file_path in documents_dir.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    files_list.append({
                        "doc_id": file_path.name,
                        "filename": file_path.name,
                        "chunks": 0,  # Not ingested yet
                        "type": file_path.suffix[1:] if file_path.suffix else "unknown",
                        "size": stat.st_size,
                        "uploaded_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "ingested": False
                    })
        
        # Get ingested documents from ChromaDB
        chroma_url = os.getenv("CHROMA_URL", "http://chromadb:8000")
        chroma_client = chromadb.HttpClient(
            host=chroma_url.split("://")[1].split(":")[0],
            port=int(chroma_url.split(":")[-1])
        )
        
        try:
            collection = chroma_client.get_collection("documents")
            
            # Get all documents
            results = collection.get(include=["metadatas"])
            
            # Group by filename and mark as ingested
            ingested_files = {}
            for i, metadata in enumerate(results["metadatas"]):
                filename = metadata.get("filename", "unknown")
                
                if filename not in ingested_files:
                    ingested_files[filename] = {
                        "chunks": 0,
                        "type": metadata.get("doc_type", "unknown"),
                        "ingestion_time": metadata.get("ingestion_time", "")
                    }
                ingested_files[filename]["chunks"] += 1
            
            # Mark uploaded files as ingested if they're in ChromaDB
            for doc in files_list:
                if doc["filename"] in ingested_files:
                    doc["ingested"] = True
                    doc["chunks"] = ingested_files[doc["filename"]]["chunks"]
            
            return JSONResponse(content={"documents": files_list})
            
        except Exception as e:
            if "does not exist" in str(e):
                return JSONResponse(content={"documents": []})
            raise
            
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")


@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a document from filesystem and all its chunks from ChromaDB."""
    try:
        import chromadb
        import os
        from pathlib import Path
        
        documents_dir = Path("/workspace/documents")
        file_path = documents_dir / doc_id
        
        chunks_deleted = 0
        file_deleted = False
        
        # Delete from ChromaDB if exists
        try:
            chroma_url = os.getenv("CHROMA_URL", "http://chromadb:8000")
            chroma_client = chromadb.HttpClient(
                host=chroma_url.split("://")[1].split(":")[0],
                port=int(chroma_url.split(":")[-1])
            )
            
            collection = chroma_client.get_collection("documents")
            
            # Get all chunk IDs for this document (match by filename)
            results = collection.get(
                where={"filename": doc_id},
                include=["metadatas"]
            )
            
            if results["ids"]:
                # Delete all chunks
                collection.delete(ids=results["ids"])
                chunks_deleted = len(results["ids"])
                logger.info(f"Deleted {chunks_deleted} chunks from ChromaDB for {doc_id}")
                
        except Exception as e:
            logger.warning(f"Could not delete from ChromaDB (may not be ingested): {e}")
        
        # Delete physical file
        if file_path.exists():
            file_path.unlink()
            file_deleted = True
            logger.info(f"Deleted file: {file_path}")
        else:
            logger.warning(f"File not found: {file_path}")
        
        if not file_deleted and chunks_deleted == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return JSONResponse(content={
            "success": True,
            "message": f"Deleted document: {doc_id}",
            "file_deleted": file_deleted,
            "chunks_deleted": chunks_deleted
        })
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete document: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")


@app.get("/settings")
async def get_settings(current_user: dict = Depends(get_current_user)):
    """Get user settings including Obsidian configuration."""
    import json
    from pathlib import Path
    
    user_id = current_user["username"]
    settings_dir = Path("data/user_settings")
    settings_dir.mkdir(parents=True, exist_ok=True)
    settings_file = settings_dir / f"{user_id}_settings.json"
    
    # Default settings
    default_settings = {
        "obsidian_vault_path": "",
        "obsidian_api_url": "https://localhost:27124",
        "obsidian_api_key": "",
        "obsidian_enabled": False
    }
    
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                user_settings = json.load(f)
                return JSONResponse(content=user_settings)
        except Exception as e:
            logger.error(f"Failed to load user settings: {e}")
            return JSONResponse(content=default_settings)
    
    return JSONResponse(content=default_settings)


@app.post("/settings")
async def save_settings(request: dict, current_user: dict = Depends(get_current_user)):
    """Save user settings including Obsidian configuration."""
    import json
    from pathlib import Path
    
    user_id = current_user["username"]
    settings_dir = Path("data/user_settings")
    settings_dir.mkdir(parents=True, exist_ok=True)
    settings_file = settings_dir / f"{user_id}_settings.json"
    
    try:
        # Validate required fields if Obsidian is enabled
        if request.get("obsidian_enabled", False):
            if not request.get("obsidian_api_url"):
                raise HTTPException(status_code=400, detail="Obsidian API URL is required when enabled")
        
        # Save settings
        with open(settings_file, 'w') as f:
            json.dump(request, f, indent=2)
        
        logger.info(f"Saved settings for user {user_id}")
        return JSONResponse(content={"success": True, "message": "Settings saved successfully"})
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save user settings: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to save settings: {str(e)}")


@app.post("/settings/test-obsidian")
async def test_obsidian_connection(request: dict, current_user: dict = Depends(get_current_user)):
    """Test Obsidian connection with provided settings."""
    import aiohttp
    from pathlib import Path
    
    vault_path = request.get("vault_path")
    api_url = request.get("api_url")
    api_key = request.get("api_key")
    
    if not api_url:
        raise HTTPException(status_code=400, detail="API URL is required")
    
    try:
        # Test API connection
        headers = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{api_url}/vault/", headers=headers, ssl=False, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    note_count = len(data.get("files", []))
                    return JSONResponse(content={
                        "success": True,
                        "message": f"Connected successfully to Obsidian vault",
                        "note_count": note_count
                    })
                else:
                    return JSONResponse(
                        content={
                            "success": False,
                            "message": f"Connection failed: HTTP {response.status}"
                        },
                        status_code=400
                    )
    except aiohttp.ClientConnectorError:
        return JSONResponse(
            content={
                "success": False,
                "message": "Cannot connect to Obsidian API. Make sure the Local REST API plugin is running."
            },
            status_code=400
        )
    except Exception as e:
        logger.error(f"Obsidian connection test failed: {e}")
        return JSONResponse(
            content={
                "success": False,
                "message": f"Connection test failed: {str(e)}"
            },
            status_code=400
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(content={"status": "healthy", "service": "tradingai-research-platform"})
