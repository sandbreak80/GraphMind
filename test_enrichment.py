#!/usr/bin/env python3
"""Test AI enrichment on sample files."""
import logging
from pathlib import Path
import json
from app.enrichment import KnowledgeEnricher
from app.config import OUTPUT_DIR, OLLAMA_BASE_URL

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_video_enrichment():
    """Test video transcript enrichment."""
    logger.info("=" * 60)
    logger.info("Testing Video Transcript Enrichment")
    logger.info("=" * 60)
    
    # Find a sample transcript
    transcripts = list(OUTPUT_DIR.glob("*_transcript.txt"))
    if not transcripts:
        logger.error("No video transcripts found in outputs/")
        return None
    
    sample_transcript = transcripts[0]
    logger.info(f"Testing with: {sample_transcript.name}")
    
    # Initialize enricher
    enricher = KnowledgeEnricher(
        ollama_url=OLLAMA_BASE_URL,
        video_model="llama3.1:8b",
        pdf_model="gpt-oss:20b",
        chunk_model="llama3.2:3b"
    )
    
    # Enrich the transcript
    result = enricher.enrich_video_transcript(sample_transcript, force_refresh=True)
    
    # Display results
    logger.info("\n" + "=" * 60)
    logger.info("VIDEO ENRICHMENT RESULT")
    logger.info("=" * 60)
    print(json.dumps(result, indent=2))
    
    return result


def test_pdf_enrichment():
    """Test PDF markdown enrichment."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing PDF Markdown Enrichment")
    logger.info("=" * 60)
    
    # Find a sample markdown
    markdowns = [f for f in OUTPUT_DIR.glob("*.md") if not f.name.startswith("Copy of")]
    if not markdowns:
        logger.error("No PDF markdowns found in outputs/")
        return None
    
    sample_md = markdowns[0]
    logger.info(f"Testing with: {sample_md.name}")
    
    # Initialize enricher
    enricher = KnowledgeEnricher(
        ollama_url=OLLAMA_BASE_URL,
        video_model="llama3.1:8b",
        pdf_model="gpt-oss:20b",
        chunk_model="llama3.2:3b"
    )
    
    # Enrich the markdown
    result = enricher.enrich_pdf_markdown(sample_md, force_refresh=True)
    
    # Display results
    logger.info("\n" + "=" * 60)
    logger.info("PDF ENRICHMENT RESULT")
    logger.info("=" * 60)
    print(json.dumps(result, indent=2))
    
    return result


def test_chunk_enrichment():
    """Test quick chunk-level enrichment."""
    logger.info("\n" + "=" * 60)
    logger.info("Testing Chunk Enrichment")
    logger.info("=" * 60)
    
    sample_chunk = """
    The momentum breakout strategy requires three key components:
    1. Price must break above the opening range high
    2. Volume should be at least 150% of average
    3. RSI should be above 50 to confirm momentum
    
    Entry is taken on the first pullback after the breakout, with a stop
    below the opening range low.
    """
    
    enricher = KnowledgeEnricher()
    result = enricher.enrich_chunk(sample_chunk, "test_chunk_001", "pdf")
    
    logger.info("\n" + "=" * 60)
    logger.info("CHUNK ENRICHMENT RESULT")
    logger.info("=" * 60)
    print(json.dumps(result, indent=2))
    
    return result


def main():
    """Run all enrichment tests."""
    logger.info("Starting AI Enrichment Tests")
    logger.info("This will test enrichment on sample files using local Ollama models")
    
    try:
        # Test 1: Video transcript
        video_result = test_video_enrichment()
        
        # Test 2: PDF markdown
        pdf_result = test_pdf_enrichment()
        
        # Test 3: Chunk-level
        chunk_result = test_chunk_enrichment()
        
        # Summary
        logger.info("\n" + "=" * 60)
        logger.info("TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Video enrichment: {'✓ Success' if video_result else '✗ Failed'}")
        logger.info(f"PDF enrichment: {'✓ Success' if pdf_result else '✗ Failed'}")
        logger.info(f"Chunk enrichment: {'✓ Success' if chunk_result else '✗ Failed'}")
        
        logger.info("\nEnrichment cache saved to: outputs/enrichment_cache/")
        
    except Exception as e:
        logger.error(f"Test failed: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
