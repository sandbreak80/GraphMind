"""FastAPI application for EminiPlayer RAG service."""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

from app.models import IngestRequest, IngestResponse, AskRequest, AskResponse
from app.ingest import PDFIngestor
from app.retrieval import HybridRetriever
from app.spec_extraction import SpecExtractor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
ingestor: PDFIngestor
retriever: HybridRetriever
spec_extractor: SpecExtractor


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    global ingestor, retriever, spec_extractor
    
    logger.info("Initializing RAG service...")
    ingestor = PDFIngestor()
    retriever = HybridRetriever()
    spec_extractor = SpecExtractor(retriever)
    logger.info("Service initialized successfully")
    
    yield
    
    logger.info("Shutting down...")


app = FastAPI(
    title="EminiPlayer RAG Service",
    description="RAG service for EminiPlayer PDFs with spec extraction",
    version="1.0.0",
    lifespan=lifespan
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


@app.get("/stats")
async def get_stats():
    """Get database statistics."""
    try:
        stats = retriever.get_stats()
        return JSONResponse(content=stats)
    except Exception as e:
        logger.error(f"Stats error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
