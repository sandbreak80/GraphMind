#!/usr/bin/env python3
"""Test video processing with LLM enrichment."""
import sys
from pathlib import Path
import logging

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from video_processor import VideoProcessor
from config import OUTPUT_DIR

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_video_processing():
    """Test video processing with a sample video."""
    
    # Initialize video processor
    processor = VideoProcessor()
    
    # Find a video file to test
    video_dir = Path("/workspace/pdfs")
    video_files = list(video_dir.rglob("*.mp4")) + list(video_dir.rglob("*.webm"))
    
    if not video_files:
        logger.error("No video files found in /home/brad/rag_docs_zone")
        return
    
    # Test with the first video
    test_video = video_files[0]
    logger.info(f"Testing video processing with: {test_video.name}")
    
    try:
        # Process the video
        chunks = processor.process_video(test_video, extract_frames=False)
        
        logger.info(f"Processing complete! Generated {len(chunks)} chunks:")
        
        # Show chunk types
        chunk_types = {}
        for chunk in chunks:
            content_type = chunk.get("content_type", "unknown")
            chunk_types[content_type] = chunk_types.get(content_type, 0) + 1
        
        for content_type, count in chunk_types.items():
            logger.info(f"  - {content_type}: {count} chunks")
        
        # Show sample chunks
        logger.info("\nSample chunks:")
        for i, chunk in enumerate(chunks[:3]):
            logger.info(f"\nChunk {i+1} ({chunk.get('content_type', 'unknown')}):")
            logger.info(f"  Text: {chunk['text'][:200]}...")
            logger.info(f"  Section: {chunk.get('section', 'N/A')}")
            if chunk.get('ai_enriched'):
                logger.info(f"  AI Enriched: Yes")
                if chunk.get('ai_summary'):
                    logger.info(f"  AI Summary: {chunk['ai_summary']}")
        
        return chunks
        
    except Exception as e:
        logger.error(f"Video processing failed: {e}")
        return []

if __name__ == "__main__":
    test_video_processing()