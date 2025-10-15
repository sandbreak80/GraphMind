"""AI-powered knowledge enrichment orchestrator."""
import logging
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.ollama_client import OllamaClient
from app.config import OLLAMA_BASE_URL, OUTPUT_DIR

logger = logging.getLogger(__name__)


class KnowledgeEnricher:
    """Orchestrates AI-powered enrichment of documents."""
    
    def __init__(
        self,
        ollama_url: str = OLLAMA_BASE_URL,
        video_model: str = "llama3.1:8b",
        pdf_model: str = "gpt-oss:20b",
        chunk_model: str = "llama3.2:3b"
    ):
        """
        Initialize enricher with different models for different tasks.
        
        Args:
            ollama_url: Ollama API base URL
            video_model: Model for video transcript enrichment (fast + quality)
            pdf_model: Model for PDF analysis (more capable)
            chunk_model: Model for quick chunk metadata (ultra fast)
        """
        self.ollama = OllamaClient(ollama_url, default_model=video_model)
        self.video_model = video_model
        self.pdf_model = pdf_model
        self.chunk_model = chunk_model
        
        # Create enrichment cache directory
        self.cache_dir = OUTPUT_DIR / "enrichment_cache"
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        
        logger.info(f"Initialized KnowledgeEnricher")
        logger.info(f"  Video model: {video_model}")
        logger.info(f"  PDF model: {pdf_model}")
        logger.info(f"  Chunk model: {chunk_model}")
    
    def enrich_video_transcript(
        self,
        transcript_path: Path,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Enrich video transcript with AI-generated metadata.
        
        Args:
            transcript_path: Path to video transcript file
            force_refresh: Force re-enrichment even if cached
            
        Returns:
            Dictionary with enriched metadata
        """
        doc_id = transcript_path.stem.replace("_transcript", "")
        cache_file = self.cache_dir / f"{doc_id}_video_enrichment.json"
        
        # Check cache
        if not force_refresh and cache_file.exists():
            logger.info(f"Using cached enrichment for {doc_id}")
            return json.loads(cache_file.read_text())
        
        logger.info(f"Enriching video transcript: {doc_id}")
        
        try:
            transcript_text = transcript_path.read_text()
            
            # Limit to first ~6000 chars for analysis (about 10 minutes of content)
            sample_text = transcript_text[:6000]
            
            prompt = f"""Analyze this trading education video transcript and extract structured information.

Transcript (first 10 minutes):
{sample_text}

Extract the following in JSON format:
{{
  "summary": "2-3 sentence summary of what this video teaches",
  "key_concepts": ["list", "5-10", "main concepts"],
  "strategies": ["specific trading strategies mentioned"],
  "indicators": ["technical indicators discussed"],
  "action_items": ["practical steps for traders"],
  "topic_category": "one of: technical_analysis, psychology, strategy_development, risk_management, market_structure",
  "difficulty": "one of: beginner, intermediate, advanced",
  "prerequisites": ["concepts trader should know first"]
}}

Be specific and extract only concepts actually discussed in detail."""

            result = self.ollama.generate_json(
                prompt=prompt,
                model=self.video_model,
                temperature=0.3,  # Lower temp for more consistent extraction
                max_tokens=1000,
                timeout=90
            )
            
            # Add metadata
            enrichment = {
                "doc_id": doc_id,
                "doc_type": "video_transcript",
                "enriched_at": datetime.now().isoformat(),
                "model_used": self.video_model,
                **result
            }
            
            # Save to cache
            cache_file.write_text(json.dumps(enrichment, indent=2))
            logger.info(f"✓ Enriched {doc_id}")
            
            return enrichment
            
        except Exception as e:
            logger.error(f"Failed to enrich video transcript {doc_id}: {e}")
            return self._get_empty_enrichment(doc_id, "video_transcript")
    
    def enrich_pdf_markdown(
        self,
        md_path: Path,
        force_refresh: bool = False
    ) -> Dict[str, Any]:
        """
        Enrich PDF markdown export with AI-generated metadata.
        
        Args:
            md_path: Path to markdown file
            force_refresh: Force re-enrichment even if cached
            
        Returns:
            Dictionary with enriched metadata
        """
        doc_id = md_path.stem
        cache_file = self.cache_dir / f"{doc_id}_pdf_enrichment.json"
        
        # Check cache
        if not force_refresh and cache_file.exists():
            logger.info(f"Using cached enrichment for {doc_id}")
            return json.loads(cache_file.read_text())
        
        logger.info(f"Enriching PDF markdown: {doc_id}")
        
        try:
            md_text = md_path.read_text()
            
            # Limit to first ~8000 chars for analysis
            sample_text = md_text[:8000]
            
            prompt = f"""Analyze this trading education document and extract structured information.

Document content:
{sample_text}

Extract the following in JSON format:
{{
  "executive_summary": "3-4 sentence overview",
  "learning_objectives": ["3-5 key things trader will learn"],
  "key_formulas": ["formulas or calculations with brief explanation"],
  "strategy_components": ["entry rules", "exit rules", "risk rules"],
  "practical_applications": ["how to apply this knowledge"],
  "difficulty": "one of: beginner, intermediate, advanced",
  "prerequisites": ["concepts needed before this"],
  "related_topics": ["related concepts to study"]
}}

Focus on actionable trading knowledge."""

            result = self.ollama.generate_json(
                prompt=prompt,
                model=self.pdf_model,
                temperature=0.3,
                max_tokens=1200,
                timeout=120
            )
            
            # Add metadata
            enrichment = {
                "doc_id": doc_id,
                "doc_type": "pdf",
                "enriched_at": datetime.now().isoformat(),
                "model_used": self.pdf_model,
                **result
            }
            
            # Save to cache
            cache_file.write_text(json.dumps(enrichment, indent=2))
            logger.info(f"✓ Enriched {doc_id}")
            
            return enrichment
            
        except Exception as e:
            logger.error(f"Failed to enrich PDF markdown {doc_id}: {e}")
            return self._get_empty_enrichment(doc_id, "pdf")
    
    def enrich_chunk(
        self,
        chunk_text: str,
        chunk_id: str,
        doc_type: str = "text"
    ) -> Dict[str, Any]:
        """
        Generate enhanced metadata for a single chunk (fast operation).
        
        Args:
            chunk_text: Text content of chunk
            chunk_id: Unique chunk identifier
            doc_type: Type of document
            
        Returns:
            Dictionary with chunk metadata
        """
        logger.debug(f"Enriching chunk: {chunk_id}")
        
        try:
            # Limit chunk text for analysis
            sample_text = chunk_text[:800]
            
            prompt = f"""For this trading content, extract:

Text:
{sample_text}

Return JSON:
{{
  "summary": "1 sentence core idea",
  "semantic_tags": ["3-5", "concept tags"],
  "trading_context": "one of: premarket, intraday, exit, risk, backtest, psychology",
  "question": "What question does this chunk answer?"
}}"""

            result = self.ollama.generate_json(
                prompt=prompt,
                model=self.chunk_model,
                temperature=0.3,
                max_tokens=300,
                timeout=30
            )
            
            return {
                "chunk_id": chunk_id,
                **result
            }
            
        except Exception as e:
            logger.warning(f"Failed to enrich chunk {chunk_id}: {e}")
            return {}
    
    def batch_enrich_videos(
        self,
        transcript_dir: Path = OUTPUT_DIR,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Batch enrich all video transcripts.
        
        Args:
            transcript_dir: Directory containing transcript files
            force_refresh: Force re-enrichment
            
        Returns:
            List of enrichment results
        """
        transcript_files = list(transcript_dir.glob("*_transcript.txt"))
        logger.info(f"Found {len(transcript_files)} video transcripts to enrich")
        
        results = []
        for i, transcript_path in enumerate(transcript_files, 1):
            logger.info(f"[{i}/{len(transcript_files)}] Processing {transcript_path.name}")
            try:
                enrichment = self.enrich_video_transcript(transcript_path, force_refresh)
                results.append(enrichment)
            except Exception as e:
                logger.error(f"Failed to process {transcript_path.name}: {e}")
        
        logger.info(f"Completed video enrichment: {len(results)}/{len(transcript_files)} successful")
        return results
    
    def batch_enrich_pdfs(
        self,
        md_dir: Path = OUTPUT_DIR,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Batch enrich all PDF markdown files.
        
        Args:
            md_dir: Directory containing markdown files
            force_refresh: Force re-enrichment
            
        Returns:
            List of enrichment results
        """
        md_files = [
            f for f in md_dir.glob("*.md")
            if not f.name.startswith("Copy of")  # Skip duplicates
        ]
        logger.info(f"Found {len(md_files)} PDF markdowns to enrich")
        
        results = []
        for i, md_path in enumerate(md_files, 1):
            logger.info(f"[{i}/{len(md_files)}] Processing {md_path.name}")
            try:
                enrichment = self.enrich_pdf_markdown(md_path, force_refresh)
                results.append(enrichment)
            except Exception as e:
                logger.error(f"Failed to process {md_path.name}: {e}")
        
        logger.info(f"Completed PDF enrichment: {len(results)}/{len(md_files)} successful")
        return results
    
    def _get_empty_enrichment(self, doc_id: str, doc_type: str) -> Dict[str, Any]:
        """Return empty enrichment structure as fallback."""
        return {
            "doc_id": doc_id,
            "doc_type": doc_type,
            "enriched_at": datetime.now().isoformat(),
            "summary": "",
            "key_concepts": [],
            "error": "Enrichment failed"
        }
