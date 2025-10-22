#!/usr/bin/env python3
"""Batch process all videos with LLM enrichment."""
import sys
from pathlib import Path
import logging

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from video_processor import VideoProcessor
from enrichment import KnowledgeEnricher
from config import OUTPUT_DIR

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_process_videos():
    """Process all videos in the documents directory."""
    
    # Initialize processors
    processor = VideoProcessor()
    enricher = KnowledgeEnricher()
    
    # Find all video files
    video_dir = Path("/home/brad/rag_docs_zone")
    video_files = []
    for ext in ['.mp4', '.webm', '.avi', '.mov']:
        video_files.extend(video_dir.glob(f"*{ext}"))
    
    logger.info(f"Found {len(video_files)} video files to process")
    
    if not video_files:
        logger.error("No video files found")
        return
    
    # Process each video
    results = []
    for i, video_file in enumerate(video_files, 1):
        logger.info(f"\n[{i}/{len(video_files)}] Processing: {video_file.name}")
        
        try:
            # Process video
            chunks = processor.process_video(video_file, extract_frames=False)
            
            if chunks:
                # Count chunk types
                chunk_types = {}
                for chunk in chunks:
                    content_type = chunk.get("content_type", "unknown")
                    chunk_types[content_type] = chunk_types.get(content_type, 0) + 1
                
                logger.info(f"  ✓ Generated {len(chunks)} chunks:")
                for content_type, count in chunk_types.items():
                    logger.info(f"    - {content_type}: {count}")
                
                results.append({
                    "file": video_file.name,
                    "chunks": len(chunks),
                    "types": chunk_types,
                    "success": True
                })
            else:
                logger.warning(f"  ⚠ No chunks generated for {video_file.name}")
                results.append({
                    "file": video_file.name,
                    "chunks": 0,
                    "success": False
                })
                
        except Exception as e:
            logger.error(f"  ✗ Failed to process {video_file.name}: {e}")
            results.append({
                "file": video_file.name,
                "error": str(e),
                "success": False
            })
    
    # Summary
    successful = sum(1 for r in results if r["success"])
    total_chunks = sum(r.get("chunks", 0) for r in results)
    
    logger.info(f"\n=== BATCH PROCESSING COMPLETE ===")
    logger.info(f"Videos processed: {successful}/{len(video_files)}")
    logger.info(f"Total chunks generated: {total_chunks}")
    
    # Show detailed results
    for result in results:
        if result["success"]:
            logger.info(f"✓ {result['file']}: {result['chunks']} chunks")
        else:
            logger.info(f"✗ {result['file']}: {result.get('error', 'Unknown error')}")
    
    return results

if __name__ == "__main__":
    batch_process_videos()