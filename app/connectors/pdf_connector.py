# GraphMind PDF Connector
# PDF document connector for GraphMind

import logging
from typing import Dict, List, Any, Optional
import os
from pathlib import Path
import asyncio

from .base_connector import BaseConnector

logger = logging.getLogger(__name__)

class PDFConnector(BaseConnector):
    """
    PDF document connector for GraphMind.
    
    This connector handles PDF document processing and retrieval
    for the GraphMind RAG framework.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize the PDF connector."""
        super().__init__(config)
        self.name = "PDF Connector"
        self.document_path = config.get('document_path', './documents')
        self.supported_formats = ['.pdf']
        self._initialize_pdf_processing()
    
    def _initialize_pdf_processing(self):
        """Initialize PDF processing capabilities."""
        # Import PDF processing libraries
        try:
            import PyPDF2
            import fitz  # PyMuPDF
            self.pdf_available = True
            logger.info("PDF processing libraries available")
        except ImportError as e:
            logger.warning(f"PDF processing libraries not available: {e}")
            self.pdf_available = False
    
    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields for PDF connector."""
        return ['name', 'document_path']
    
    async def connect(self) -> bool:
        """Test connection to PDF documents."""
        try:
            if not self.pdf_available:
                logger.error("PDF processing libraries not available")
                return False
            
            doc_path = Path(self.document_path)
            if not doc_path.exists():
                logger.error(f"Document path does not exist: {self.document_path}")
                return False
            
            # Check if there are any PDF files
            pdf_files = list(doc_path.glob("*.pdf"))
            if not pdf_files:
                logger.warning(f"No PDF files found in: {self.document_path}")
                return False
            
            self.connection = True
            logger.info(f"PDF connector connected to {len(pdf_files)} PDF files")
            return True
            
        except Exception as e:
            logger.error(f"PDF connector connection failed: {e}")
            return False
    
    async def search(self, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search PDF documents."""
        try:
            if not self.connection:
                await self.connect()
            
            if not self.connection:
                return []
            
            results = []
            doc_path = Path(self.document_path)
            
            # Search through all PDF files
            for pdf_file in doc_path.glob("*.pdf"):
                try:
                    file_results = await self._search_pdf_file(pdf_file, query, **kwargs)
                    results.extend(file_results)
                except Exception as e:
                    logger.error(f"Error searching PDF {pdf_file}: {e}")
                    continue
            
            # Sort by relevance score
            results.sort(key=lambda x: x.get('score', 0), reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"PDF search failed: {e}")
            return []
    
    async def _search_pdf_file(self, pdf_file: Path, query: str, **kwargs) -> List[Dict[str, Any]]:
        """Search a single PDF file."""
        try:
            import fitz  # PyMuPDF
            
            results = []
            doc = fitz.open(pdf_file)
            
            # Search through all pages
            for page_num in range(doc.page_count):
                page = doc[page_num]
                text = page.get_text()
                
                # Simple text search
                if query.lower() in text.lower():
                    # Extract relevant text around the query
                    context = self._extract_context(text, query)
                    
                    results.append({
                        'text': context,
                        'metadata': {
                            'doc_id': pdf_file.name,
                            'file_name': pdf_file.name,
                            'page': page_num + 1,
                            'doc_type': 'pdf',
                            'source': 'pdf_connector'
                        },
                        'score': self._calculate_relevance_score(text, query)
                    })
            
            doc.close()
            return results
            
        except Exception as e:
            logger.error(f"Error processing PDF {pdf_file}: {e}")
            return []
    
    def _extract_context(self, text: str, query: str, context_length: int = 200) -> str:
        """Extract context around the query."""
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Find query position
        query_pos = text_lower.find(query_lower)
        if query_pos == -1:
            return text[:context_length] + "..."
        
        # Extract context around query
        start = max(0, query_pos - context_length // 2)
        end = min(len(text), query_pos + len(query) + context_length // 2)
        
        context = text[start:end]
        if start > 0:
            context = "..." + context
        if end < len(text):
            context = context + "..."
        
        return context
    
    def _calculate_relevance_score(self, text: str, query: str) -> float:
        """Calculate relevance score for text."""
        query_lower = query.lower()
        text_lower = text.lower()
        
        # Simple scoring based on query frequency
        query_count = text_lower.count(query_lower)
        text_length = len(text_lower)
        
        if text_length == 0:
            return 0.0
        
        # Normalize score
        score = min(1.0, query_count / (text_length / 1000))
        return score
    
    async def get_metadata(self) -> Dict[str, Any]:
        """Get PDF connector metadata."""
        try:
            doc_path = Path(self.document_path)
            pdf_files = list(doc_path.glob("*.pdf"))
            
            total_pages = 0
            total_size = 0
            
            for pdf_file in pdf_files:
                try:
                    import fitz
                    doc = fitz.open(pdf_file)
                    total_pages += doc.page_count
                    total_size += pdf_file.stat().st_size
                    doc.close()
                except Exception as e:
                    logger.error(f"Error getting metadata for {pdf_file}: {e}")
                    continue
            
            return {
                'connector': self.name,
                'document_path': str(self.document_path),
                'total_files': len(pdf_files),
                'total_pages': total_pages,
                'total_size_bytes': total_size,
                'supported_formats': self.supported_formats
            }
            
        except Exception as e:
            logger.error(f"Failed to get PDF metadata: {e}")
            return {
                'connector': self.name,
                'error': str(e)
            }
    
    def get_supported_formats(self) -> List[str]:
        """Get supported file formats."""
        return self.supported_formats
    
    def get_search_capabilities(self) -> Dict[str, Any]:
        """Get search capabilities."""
        return {
            'text_search': True,
            'metadata_search': True,
            'faceted_search': False,
            'full_text_search': True,
            'page_search': True
        }
    
    async def close(self):
        """Close the PDF connector."""
        self.connection = False
        logger.info("PDF connector closed")
