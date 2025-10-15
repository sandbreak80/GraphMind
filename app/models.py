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


class AskRequest(BaseModel):
    """Request to ask a question."""
    query: str = Field(..., description="Question to ask")
    mode: str = Field("qa", description="Mode: 'qa' or 'spec'")
    top_k: int = Field(5, description="Number of results to return")


class AskResponse(BaseModel):
    """Response from ask endpoint."""
    query: str
    answer: str
    citations: List[Citation]
    mode: str
    spec_file: Optional[str] = None


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
