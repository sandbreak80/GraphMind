"""Advanced hybrid retrieval with semantic chunking and hierarchical indexing."""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
import chromadb
from chromadb.config import Settings

logger = logging.getLogger(__name__)

@dataclass
class SemanticChunk:
    """Represents a semantically meaningful chunk of text."""
    text: str
    chunk_id: str
    document_id: str
    start_pos: int
    end_pos: int
    semantic_type: str  # 'concept', 'example', 'definition', 'strategy', 'analysis'
    importance_score: float
    keywords: List[str]
    parent_chunk_id: Optional[str] = None
    child_chunk_ids: List[str] = None

@dataclass
class HierarchicalIndex:
    """Hierarchical index structure for documents."""
    document_id: str
    title: str
    sections: List[Dict[str, Any]]
    concepts: List[str]
    strategies: List[str]
    examples: List[str]
    level: int  # 0=document, 1=section, 2=subsection, 3=chunk

class AdvancedHybridRetriever:
    """Advanced hybrid retrieval with semantic chunking and hierarchical indexing."""
    
    def __init__(self, chroma_client, embedding_model: SentenceTransformer):
        self.chroma_client = chroma_client
        self.embedding_model = embedding_model
        self.collection = chroma_client.get_or_create_collection("documents")  # Use existing collection
        
        # BM25 for keyword matching
        self.bm25_docs = []
        self.bm25_model = None
        
        # Semantic chunking parameters
        self.chunk_size = 512
        self.chunk_overlap = 50
        self.semantic_threshold = 0.7
        
        # Hierarchical indexing
        self.hierarchical_index = {}
        
        # Performance tracking
        self.retrieval_stats = {
            'total_queries': 0,
            'avg_response_time': 0.0,
            'cache_hits': 0,
            'semantic_hits': 0,
            'bm25_hits': 0
        }
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> None:
        """Add documents with advanced semantic chunking and hierarchical indexing."""
        logger.info(f"Adding {len(documents)} documents with advanced processing...")
        
        all_chunks = []
        all_texts = []
        
        for doc in documents:
            # Create hierarchical index
            hierarchical_index = self._create_hierarchical_index(doc)
            self.hierarchical_index[doc['id']] = hierarchical_index
            
            # Generate semantic chunks
            chunks = self._create_semantic_chunks(doc, hierarchical_index)
            all_chunks.extend(chunks)
            all_texts.extend([chunk.text for chunk in chunks])
        
        # Update BM25 model
        self.bm25_docs = all_texts
        self.bm25_model = BM25Okapi([text.split() for text in all_texts])
        
        # Add to ChromaDB with metadata
        if all_chunks:
            chunk_texts = [chunk.text for chunk in all_chunks]
            chunk_ids = [chunk.chunk_id for chunk in all_chunks]
            chunk_embeddings = self.embedding_model.encode(chunk_texts)
            
            # Prepare metadata
            metadatas = []
            for chunk in all_chunks:
                metadata = {
                    'document_id': chunk.document_id,
                    'chunk_id': chunk.chunk_id,
                    'semantic_type': chunk.semantic_type,
                    'importance_score': chunk.importance_score,
                    'keywords': ','.join(chunk.keywords),
                    'parent_chunk_id': chunk.parent_chunk_id or '',
                    'child_chunk_ids': ','.join(chunk.child_chunk_ids or []),
                    'start_pos': chunk.start_pos,
                    'end_pos': chunk.end_pos
                }
                metadatas.append(metadata)
            
            # Add to collection
            self.collection.add(
                embeddings=chunk_embeddings.tolist(),
                documents=chunk_texts,
                metadatas=metadatas,
                ids=chunk_ids
            )
        
        logger.info(f"Added {len(all_chunks)} semantic chunks from {len(documents)} documents")
    
    async def load_existing_documents(self) -> None:
        """Load existing documents from the collection for advanced processing."""
        try:
            # Get all documents from the existing collection
            results = self.collection.get(include=['documents', 'metadatas'])
            
            if not results['documents']:
                logger.info("No existing documents found in collection")
                return
            
            logger.info(f"Found {len(results['documents'])} existing documents, processing for advanced retrieval...")
            
            # Process existing documents
            documents = []
            for i, (doc_text, metadata) in enumerate(zip(results['documents'], results['metadatas'])):
                doc = {
                    'id': metadata.get('id', f'doc_{i}'),
                    'title': metadata.get('title', f'Document {i}'),
                    'text': doc_text,
                    'source': metadata.get('source', 'unknown')
                }
                documents.append(doc)
            
            # Add documents with advanced processing
            await self.add_documents(documents)
            
        except Exception as e:
            logger.error(f"Error loading existing documents: {e}")
    
    def _create_hierarchical_index(self, document: Dict[str, Any]) -> HierarchicalIndex:
        """Create hierarchical index structure for a document."""
        text = document.get('text', '')
        title = document.get('title', 'Untitled')
        
        # Extract sections (simple heuristic - can be enhanced)
        sections = self._extract_sections(text)
        
        # Extract concepts, strategies, and examples
        concepts = self._extract_concepts(text)
        strategies = self._extract_strategies(text)
        examples = self._extract_examples(text)
        
        return HierarchicalIndex(
            document_id=document['id'],
            title=title,
            sections=sections,
            concepts=concepts,
            strategies=strategies,
            examples=examples,
            level=0
        )
    
    def _extract_sections(self, text: str) -> List[Dict[str, Any]]:
        """Extract document sections."""
        sections = []
        lines = text.split('\n')
        current_section = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
                
            # Detect section headers (simple heuristic)
            if (len(line) < 100 and 
                (line.isupper() or 
                 line.startswith('#') or 
                 any(word in line.lower() for word in ['section', 'chapter', 'part', 'strategy', 'method']))):
                
                if current_section:
                    sections.append(current_section)
                
                current_section = {
                    'title': line,
                    'start_line': i,
                    'end_line': i,
                    'content': line
                }
            elif current_section:
                current_section['content'] += '\n' + line
                current_section['end_line'] = i
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _extract_concepts(self, text: str) -> List[str]:
        """Extract trading concepts from text."""
        concepts = []
        concept_keywords = [
            'moving average', 'rsi', 'macd', 'bollinger bands', 'support', 'resistance',
            'trend', 'momentum', 'volatility', 'liquidity', 'volume', 'price action',
            'technical analysis', 'fundamental analysis', 'risk management', 'portfolio'
        ]
        
        text_lower = text.lower()
        for concept in concept_keywords:
            if concept in text_lower:
                concepts.append(concept)
        
        return concepts
    
    def _extract_strategies(self, text: str) -> List[str]:
        """Extract trading strategies from text."""
        strategies = []
        strategy_keywords = [
            'mean reversion', 'momentum trading', 'arbitrage', 'hedging', 'scalping',
            'swing trading', 'day trading', 'position trading', 'algorithmic trading',
            'high frequency trading', 'market making', 'statistical arbitrage'
        ]
        
        text_lower = text.lower()
        for strategy in strategy_keywords:
            if strategy in text_lower:
                strategies.append(strategy)
        
        return strategies
    
    def _extract_examples(self, text: str) -> List[str]:
        """Extract examples from text."""
        examples = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if (line.startswith('Example:') or 
                line.startswith('For example') or 
                line.startswith('Consider') or
                'for instance' in line.lower()):
                examples.append(line)
        
        return examples
    
    def _create_semantic_chunks(self, document: Dict[str, Any], hierarchical_index: HierarchicalIndex) -> List[SemanticChunk]:
        """Create semantic chunks from document."""
        text = document.get('text', '')
        doc_id = document['id']
        
        chunks = []
        sentences = text.split('. ')
        current_chunk = ""
        current_pos = 0
        chunk_id = 0
        
        for i, sentence in enumerate(sentences):
            sentence = sentence.strip()
            if not sentence:
                continue
            
            # Check if adding this sentence would exceed chunk size
            if len(current_chunk) + len(sentence) > self.chunk_size and current_chunk:
                # Create chunk from current content
                chunk = self._create_chunk(
                    text=current_chunk,
                    doc_id=doc_id,
                    chunk_id=f"{doc_id}_chunk_{chunk_id}",
                    start_pos=current_pos - len(current_chunk),
                    end_pos=current_pos,
                    hierarchical_index=hierarchical_index
                )
                chunks.append(chunk)
                chunk_id += 1
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-self.chunk_overlap:] if len(current_chunk) > self.chunk_overlap else current_chunk
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk += " " + sentence if current_chunk else sentence
            
            current_pos += len(sentence) + 2  # +2 for ". "
        
        # Add final chunk
        if current_chunk:
            chunk = self._create_chunk(
                text=current_chunk,
                doc_id=doc_id,
                chunk_id=f"{doc_id}_chunk_{chunk_id}",
                start_pos=current_pos - len(current_chunk),
                end_pos=current_pos,
                hierarchical_index=hierarchical_index
            )
            chunks.append(chunk)
        
        return chunks
    
    def _create_chunk(self, text: str, doc_id: str, chunk_id: str, start_pos: int, 
                     end_pos: int, hierarchical_index: HierarchicalIndex) -> SemanticChunk:
        """Create a semantic chunk with metadata."""
        # Determine semantic type
        semantic_type = self._classify_semantic_type(text, hierarchical_index)
        
        # Calculate importance score
        importance_score = self._calculate_importance_score(text, hierarchical_index)
        
        # Extract keywords
        keywords = self._extract_keywords(text)
        
        return SemanticChunk(
            text=text,
            chunk_id=chunk_id,
            document_id=doc_id,
            start_pos=start_pos,
            end_pos=end_pos,
            semantic_type=semantic_type,
            importance_score=importance_score,
            keywords=keywords,
            child_chunk_ids=[]
        )
    
    def _classify_semantic_type(self, text: str, hierarchical_index: HierarchicalIndex) -> str:
        """Classify the semantic type of a chunk."""
        text_lower = text.lower()
        
        # Check for definitions
        if any(word in text_lower for word in ['is defined as', 'refers to', 'means', 'definition']):
            return 'definition'
        
        # Check for examples
        if any(word in text_lower for word in ['example', 'for instance', 'consider', 'suppose']):
            return 'example'
        
        # Check for strategies
        if any(word in text_lower for word in ['strategy', 'method', 'approach', 'technique']):
            return 'strategy'
        
        # Check for analysis
        if any(word in text_lower for word in ['analysis', 'evaluate', 'compare', 'assess']):
            return 'analysis'
        
        # Check for concepts
        if any(concept in text_lower for concept in hierarchical_index.concepts):
            return 'concept'
        
        return 'general'
    
    def _calculate_importance_score(self, text: str, hierarchical_index: HierarchicalIndex) -> float:
        """Calculate importance score for a chunk."""
        score = 0.0
        text_lower = text.lower()
        
        # Higher score for concepts
        for concept in hierarchical_index.concepts:
            if concept in text_lower:
                score += 0.3
        
        # Higher score for strategies
        for strategy in hierarchical_index.strategies:
            if strategy in text_lower:
                score += 0.4
        
        # Higher score for examples
        for example in hierarchical_index.examples:
            if example in text_lower:
                score += 0.2
        
        # Higher score for technical terms
        technical_terms = ['algorithm', 'implementation', 'code', 'formula', 'calculation']
        for term in technical_terms:
            if term in text_lower:
                score += 0.1
        
        # Normalize to 0.0-1.0
        return min(score, 1.0)
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        # Simple keyword extraction (can be enhanced with NLP)
        words = text.lower().split()
        keywords = []
        
        # Filter for meaningful words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        for word in words:
            if (len(word) > 3 and 
                word not in stop_words and 
                word.isalpha() and
                word not in keywords):
                keywords.append(word)
        
        return keywords[:10]  # Limit to top 10 keywords
    
    async def retrieve_advanced(self, query: str, top_k: int = 10, 
                              semantic_weight: float = 0.7, 
                              bm25_weight: float = 0.3) -> List[Dict[str, Any]]:
        """Advanced hybrid retrieval with semantic chunking."""
        start_time = time.time()
        self.retrieval_stats['total_queries'] += 1
        
        # Parallel retrieval
        semantic_task = asyncio.create_task(self._semantic_search(query, top_k * 2))
        bm25_task = asyncio.create_task(self._bm25_search_advanced(query, top_k * 2))
        
        semantic_results, bm25_results = await asyncio.gather(semantic_task, bm25_task)
        
        # Combine and rerank results
        combined_results = self._combine_and_rerank(
            semantic_results, bm25_results, 
            semantic_weight, bm25_weight, top_k
        )
        
        # Update stats
        response_time = time.time() - start_time
        self.retrieval_stats['avg_response_time'] = (
            (self.retrieval_stats['avg_response_time'] * (self.retrieval_stats['total_queries'] - 1) + response_time) 
            / self.retrieval_stats['total_queries']
        )
        
        logger.info(f"Advanced retrieval completed in {response_time:.2f}s, returned {len(combined_results)} results")
        
        return combined_results
    
    async def _semantic_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Semantic search using embeddings."""
        try:
            query_embedding = self.embedding_model.encode(query)
            
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=top_k,
                include=['documents', 'metadatas', 'distances']
            )
            
            semantic_results = []
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            )):
                semantic_results.append({
                    'text': doc,
                    'metadata': metadata,
                    'score': 1.0 - distance,  # Convert distance to similarity
                    'type': 'semantic'
                })
            
            self.retrieval_stats['semantic_hits'] += len(semantic_results)
            return semantic_results
            
        except Exception as e:
            logger.error(f"Semantic search error: {e}")
            return []
    
    async def _bm25_search_advanced(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Advanced BM25 search with keyword matching."""
        try:
            if not self.bm25_model:
                return []
            
            query_words = query.lower().split()
            scores = self.bm25_model.get_scores(query_words)
            
            # Get top results
            top_indices = np.argsort(scores)[::-1][:top_k]
            
            bm25_results = []
            for idx in top_indices:
                if scores[idx] > 0:
                    bm25_results.append({
                        'text': self.bm25_docs[idx],
                        'score': scores[idx],
                        'type': 'bm25'
                    })
            
            self.retrieval_stats['bm25_hits'] += len(bm25_results)
            return bm25_results
            
        except Exception as e:
            logger.error(f"BM25 search error: {e}")
            return []
    
    def _combine_and_rerank(self, semantic_results: List[Dict], bm25_results: List[Dict],
                          semantic_weight: float, bm25_weight: float, top_k: int) -> List[Dict[str, Any]]:
        """Combine and rerank results from both methods."""
        # Create a combined score for each unique text
        text_scores = {}
        
        # Add semantic scores
        for result in semantic_results:
            text = result['text']
            score = result['score'] * semantic_weight
            if text in text_scores:
                text_scores[text]['score'] += score
                text_scores[text]['semantic_score'] = result['score']
            else:
                text_scores[text] = {
                    'text': text,
                    'score': score,
                    'semantic_score': result['score'],
                    'bm25_score': 0.0,
                    'metadata': result.get('metadata', {}),
                    'type': 'hybrid'
                }
        
        # Add BM25 scores
        for result in bm25_results:
            text = result['text']
            score = result['score'] * bm25_weight
            if text in text_scores:
                text_scores[text]['score'] += score
                text_scores[text]['bm25_score'] = result['score']
            else:
                text_scores[text] = {
                    'text': text,
                    'score': score,
                    'semantic_score': 0.0,
                    'bm25_score': result['score'],
                    'metadata': {},
                    'type': 'hybrid'
                }
        
        # Sort by combined score and return top_k
        sorted_results = sorted(text_scores.values(), key=lambda x: x['score'], reverse=True)
        
        return sorted_results[:top_k]
    
    def get_retrieval_stats(self) -> Dict[str, Any]:
        """Get retrieval performance statistics."""
        return {
            'total_queries': self.retrieval_stats['total_queries'],
            'avg_response_time': self.retrieval_stats['avg_response_time'],
            'semantic_hits': self.retrieval_stats['semantic_hits'],
            'bm25_hits': self.retrieval_stats['bm25_hits'],
            'cache_hits': self.retrieval_stats['cache_hits'],
            'hierarchical_documents': len(self.hierarchical_index)
        }