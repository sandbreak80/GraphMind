"""Multi-format ingestion: PDF, Video, Excel, Word, and more."""
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
import subprocess
from datetime import datetime
from collections import Counter
import json
import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

from app.config import PDF_DIR, CHROMA_DIR, OUTPUT_DIR, EMBEDDING_MODEL, COLLECTION_NAME, CHUNK_SIZE, CHUNK_OVERLAP, AI_ENRICHMENT_ENABLED
from app.document_processor import DocumentProcessor
from app.video_processor import VideoProcessor
from app.doc_type_inference import infer_doc_type, get_doc_category, get_difficulty_hint

logger = logging.getLogger(__name__)


class PDFIngestor:
    """Handles multi-format ingestion: PDF, Video, Excel, Word, Text."""
    
    def __init__(self):
        """Initialize ingestor with Chroma, embedding model, and processors."""
        # Use HttpClient to connect to the ChromaDB service (not PersistentClient)
        chroma_url = os.getenv("CHROMA_URL", "http://chromadb:8000")
        self.chroma_client = chromadb.HttpClient(
            host=chroma_url.split("://")[1].split(":")[0],
            port=int(chroma_url.split(":")[-1])
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",  # Use standard collection name
            metadata={"hnsw:space": "cosine"}
        )
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        
        # Initialize specialized processors
        self.doc_processor = DocumentProcessor()
        self.video_processor = VideoProcessor()
        
        # Load AI enrichment cache if available
        self.enrichment_cache_dir = OUTPUT_DIR / "enrichment_cache"
        self.enrichment_cache = self._load_enrichment_cache()
        
        logger.info(f"Loaded embedding model: {EMBEDDING_MODEL}")
        logger.info("Initialized all file processors")
        if AI_ENRICHMENT_ENABLED and self.enrichment_cache:
            logger.info(f"Loaded {len(self.enrichment_cache)} AI enrichment entries")
    
    def ingest_all(self, force_reindex: bool = False) -> Dict[str, int]:
        """Ingest all supported files from PDF_DIR."""
        # Find all supported file types
        supported_extensions = {
            'pdf', 'mp4', 'webm', 'avi', 'mov',  # PDF and Video
            'xlsx', 'xls', 'docx', 'doc', 'txt'  # Office and Text
        }
        
        all_files = []
        for ext in supported_extensions:
            all_files.extend(PDF_DIR.rglob(f"*.{ext}"))
        
        # Filter out temp files
        all_files = [f for f in all_files if not f.name.startswith('~$')]
        
        logger.info(f"Found {len(all_files)} files across all supported formats")
        
        # Log breakdown by type
        file_types = {}
        for f in all_files:
            ext = f.suffix.lower().lstrip('.')
            file_types[ext] = file_types.get(ext, 0) + 1
        logger.info(f"File breakdown: {file_types}")
        
        if force_reindex:
            logger.info("Force reindex: clearing existing collection")
            try:
                self.chroma_client.delete_collection("documents")
            except Exception as e:
                logger.warning(f"Could not delete collection (may not exist): {e}")
        
        self.collection = self.chroma_client.get_or_create_collection(
            name="documents",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Check collection state before ingestion
        try:
            count = self.collection.count()
            logger.info(f"Collection 'documents' currently has {count} documents")
        except Exception as e:
            logger.warning(f"Could not get collection count: {e}")
        
        processed_files = 0
        total_chunks = 0
        failed_files = []
        
        for file_path in all_files:
            try:
                chunks = self._process_file(file_path)
                if chunks:
                    # Enhance chunks with file-level metadata
                    chunks = self._enhance_chunks_with_metadata(chunks, file_path)
                    self._index_chunks(chunks)
                    processed_files += 1
                    total_chunks += len(chunks)
                    logger.info(f"✓ {file_path.name}: {len(chunks)} chunks")
                else:
                    logger.warning(f"⚠ {file_path.name}: No chunks extracted")
            except Exception as e:
                logger.error(f"✗ Failed to process {file_path.name}: {e}")
                failed_files.append(file_path.name)
        
        if failed_files:
            logger.warning(f"Failed files ({len(failed_files)}): {', '.join(failed_files[:10])}")
        
        # Check final collection state
        try:
            final_count = self.collection.count()
            logger.info(f"Final collection 'documents' has {final_count} documents")
        except Exception as e:
            logger.warning(f"Could not get final collection count: {e}")
        
        return {
            "processed_files": processed_files,
            "total_chunks": total_chunks,
            "failed_files": len(failed_files)
        }
    
    def _process_file(self, file_path: Path) -> List[Dict[str, Any]]:
        """Route file to appropriate processor based on extension."""
        ext = file_path.suffix.lower()
        
        # PDFs
        if ext == '.pdf':
            return self._process_pdf(file_path)
        
        # Videos - Process with LLM enrichment
        elif ext in ['.mp4', '.webm', '.avi', '.mov']:
            return self.video_processor.process_video(file_path, extract_frames=False)  # Skip frames for now
        
        # Excel
        elif ext in ['.xlsx', '.xls']:
            return self.doc_processor.process_excel(file_path)
        
        # Word
        elif ext in ['.docx', '.doc']:
            return self.doc_processor.process_word(file_path)
        
        # Text
        elif ext == '.txt':
            return self.doc_processor.process_text(file_path)
        
        else:
            logger.warning(f"Unsupported file type: {ext}")
            return []
    
    def _process_pdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Process PDF with fallback strategy."""
        # Try Docling first
        try:
            return self._extract_with_docling(pdf_path)
        except Exception as e:
            logger.warning(f"Docling failed for {pdf_path.name}: {e}")
        
        # Try OCR + Docling
        try:
            ocr_pdf = self._apply_ocr(pdf_path)
            return self._extract_with_docling(ocr_pdf)
        except Exception as e:
            logger.warning(f"OCR+Docling failed for {pdf_path.name}: {e}")
        
        # Final fallback: PyMuPDF
        try:
            return self._extract_with_pymupdf(pdf_path)
        except Exception as e:
            logger.error(f"All extraction methods failed for {pdf_path.name}: {e}")
            return []
    
    def _extract_with_docling(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Extract content using Docling with structure, tables, and images."""
        try:
            from docling.document_converter import DocumentConverter
            
            converter = DocumentConverter()
            result = converter.convert(str(pdf_path))
            
            chunks = []
            doc_id = pdf_path.stem
            
            # Export to markdown for structure-aware chunking
            markdown_text = result.document.export_to_markdown()
            output_md = OUTPUT_DIR / f"{doc_id}.md"
            output_md.write_text(markdown_text)
            
            # Chunk the markdown with structure awareness
            text_chunks = self._chunk_structured_text(markdown_text, doc_id, pdf_path)
            
            # Mark as text content
            for chunk in text_chunks:
                chunk["content_type"] = "text"
                chunk["extraction_method"] = "docling"
            
            chunks.extend(text_chunks)
            
            # Extract tables if available
            try:
                if hasattr(result.document, 'tables') and result.document.tables:
                    for idx, table in enumerate(result.document.tables):
                        table_text = str(table)  # Get table representation
                        if table_text.strip():
                            chunks.append({
                                "text": f"Table {idx + 1}:\n{table_text}",
                                "doc_id": doc_id,
                                "page": None,  # Table may span pages
                                "section": f"Table {idx + 1}",
                                "chunk_id": f"{doc_id}_table_{idx}",
                                "content_type": "table",
                                "extraction_method": "docling"
                            })
                    logger.info(f"Extracted {len(result.document.tables)} tables from {pdf_path.name}")
            except Exception as e:
                logger.debug(f"Could not extract tables: {e}")
            
            # Note: Images would require additional processing
            # For now, Docling's markdown export includes image descriptions
            
            return chunks
        except Exception as e:
            raise Exception(f"Docling extraction failed: {e}")
    
    def _apply_ocr(self, pdf_path: Path) -> Path:
        """Apply OCR to PDF using ocrmypdf."""
        output_path = OUTPUT_DIR / f"{pdf_path.stem}_ocr.pdf"
        
        cmd = [
            "ocrmypdf",
            "--skip-text",
            "--optimize", "0",
            "--output-type", "pdf",
            str(pdf_path),
            str(output_path)
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        logger.info(f"OCR applied to {pdf_path.name}")
        return output_path
    
    def _extract_with_pymupdf(self, pdf_path: Path) -> List[Dict[str, Any]]:
        """Fallback extraction with PyMuPDF."""
        import fitz  # PyMuPDF
        
        chunks = []
        doc_id = pdf_path.stem
        
        doc = fitz.open(pdf_path)
        for page_num, page in enumerate(doc, start=1):
            text = page.get_text()
            if text.strip():
                # Simple chunking for fallback
                for i, chunk_text in enumerate(self._simple_chunk(text)):
                    chunks.append({
                        "text": chunk_text,
                        "doc_id": doc_id,
                        "page": page_num,
                        "section": f"Page {page_num}",
                        "chunk_id": f"{doc_id}_p{page_num}_c{i}"
                    })
        
        doc.close()
        return chunks
    
    def _chunk_structured_text(self, text: str, doc_id: str, pdf_path: Path) -> List[Dict[str, Any]]:
        """Structure-aware chunking preserving headings and sections."""
        chunks = []
        lines = text.split('\n')
        
        current_section = "Introduction"
        current_page = 1
        current_chunk = []
        current_length = 0
        chunk_idx = 0
        
        for line in lines:
            # Detect headings
            if line.startswith('#'):
                current_section = line.strip('#').strip()
                
            # Check if adding line would exceed chunk size
            line_length = len(line)
            if current_length + line_length > CHUNK_SIZE and current_chunk:
                # Save current chunk
                chunk_text = '\n'.join(current_chunk)
                if chunk_text.strip():
                    chunks.append({
                        "text": chunk_text,
                        "doc_id": doc_id,
                        "page": current_page,
                        "section": current_section,
                        "chunk_id": f"{doc_id}_c{chunk_idx}"
                    })
                    chunk_idx += 1
                
                # Start new chunk with overlap
                overlap_lines = current_chunk[-5:] if len(current_chunk) > 5 else current_chunk
                current_chunk = overlap_lines + [line]
                current_length = sum(len(l) for l in current_chunk)
            else:
                current_chunk.append(line)
                current_length += line_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = '\n'.join(current_chunk)
            if chunk_text.strip():
                chunks.append({
                    "text": chunk_text,
                    "doc_id": doc_id,
                    "page": current_page,
                    "section": current_section,
                    "chunk_id": f"{doc_id}_c{chunk_idx}"
                })
        
        return chunks
    
    def _simple_chunk(self, text: str) -> List[str]:
        """Simple text chunking with overlap."""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), CHUNK_SIZE - CHUNK_OVERLAP):
            chunk = ' '.join(words[i:i + CHUNK_SIZE])
            if chunk.strip():
                chunks.append(chunk)
        
        return chunks
    
    def _index_chunks(self, chunks: List[Dict[str, Any]]):
        """Index chunks into Chroma with rich metadata."""
        if not chunks:
            return
        
        # Enhance each chunk with metadata
        for chunk in chunks:
            # Add extraction metadata if not present
            if "extraction_method" not in chunk:
                chunk["extraction_method"] = "unknown"
            if "content_type" not in chunk:
                chunk["content_type"] = "text"
            
            # Extract keywords
            chunk["keywords"] = self._extract_keywords(chunk["text"])
            
            # Add ingestion timestamp
            chunk["ingested_at"] = datetime.now().isoformat()
        
        texts = [chunk["text"] for chunk in chunks]
        embeddings = self.embedding_model.encode(texts, show_progress_bar=False)
        
        # Build and validate all metadata first
        all_metadatas = []
        for i, chunk in enumerate(chunks):
            try:
                metadata = self._build_metadata(chunk)
                # Final validation - check for any None values
                has_none = any(v is None for v in metadata.values())
                if has_none:
                    logger.error(f"Chunk {i} ({chunk.get('chunk_id', 'unknown')}) has None in metadata: {[k for k, v in metadata.items() if v is None]}")
                    # Remove None values as last resort
                    metadata = {k: v for k, v in metadata.items() if v is not None}
                all_metadatas.append(metadata)
            except Exception as e:
                logger.error(f"Failed to build metadata for chunk {i}: {e}")
                # Use minimal metadata as fallback
                all_metadatas.append({
                    "doc_id": str(chunk.get("doc_id", "unknown")),
                    "page": 0
                })
        
        try:
            logger.info(f"Adding {len(chunks)} chunks to ChromaDB collection 'documents'")
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=texts,
                ids=[chunk["chunk_id"] for chunk in chunks],
                metadatas=all_metadatas
            )
            logger.info(f"Successfully added {len(chunks)} chunks to ChromaDB")
        except Exception as e:
            logger.error(f"Failed to add chunks to ChromaDB: {e}")
            raise
    
    def _build_metadata(self, chunk: Dict[str, Any]) -> Dict[str, Any]:
        """Build Chroma-compatible metadata (only str, int, float, bool) - STRICT None filtering."""
        # Start with empty metadata and only add non-None values
        metadata = {}
        
        # Required fields with defaults
        metadata["doc_id"] = str(chunk.get("doc_id", "unknown"))
        metadata["page"] = int(chunk.get("page") or 0)  # Convert None to 0
        
        # Optional string fields - only add if not None/empty
        section = chunk.get("section")
        if section:
            metadata["section"] = str(section)[:500]
        
        content_type = chunk.get("content_type")
        if content_type:
            metadata["content_type"] = str(content_type)
        
        extraction_method = chunk.get("extraction_method")
        if extraction_method:
            metadata["extraction_method"] = str(extraction_method)
        
        ingested_at = chunk.get("ingested_at")
        if ingested_at:
            metadata["ingested_at"] = str(ingested_at)
        
        # Add document type inference
        if "doc_type" in chunk and chunk["doc_type"]:
            metadata["doc_type"] = str(chunk["doc_type"])[:200]
        if "doc_category" in chunk and chunk["doc_category"]:
            metadata["doc_category"] = str(chunk["doc_category"])[:200]
        if "difficulty_hint" in chunk and chunk["difficulty_hint"]:
            metadata["difficulty_hint"] = str(chunk["difficulty_hint"])[:50]
        
        # Add AI enrichment metadata (ensure all values are valid)
        if "ai_enriched" in chunk and chunk.get("ai_enriched") is True:
            metadata["ai_enriched"] = True
            
            if "ai_summary" in chunk and chunk["ai_summary"]:
                metadata["ai_summary"] = str(chunk["ai_summary"])[:500]
            
            if "ai_concepts" in chunk and chunk["ai_concepts"]:
                metadata["ai_concepts"] = str(chunk["ai_concepts"])[:500]
            
            if "ai_category" in chunk and chunk["ai_category"]:
                metadata["ai_category"] = str(chunk["ai_category"])[:100]
            
            if "ai_difficulty" in chunk and chunk["ai_difficulty"]:
                metadata["ai_difficulty"] = str(chunk["ai_difficulty"])[:50]
        
        # Add keywords (join as string for Chroma) - only if not empty
        if "keywords" in chunk and chunk["keywords"]:
            keywords_list = [str(k) for k in chunk["keywords"][:5] if k]
            if keywords_list:
                metadata["keywords"] = ", ".join(keywords_list)
        
        # Add media type for videos (string only) - only if not None
        if "media_type" in chunk and chunk["media_type"]:
            metadata["media_type"] = str(chunk["media_type"])
        
        # Add timestamps for videos (must be float or int, not None)
        if "timestamp_start" in chunk and chunk["timestamp_start"] is not None:
            try:
                metadata["timestamp_start"] = float(chunk["timestamp_start"])
            except (ValueError, TypeError):
                pass
                
        if "timestamp_end" in chunk and chunk["timestamp_end"] is not None:
            try:
                metadata["timestamp_end"] = float(chunk["timestamp_end"])
            except (ValueError, TypeError):
                pass
        
        # Add frame path for video frames (string only) - only if not None
        if "frame_path" in chunk and chunk["frame_path"]:
            metadata["frame_path"] = str(chunk["frame_path"])[:500]
        
        # Add boolean flags for Excel - only if not None
        if "has_formulas" in chunk and chunk["has_formulas"] is not None:
            metadata["has_formulas"] = bool(chunk["has_formulas"])
        if "has_comments" in chunk and chunk["has_comments"] is not None:
            metadata["has_comments"] = bool(chunk["has_comments"])
        
        # FINAL AGGRESSIVE VALIDATION - Rebuild dict with only valid values
        validated_metadata = {}
        for key, value in metadata.items():
            # Absolutely skip None
            if value is None:
                logger.debug(f"Skipping None value for key: {key}")
                continue
            
            # Type-specific validation
            if isinstance(value, bool):
                # Booleans are always valid
                validated_metadata[key] = value
            elif isinstance(value, (int, float)):
                # Check for NaN, Inf
                try:
                    if value != value:  # NaN check
                        continue
                    if value in (float('inf'), float('-inf')):
                        continue
                    validated_metadata[key] = value
                except:
                    continue
            elif isinstance(value, str):
                # Only add non-empty, non-'None' strings
                if value and value not in ('None', 'null', ''):
                    validated_metadata[key] = value
            else:
                # Unknown type - log and skip
                logger.warning(f"Unknown metadata type for {key}: {type(value)}")
        
        # PARANOID CHECK - verify no None values made it through
        if any(v is None for v in validated_metadata.values()):
            logger.error(f"CRITICAL: None values in validated metadata: {[k for k, v in validated_metadata.items() if v is None]}")
            validated_metadata = {k: v for k, v in validated_metadata.items() if v is not None}
        
        return validated_metadata
    
    def _extract_keywords(self, text: str, max_keywords: int = 5) -> List[str]:
        """Extract keywords from text using frequency analysis."""
        # Stop words to exclude
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has',
            'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may',
            'might', 'can', 'this', 'that', 'these', 'those', 'it', 'its', 'with',
            'from', 'by', 'as', 'into', 'through', 'during', 'before', 'after',
            'above', 'below', 'between', 'under', 'again', 'further', 'then', 'once'
        }
        
        # Tokenize and filter
        words = text.lower().split()
        filtered_words = [
            w.strip('.,!?;:') 
            for w in words 
            if len(w) > 3 and w.lower() not in stop_words and w.isalpha()
        ]
        
        # Get most common
        word_counts = Counter(filtered_words)
        return [word for word, count in word_counts.most_common(max_keywords)]
    
    def _load_enrichment_cache(self) -> Dict[str, Dict[str, Any]]:
        """Load AI enrichment cache from disk."""
        if not AI_ENRICHMENT_ENABLED or not self.enrichment_cache_dir.exists():
            return {}
        
        cache = {}
        for enrichment_file in self.enrichment_cache_dir.glob("*_enrichment.json"):
            try:
                data = json.loads(enrichment_file.read_text())
                doc_id = data.get("doc_id")
                if doc_id:
                    cache[doc_id] = data
            except Exception as e:
                logger.warning(f"Failed to load enrichment {enrichment_file.name}: {e}")
        
        return cache
    
    def _enhance_chunks_with_metadata(
        self,
        chunks: List[Dict[str, Any]],
        file_path: Path
    ) -> List[Dict[str, Any]]:
        """
        Enhance chunks with file-level and AI-generated metadata.
        
        Args:
            chunks: List of chunk dictionaries
            file_path: Path to source file
            
        Returns:
            Enhanced chunks
        """
        if not chunks:
            return chunks
        
        doc_id = chunks[0].get("doc_id", file_path.stem)
        
        # Add document type inference
        doc_type = infer_doc_type(file_path)
        doc_category = get_doc_category(doc_type)
        difficulty_hint = get_difficulty_hint(file_path)
        
        # Get AI enrichment if available (SKIP FOR VIDEOS TEMPORARILY TO DEBUG)
        ai_enrichment = None
        is_video = file_path.suffix.lower() in ['.mp4', '.webm', '.avi', '.mov']
        
        if AI_ENRICHMENT_ENABLED and self.enrichment_cache and not is_video:
            # Try exact match
            ai_enrichment = self.enrichment_cache.get(doc_id)
            # Try without transcript suffix
            if not ai_enrichment and doc_id.endswith("_transcript"):
                ai_enrichment = self.enrichment_cache.get(doc_id.replace("_transcript", ""))
        
        # Enhance each chunk
        for chunk in chunks:
            # Add filename for easy identification
            chunk["filename"] = file_path.name
            
            # Add document type
            chunk["doc_type"] = doc_type
            chunk["doc_category"] = doc_category
            
            if difficulty_hint:
                chunk["difficulty_hint"] = difficulty_hint
            
            # Add AI enrichment metadata (only if values are not None/empty)
            if ai_enrichment:
                chunk["ai_enriched"] = True
                
                # Add summary (truncate for metadata)
                if "summary" in ai_enrichment and ai_enrichment["summary"]:
                    summary_str = str(ai_enrichment["summary"]).strip()
                    if summary_str and summary_str != "None":
                        chunk["ai_summary"] = summary_str[:500]
                
                # Add concepts as comma-separated string
                if "key_concepts" in ai_enrichment and ai_enrichment["key_concepts"]:
                    concepts = [str(c).strip() for c in ai_enrichment["key_concepts"][:10] if c]
                    if concepts:
                        chunk["ai_concepts"] = ", ".join(concepts)
                
                # Add category
                if "topic_category" in ai_enrichment and ai_enrichment["topic_category"]:
                    category_str = str(ai_enrichment["topic_category"]).strip()
                    if category_str and category_str != "None":
                        chunk["ai_category"] = category_str
                
                # Add difficulty
                if "difficulty" in ai_enrichment and ai_enrichment["difficulty"]:
                    difficulty_str = str(ai_enrichment["difficulty"]).strip()
                    if difficulty_str and difficulty_str != "None":
                        chunk["ai_difficulty"] = difficulty_str
        
        return chunks
