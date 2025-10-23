"""Pydantic models for API."""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class IngestRequest(BaseModel):
    """Request to ingest PDFs."""
    force_reindex: bool = Field(False, description="Force reindexing of all PDFs")


class IngestResponse(BaseModel):
    """Response from ingestion."""
    status: str
    processed_files: int
    total_chunks: int
    message: str


class Citation(BaseModel):
    """Citation with source information."""
    text: str
    doc_id: str
    page: Optional[int] = None
    section: Optional[str] = None
    score: float


class Message(BaseModel):
    """Chat message for conversation context."""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class AskRequest(BaseModel):
    """Request to ask a question."""
    query: str = Field(..., description="Question to ask")
    mode: str = Field("qa", description="Mode: 'qa' or 'spec'")
    top_k: int = Field(5, description="Number of results to return (legacy, use rerank_top_k)")
    temperature: Optional[float] = Field(None, description="Temperature for LLM generation")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens for LLM generation")
    top_k_sampling: Optional[int] = Field(None, description="Top-K sampling for LLM generation")
    model: Optional[str] = Field(None, description="LLM model to use for generation")
    conversation_history: Optional[List[Message]] = Field(None, description="Previous conversation messages")
    # Document Retrieval Settings
    bm25_top_k: Optional[int] = Field(None, description="Number of BM25 search results")
    embedding_top_k: Optional[int] = Field(None, description="Number of embedding search results")
    rerank_top_k: Optional[int] = Field(None, description="Number of final reranked results")
    # Web Search Settings
    web_search_results: Optional[int] = Field(None, description="Number of web search results")
    web_pages_to_parse: Optional[int] = Field(None, description="Number of web pages to parse")


class AskResponse(BaseModel):
    """Response from ask endpoint."""
    query: str
    answer: str
    citations: List[Citation]
    mode: str
    spec_file: Optional[str] = None
    web_enabled: Optional[bool] = None
    total_sources: Optional[int] = None
    search_metadata: Optional[Dict[str, Any]] = None


class StrategySpec(BaseModel):
    """YAML strategy specification schema."""
    name: str = Field(..., description="Strategy name")
    description: str = Field(..., description="Strategy description")
    timeframe: str = Field(..., description="Trading timeframe")
    markets: List[str] = Field(..., description="Applicable markets")
    entry_rules: List[str] = Field(..., description="Entry conditions")
    exit_rules: List[str] = Field(..., description="Exit conditions")
    risk_management: Dict[str, Any] = Field(..., description="Risk parameters")
    indicators: List[Dict[str, Any]] = Field(default_factory=list, description="Technical indicators")
    notes: Optional[str] = Field(None, description="Additional notes")
