#!/usr/bin/env python3
"""Batch process all transcripts and PDFs with AI enrichment."""
import logging
import sys
from pathlib import Path
from datetime import datetime
from app.enrichment import KnowledgeEnricher
from app.config import OUTPUT_DIR

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Run batch enrichment on all documents."""
    logger.info("="*60)
    logger.info("BATCH AI ENRICHMENT - Phase 1")
    logger.info("="*60)
    logger.info("This will process:")
    logger.info("  - All video transcripts with llama3.1:8b")
    logger.info("  - All PDF markdowns with gpt-oss:20b")
    logger.info("")
    logger.info("Estimated time: 60-90 minutes total")
    logger.info("="*60)
    
    start_time = datetime.now()
    
    # Initialize enricher
    enricher = KnowledgeEnricher(
        video_model="llama3.1:8b",
        pdf_model="gpt-oss:20b",
        chunk_model="llama3.2:3b"
    )
    
    # Step 1: Enrich video transcripts
    logger.info("\n" + "="*60)
    logger.info("STEP 1: Enriching Video Transcripts")
    logger.info("="*60)
    video_start = datetime.now()
    
    video_results = enricher.batch_enrich_videos(
        transcript_dir=OUTPUT_DIR,
        force_refresh=False  # Use cache if available
    )
    
    video_elapsed = (datetime.now() - video_start).total_seconds() / 60
    logger.info(f"\n✓ Video enrichment completed in {video_elapsed:.1f} minutes")
    logger.info(f"  Processed: {len(video_results)} transcripts")
    
    # Step 2: Enrich PDF markdowns
    logger.info("\n" + "="*60)
    logger.info("STEP 2: Enriching PDF Markdowns")
    logger.info("="*60)
    pdf_start = datetime.now()
    
    pdf_results = enricher.batch_enrich_pdfs(
        md_dir=OUTPUT_DIR,
        force_refresh=False  # Use cache if available
    )
    
    pdf_elapsed = (datetime.now() - pdf_start).total_seconds() / 60
    logger.info(f"\n✓ PDF enrichment completed in {pdf_elapsed:.1f} minutes")
    logger.info(f"  Processed: {len(pdf_results)} PDFs")
    
    # Summary
    total_elapsed = (datetime.now() - start_time).total_seconds() / 60
    logger.info("\n" + "="*60)
    logger.info("ENRICHMENT COMPLETE!")
    logger.info("="*60)
    logger.info(f"Total time: {total_elapsed:.1f} minutes")
    logger.info(f"Video transcripts: {len(video_results)}")
    logger.info(f"PDF markdowns: {len(pdf_results)}")
    logger.info(f"Total enriched: {len(video_results) + len(pdf_results)}")
    logger.info(f"\nEnrichment cache: {enricher.cache_dir}")
    logger.info("="*60)
    
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\nEnrichment interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Enrichment failed: {e}", exc_info=True)
        sys.exit(1)
