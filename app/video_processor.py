"""Process video files with audio transcription, LLM enrichment, and frame analysis."""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import cv2
import numpy as np
from faster_whisper import WhisperModel
from PIL import Image
import json

from app.config import OUTPUT_DIR, VIDEO_FRAME_INTERVAL, WHISPER_MODEL_SIZE, AI_ENRICHMENT_ENABLED
from app.enrichment import KnowledgeEnricher

logger = logging.getLogger(__name__)


class VideoProcessor:
    """Process videos with transcription, LLM enrichment, and visual analysis."""
    
    def __init__(self):
        """Initialize with Whisper model and LLM enricher."""
        try:
            # Use GPU if available, fallback to CPU
            self.whisper_model = WhisperModel(
                WHISPER_MODEL_SIZE,
                device="cuda",
                compute_type="float16"
            )
            logger.info(f"Loaded Whisper {WHISPER_MODEL_SIZE} model on GPU")
        except Exception as e:
            logger.warning(f"GPU Whisper failed, using CPU: {e}")
            self.whisper_model = WhisperModel(WHISPER_MODEL_SIZE, device="cpu")
        
        # Initialize LLM enricher for video transcripts
        if AI_ENRICHMENT_ENABLED:
            self.enricher = KnowledgeEnricher()
            logger.info("Initialized LLM enricher for video processing")
        else:
            self.enricher = None
            logger.info("LLM enrichment disabled for video processing")
    
    def process_video(self, file_path: Path, extract_frames: bool = True) -> List[Dict[str, Any]]:
        """
        Process video file:
        1. Extract audio and transcribe with timestamps
        2. Process transcript with LLM for key insights
        3. Extract keyframes for visual analysis (optional)
        4. Combine into searchable chunks
        """
        chunks = []
        doc_id = file_path.stem
        
        try:
            # Step 1: Transcribe audio
            logger.info(f"Transcribing {file_path.name}...")
            transcript_chunks = self._transcribe_audio(file_path, doc_id)
            chunks.extend(transcript_chunks)
            
            # Step 2: Save full transcript
            transcript_path = self._save_transcript(doc_id, transcript_chunks)
            
            # Step 3: Process transcript with LLM for key insights
            if self.enricher and transcript_path:
                logger.info(f"Processing transcript with LLM for {file_path.name}...")
                llm_chunks = self._process_transcript_with_llm(transcript_path, doc_id)
                chunks.extend(llm_chunks)
            
            # Step 4: Extract keyframes (optional - can be heavy)
            if extract_frames:
                logger.info(f"Extracting keyframes from {file_path.name}...")
                frame_chunks = self._extract_keyframes(file_path, doc_id)
                chunks.extend(frame_chunks)
            
            logger.info(f"Processed video {file_path.name}: {len(chunks)} chunks")
            return chunks
            
        except Exception as e:
            logger.error(f"Failed to process video {file_path}: {e}")
            return []
    
    def _transcribe_audio(self, video_path: Path, doc_id: str) -> List[Dict[str, Any]]:
        """Transcribe audio from video with timestamps."""
        chunks = []
        
        try:
            segments, info = self.whisper_model.transcribe(
                str(video_path),
                language="en",
                beam_size=5,
                vad_filter=True  # Voice activity detection
            )
            
            logger.info(f"Detected language: {info.language} ({info.language_probability:.2f})")
            
            for segment in segments:
                # Create chunk for each segment
                timestamp_str = f"{self._format_timestamp(segment.start)} - {self._format_timestamp(segment.end)}"
                
                chunk_text = f"[{timestamp_str}]\n{segment.text.strip()}"
                
                # Create unique chunk ID using milliseconds to avoid duplicates
                chunk_id = f"{doc_id}_t{int(segment.start * 1000)}"
                
                # Ensure ALL values are non-None
                chunks.append({
                    "text": str(chunk_text),
                    "doc_id": str(doc_id),
                    "page": 0,
                    "section": str(f"Video @ {timestamp_str}"),
                    "chunk_id": str(chunk_id),
                    "timestamp_start": float(segment.start),
                    "timestamp_end": float(segment.end),
                    "media_type": "video_transcript",
                    "content_type": "video_transcript",
                    "extraction_method": "whisper",
                    "ingested_at": ""  # Will be set by ingestor
                })
            
            return chunks
            
        except Exception as e:
            logger.error(f"Transcription failed for {video_path}: {e}")
            return []
    
    def _extract_keyframes(
        self,
        video_path: Path,
        doc_id: str,
        frame_interval: int = VIDEO_FRAME_INTERVAL
    ) -> List[Dict[str, Any]]:
        """
        Extract keyframes from video for visual analysis.
        Saves frames and creates descriptive chunks.
        """
        chunks = []
        
        try:
            cap = cv2.VideoCapture(str(video_path))
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            frame_count = 0
            saved_frames = []
            
            # Extract frames at intervals
            interval_frames = int(fps * frame_interval)
            
            while cap.isOpened():
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_count % interval_frames == 0:
                    timestamp = frame_count / fps
                    
                    # Save frame
                    frame_filename = f"{doc_id}_frame_{int(timestamp)}s.jpg"
                    frame_path = OUTPUT_DIR / "frames" / frame_filename
                    frame_path.parent.mkdir(exist_ok=True, parents=True)
                    
                    cv2.imwrite(str(frame_path), frame)
                    saved_frames.append({
                        "timestamp": timestamp,
                        "path": str(frame_path)
                    })
                    
                    # Analyze frame content (simple description for now)
                    frame_description = self._analyze_frame(frame, timestamp)
                    
                    # Create unique chunk ID
                    chunk_id = f"{doc_id}_f{int(timestamp * 1000)}"
                    
                    # Ensure ALL values are non-None  
                    chunks.append({
                        "text": str(frame_description),
                        "doc_id": str(doc_id),
                        "page": 0,
                        "section": str(f"Video Frame @ {self._format_timestamp(timestamp)}"),
                        "chunk_id": str(chunk_id),
                        "timestamp_start": float(timestamp),
                        "timestamp_end": float(timestamp + 1),
                        "frame_path": str(frame_path),
                        "media_type": "video_frame",
                        "content_type": "video_frame",
                        "extraction_method": "opencv+ocr",
                        "ingested_at": ""  # Will be set by ingestor
                    })
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Extracted {len(saved_frames)} keyframes from {video_path.name}")
            
            return chunks
            
        except Exception as e:
            logger.error(f"Frame extraction failed for {video_path}: {e}")
            return []
    
    def _analyze_frame(self, frame: np.ndarray, timestamp: float) -> str:
        """
        Analyze frame content with OCR for trading videos.
        Extracts visible text (tickers, indicators, price levels).
        """
        description_parts = [f"Video frame at {self._format_timestamp(timestamp)}"]
        
        try:
            # OCR to extract visible text (trading symbols, indicators, prices)
            import pytesseract
            from PIL import Image
            
            # Convert to PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(frame_rgb)
            
            # Extract text with confidence
            ocr_data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
            
            # Filter high-confidence text
            extracted_text = []
            for i, conf in enumerate(ocr_data['conf']):
                if int(conf) > 50:  # Confidence > 50%
                    text = ocr_data['text'][i].strip()
                    if text and len(text) > 1:
                        extracted_text.append(text)
            
            if extracted_text:
                # Join unique words
                unique_text = list(dict.fromkeys(extracted_text))  # Preserve order
                visible_text = " ".join(unique_text[:30])  # Limit to 30 words
                description_parts.append(f"Visible text: {visible_text}")
                
                # Detect trading-specific terms
                trading_terms = ['ES', 'NQ', 'YM', 'RTY', 'VWAP', 'EMA', 'RSI', 
                                'MACD', 'Support', 'Resistance', 'Entry', 'Exit']
                found_terms = [term for term in trading_terms if term in " ".join(unique_text)]
                if found_terms:
                    description_parts.append(f"Trading indicators: {', '.join(found_terms)}")
        
        except Exception as e:
            logger.debug(f"OCR failed for frame at {timestamp}: {e}")
        
        # Visual analysis
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.count_nonzero(edges) / edges.size
        
        if edge_density > 0.1:
            description_parts.append("Contains chart/graphical content (high edge density detected)")
        
        return " ".join(description_parts)
    
    def _format_timestamp(self, seconds: float) -> str:
        """Format timestamp as HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    
    def _save_transcript(self, doc_id: str, transcript_chunks: List[Dict[str, Any]]) -> Optional[Path]:
        """Save full transcript to file."""
        try:
            transcript_path = OUTPUT_DIR / f"{doc_id}_transcript.txt"
            
            lines = []
            for chunk in transcript_chunks:
                if "timestamp_start" in chunk:
                    timestamp = self._format_timestamp(chunk["timestamp_start"])
                    text = chunk["text"].split("\n", 1)[-1]  # Remove timestamp from text
                    lines.append(f"[{timestamp}] {text}\n")
            
            transcript_path.write_text("".join(lines))
            logger.info(f"Saved transcript to {transcript_path}")
            return transcript_path
            
        except Exception as e:
            logger.error(f"Failed to save transcript: {e}")
            return None
    
    def _process_transcript_with_llm(self, transcript_path: Path, doc_id: str) -> List[Dict[str, Any]]:
        """
        Process video transcript with LLM to extract key insights and create enriched chunks.
        
        Args:
            transcript_path: Path to transcript file
            doc_id: Document identifier
            
        Returns:
            List of enriched chunks from LLM processing
        """
        chunks = []
        
        try:
            # Get LLM enrichment
            enrichment = self.enricher.enrich_video_transcript(transcript_path)
            
            # Create chunks from LLM insights
            llm_chunks = []
            
            # 1. Summary chunk
            if enrichment.get("summary"):
                summary_chunk = {
                    "text": f"Video Summary: {enrichment['summary']}",
                    "doc_id": doc_id,
                    "page": 0,
                    "section": "LLM Summary",
                    "chunk_id": f"{doc_id}_summary",
                    "content_type": "llm_summary",
                    "extraction_method": "llm_enrichment",
                    "media_type": "video_insights",
                    "ai_enriched": True,
                    "ai_summary": enrichment["summary"],
                    "ai_category": enrichment.get("topic_category", ""),
                    "ai_difficulty": enrichment.get("difficulty", "")
                }
                llm_chunks.append(summary_chunk)
            
            # 2. Key concepts chunk
            if enrichment.get("key_concepts"):
                concepts_text = "Key Concepts: " + ", ".join(enrichment["key_concepts"])
                concepts_chunk = {
                    "text": concepts_text,
                    "doc_id": doc_id,
                    "page": 0,
                    "section": "LLM Key Concepts",
                    "chunk_id": f"{doc_id}_concepts",
                    "content_type": "llm_concepts",
                    "extraction_method": "llm_enrichment",
                    "media_type": "video_insights",
                    "ai_enriched": True,
                    "ai_concepts": ", ".join(enrichment["key_concepts"])
                }
                llm_chunks.append(concepts_chunk)
            
            # 3. Strategies chunk
            if enrichment.get("strategies"):
                strategies_text = "Trading Strategies: " + ", ".join(enrichment["strategies"])
                strategies_chunk = {
                    "text": strategies_text,
                    "doc_id": doc_id,
                    "page": 0,
                    "section": "LLM Strategies",
                    "chunk_id": f"{doc_id}_strategies",
                    "content_type": "llm_strategies",
                    "extraction_method": "llm_enrichment",
                    "media_type": "video_insights",
                    "ai_enriched": True
                }
                llm_chunks.append(strategies_chunk)
            
            # 4. Action items chunk
            if enrichment.get("action_items"):
                actions_text = "Action Items: " + ", ".join(enrichment["action_items"])
                actions_chunk = {
                    "text": actions_text,
                    "doc_id": doc_id,
                    "page": 0,
                    "section": "LLM Action Items",
                    "chunk_id": f"{doc_id}_actions",
                    "content_type": "llm_actions",
                    "extraction_method": "llm_enrichment",
                    "media_type": "video_insights",
                    "ai_enriched": True
                }
                llm_chunks.append(actions_chunk)
            
            # 5. Technical indicators chunk
            if enrichment.get("indicators"):
                indicators_text = "Technical Indicators: " + ", ".join(enrichment["indicators"])
                indicators_chunk = {
                    "text": indicators_text,
                    "doc_id": doc_id,
                    "page": 0,
                    "section": "LLM Indicators",
                    "chunk_id": f"{doc_id}_indicators",
                    "content_type": "llm_indicators",
                    "extraction_method": "llm_enrichment",
                    "media_type": "video_insights",
                    "ai_enriched": True
                }
                llm_chunks.append(indicators_chunk)
            
            logger.info(f"Created {len(llm_chunks)} LLM-enriched chunks for {doc_id}")
            return llm_chunks
            
        except Exception as e:
            logger.error(f"Failed to process transcript with LLM for {doc_id}: {e}")
            return []
