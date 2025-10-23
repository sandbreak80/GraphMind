#!/usr/bin/env python3
"""Test LLM enrichment for video transcripts."""
import sys
from pathlib import Path
import logging

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from enrichment import KnowledgeEnricher

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_llm_enrichment():
    """Test LLM enrichment on a video transcript."""
    
    # Initialize enricher
    enricher = KnowledgeEnricher()
    
    # Find a transcript file
    transcript_path = Path("/workspace/outputs/Mid_transcript.txt")
    
    if not transcript_path.exists():
        logger.error(f"Transcript file not found: {transcript_path}")
        return
    
    logger.info(f"Testing LLM enrichment on: {transcript_path.name}")
    
    try:
        # Enrich the transcript
        enrichment = enricher.enrich_video_transcript(transcript_path)
        
        logger.info("Enrichment completed!")
        logger.info(f"Summary: {enrichment.get('summary', 'N/A')}")
        logger.info(f"Key Concepts: {enrichment.get('key_concepts', [])}")
        logger.info(f"Strategies: {enrichment.get('strategies', [])}")
        logger.info(f"Action Items: {enrichment.get('action_items', [])}")
        logger.info(f"Topic Category: {enrichment.get('topic_category', 'N/A')}")
        logger.info(f"Difficulty: {enrichment.get('difficulty', 'N/A')}")
        
        return enrichment
        
    except Exception as e:
        logger.error(f"LLM enrichment failed: {e}")
        return None

if __name__ == "__main__":
    test_llm_enrichment()