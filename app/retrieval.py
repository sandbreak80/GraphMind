"""High-performance hybrid retrieval with BM25, embeddings, and reranking."""
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import requests
import asyncio
import concurrent.futures
from functools import lru_cache
import threading
import time
import numpy as np

from app.config import (
    CHROMA_DIR, EMBEDDING_MODEL, RERANKER_MODEL, COLLECTION_NAME,
    BM25_TOP_K, EMBEDDING_TOP_K, RERANK_TOP_K,
    MIN_SIMILARITY_THRESHOLD,
    OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TOP_K,
    MAX_WORKERS, BATCH_SIZE, EMBEDDING_BATCH_SIZE,
    ENABLE_AGGRESSIVE_CACHING, CACHE_EMBEDDINGS, CACHE_BM25_INDEX, CACHE_RERANKER
)
from app.models import Citation
from app.metrics import RetrievalMetrics

logger = logging.getLogger(__name__)


class HybridRetriever:
    """High-performance hybrid retrieval with parallel processing and aggressive caching."""
    
    def __init__(self):
        """Initialize retriever with models and Chroma."""
        # Initialize ChromaDB with persistent client
        self.chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )
        
        # Initialize models with caching
        self.embedding_model = self._load_embedding_model()
        self.reranker = self._load_reranker()
        self.metrics = RetrievalMetrics()
        
        # Initialize thread pool for parallel processing
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS)
        
        # Initialize caches
        self.embedding_cache = {}
        self.bm25_cache = {}
        self.reranker_cache = {}
        
        # Initialize BM25 index
        self._build_bm25_index()
        logger.info(f"High-performance HybridRetriever initialized with {MAX_WORKERS} workers")
        logger.info(f"Retrieval config: BM25={BM25_TOP_K}, Embedding={EMBEDDING_TOP_K}, Rerank={RERANK_TOP_K}")
    
    def _load_embedding_model(self):
        """Load embedding model with caching enabled."""
        if CACHE_EMBEDDINGS:
            return SentenceTransformer(EMBEDDING_MODEL, cache_folder="/tmp/embeddings_cache")
        return SentenceTransformer(EMBEDDING_MODEL)
    
    def _load_reranker(self):
        """Load reranker with caching enabled."""
        if CACHE_RERANKER:
            return CrossEncoder(RERANKER_MODEL, cache_folder="/tmp/reranker_cache")
        return CrossEncoder(RERANKER_MODEL)
    
    def _build_bm25_index(self):
        """Build BM25 index from Chroma collection."""
        try:
            # Get all documents
            results = self.collection.get()
            if not results['documents']:
                logger.warning("No documents in collection for BM25 index")
                self.bm25 = None
                self.bm25_docs = []
                self.bm25_ids = []
                self.bm25_metadatas = []
                return
            
            self.bm25_docs = results['documents']
            self.bm25_ids = results['ids']
            self.bm25_metadatas = results['metadatas']
            
            # Tokenize for BM25
            tokenized_docs = [doc.lower().split() for doc in self.bm25_docs]
            self.bm25 = BM25Okapi(tokenized_docs)
            logger.info(f"Built BM25 index with {len(self.bm25_docs)} documents")
        except Exception as e:
            logger.error(f"Failed to build BM25 index: {e}")
            self.bm25 = None
            self.bm25_docs = []
    
    def retrieve(self, query: str, top_k: int = RERANK_TOP_K, compute_metrics: bool = False, 
                 bm25_top_k: Optional[int] = None, embedding_top_k: Optional[int] = None, 
                 rerank_top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval pipeline:
        1. BM25 prefilter
        2. Embedding-based KNN
        3. Rerank with cross-encoder
        
        Args:
            query: Search query
            top_k: Number of final results
            compute_metrics: If True, compute and log retrieval metrics
            bm25_top_k: Number of BM25 results (overrides config)
            embedding_top_k: Number of embedding results (overrides config)
            rerank_top_k: Number of final reranked results (overrides top_k)
        """
        # Use provided parameters or fall back to config defaults
        bm25_k = bm25_top_k if bm25_top_k is not None else BM25_TOP_K
        embedding_k = embedding_top_k if embedding_top_k is not None else EMBEDDING_TOP_K
        final_k = rerank_top_k if rerank_top_k is not None else top_k
        
        # Stage 1: BM25 prefilter
        bm25_results = self._bm25_search(query, top_k=bm25_k)
        logger.info(f"BM25 retrieved: {len(bm25_results)} results (top_k={bm25_k})")
        
        # Stage 2: Embedding search
        embedding_results = self._embedding_search(query, top_k=embedding_k)
        logger.info(f"Embedding retrieved: {len(embedding_results)} results (top_k={embedding_k})")
        
        # Combine and deduplicate
        combined = self._merge_results(bm25_results, embedding_results)
        logger.info(f"Combined unique results: {len(combined)}")
        
        # Stage 3: Rerank
        reranked = self._rerank(query, combined, top_k=final_k)
        logger.info(f"Final reranked results: {len(reranked)} (top_k={final_k})")
        
        # Optional: Compute metrics for monitoring
        if compute_metrics and len(reranked) > 0:
            self._compute_and_log_metrics(query, reranked)
        
        return reranked
    
    async def retrieve_async(self, query: str, top_k: int = RERANK_TOP_K, compute_metrics: bool = False, 
                            bm25_top_k: Optional[int] = None, embedding_top_k: Optional[int] = None, 
                            rerank_top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Async hybrid retrieval pipeline with parallel BM25 and embedding search:
        1. BM25 prefilter + Embedding-based KNN (parallel)
        2. Rerank with cross-encoder
        
        Args:
            query: Search query
            top_k: Number of final results
            compute_metrics: If True, compute and log retrieval metrics
            bm25_top_k: Number of BM25 results (overrides config)
            embedding_top_k: Number of embedding results (overrides config)
            rerank_top_k: Number of final reranked results (overrides top_k)
        """
        # Use provided parameters or fall back to config defaults
        bm25_k = bm25_top_k if bm25_top_k is not None else BM25_TOP_K
        embedding_k = embedding_top_k if embedding_top_k is not None else EMBEDDING_TOP_K
        final_k = rerank_top_k if rerank_top_k is not None else top_k
        
        # Stage 1: Parallel BM25 and Embedding search
        start_time = time.time()
        bm25_task = asyncio.create_task(self._bm25_search_async(query, top_k=bm25_k))
        embedding_task = asyncio.create_task(self._embedding_search_async(query, top_k=embedding_k))
        
        # Wait for both searches to complete
        bm25_results, embedding_results = await asyncio.gather(bm25_task, embedding_task)
        
        parallel_time = time.time() - start_time
        logger.info(f"Parallel retrieval completed in {parallel_time:.2f}s")
        logger.info(f"BM25 retrieved: {len(bm25_results)} results (top_k={bm25_k})")
        logger.info(f"Embedding retrieved: {len(embedding_results)} results (top_k={embedding_k})")
        
        # Combine and deduplicate
        combined = self._merge_results(bm25_results, embedding_results)
        logger.info(f"Combined unique results: {len(combined)}")
        
        # Stage 2: Rerank
        rerank_start = time.time()
        reranked = self._rerank(query, combined, top_k=final_k)
        rerank_time = time.time() - rerank_start
        logger.info(f"Reranking completed in {rerank_time:.2f}s")
        logger.info(f"Final reranked results: {len(reranked)} (top_k={final_k})")
        
        # Optional: Compute metrics for monitoring
        if compute_metrics and len(reranked) > 0:
            self._compute_and_log_metrics(query, reranked)
        
        return reranked
    
    def _compute_and_log_metrics(self, query: str, results: List[Dict[str, Any]]):
        """Compute and log retrieval metrics."""
        try:
            # Estimate relevant docs (in production, use labeled test set)
            from app.metrics import estimate_relevant_docs
            
            all_docs = self.collection.get()
            all_chunks = [
                {"id": all_docs['ids'][i], "text": all_docs['documents'][i]}
                for i in range(len(all_docs['ids']))
            ]
            
            relevant_ids = estimate_relevant_docs(query, all_chunks)
            
            if relevant_ids:
                metrics = self.metrics.evaluate_retrieval(
                    query, results, relevant_ids, k_values=[5, 10, 20, 50, 100]
                )
                self.metrics.log_metrics(metrics, query)
        except Exception as e:
            logger.warning(f"Could not compute metrics: {e}")
    
    def _bm25_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """BM25 search over documents."""
        if not self.bm25 or not self.bm25_docs:
            return []
        
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top k indices
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:
                results.append({
                    "text": self.bm25_docs[idx],
                    "metadata": self.bm25_metadatas[idx],
                    "id": self.bm25_ids[idx],
                    "score": float(scores[idx]),
                    "source": "bm25"
                })
        
        return results
    
    async def _bm25_search_async(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Async BM25 search over documents."""
        # Run BM25 search in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._bm25_search, query, top_k)
    
    def _embedding_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Embedding-based vector search with similarity filtering."""
        try:
            query_embedding = self.embedding_model.encode(query)
            
            # Request more results for filtering
            fetch_k = min(top_k * 2, self.collection.count())
            
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=fetch_k
            )
            
            retrieved = []
            for i in range(len(results['ids'][0])):
                similarity = 1.0 - results['distances'][0][i]
                
                # Filter by minimum similarity threshold
                if similarity >= MIN_SIMILARITY_THRESHOLD:
                    retrieved.append({
                        "text": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "id": results['ids'][0][i],
                        "score": similarity,
                        "source": "embedding"
                    })
            
            # Return top k after filtering
            return retrieved[:top_k]
            
        except Exception as e:
            logger.error(f"Embedding search failed: {e}")
            return []
    
    async def _embedding_search_async(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Async embedding-based vector search with similarity filtering."""
        # Run embedding search in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self._embedding_search, query, top_k)
    
    def _merge_results(self, bm25_results: List[Dict], embedding_results: List[Dict]) -> List[Dict]:
        """Merge and deduplicate results from both methods."""
        seen_ids = set()
        merged = []
        
        # Combine both result sets
        all_results = bm25_results + embedding_results
        
        for result in all_results:
            if result['id'] not in seen_ids:
                seen_ids.add(result['id'])
                merged.append(result)
        
        return merged
    
    def _rerank(self, query: str, results: List[Dict], top_k: int) -> List[Dict[str, Any]]:
        """Rerank results using cross-encoder with batch processing for speed."""
        if not results:
            return []
        
        # Limit results to process for faster reranking
        max_rerank = min(len(results), 50)  # Process max 50 results for speed
        results_to_rerank = results[:max_rerank]
        
        # Prepare pairs for reranking
        pairs = [[query, result['text']] for result in results_to_rerank]
        
        # Get reranking scores with batch processing
        batch_size = 16  # Smaller batch size for faster processing
        rerank_scores = []
        
        for i in range(0, len(pairs), batch_size):
            batch_pairs = pairs[i:i + batch_size]
            batch_scores = self.reranker.predict(batch_pairs)
            rerank_scores.extend(batch_scores)
        
        # Sort by rerank score
        for i, result in enumerate(results_to_rerank):
            result['rerank_score'] = float(rerank_scores[i])
        
        results_to_rerank.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        # Add remaining results without reranking
        remaining_results = results[max_rerank:]
        for result in remaining_results:
            result['rerank_score'] = 0.0  # Default score for non-reranked results
        
        # Combine and sort all results
        all_results = results_to_rerank + remaining_results
        all_results.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        return all_results[:top_k]
    
    def answer_query(self, query: str, top_k: int = 5, conversation_history: Optional[List[Dict[str, str]]] = None, 
                     model: Optional[str] = None, bm25_top_k: Optional[int] = None, 
                     embedding_top_k: Optional[int] = None, rerank_top_k: Optional[int] = None) -> Dict[str, Any]:
        """Answer query using retrieved context and Ollama."""
        # Retrieve relevant documents with custom settings
        results = self.retrieve(
            query, 
            top_k=top_k,
            bm25_top_k=bm25_top_k,
            embedding_top_k=embedding_top_k,
            rerank_top_k=rerank_top_k
        )
    
    async def answer_query_async(self, query: str, top_k: int = 5, conversation_history: Optional[List[Dict[str, str]]] = None, 
                                model: Optional[str] = None, bm25_top_k: Optional[int] = None, 
                                embedding_top_k: Optional[int] = None, rerank_top_k: Optional[int] = None) -> Dict[str, Any]:
        """Answer query using retrieved context and Ollama with parallel processing."""
        # Retrieve relevant documents with custom settings using parallel processing
        results = await self.retrieve_async(
            query, 
            top_k=top_k,
            bm25_top_k=bm25_top_k,
            embedding_top_k=embedding_top_k,
            rerank_top_k=rerank_top_k
        )
        
        if not results:
            return {
                "answer": "No relevant documents found.",
                "citations": []
            }
        
        # Build context
        context_parts = []
        for i, result in enumerate(results, 1):
            doc_id = result['metadata'].get('doc_id', 'unknown')
            page = result['metadata'].get('page', 'N/A')
            section = result['metadata'].get('section', 'N/A')
            context_parts.append(
                f"[Source {i} - {doc_id}, Page {page}, {section}]\n{result['text']}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Generate answer with Ollama
        answer = self._generate_answer(query, context, conversation_history, model)
        
        # Build citations
        citations = [
            Citation(
                text=result['text'][:200] + "...",
                doc_id=result['metadata'].get('doc_id') or result['metadata'].get('file_name', 'unknown'),
                page=result['metadata'].get('page'),
                section=result['metadata'].get('section') or result['metadata'].get('doc_type', 'unknown'),
                score=result['rerank_score']
            )
            for result in results
        ]
        
        return {
            "answer": answer,
            "citations": citations
        }
    
    async def answer_query_async(self, query: str, top_k: int = 5, conversation_history: Optional[List[Dict[str, str]]] = None, 
                                model: Optional[str] = None, bm25_top_k: Optional[int] = None, 
                                embedding_top_k: Optional[int] = None, rerank_top_k: Optional[int] = None) -> Dict[str, Any]:
        """Answer query using retrieved context and Ollama with parallel processing."""
        # Retrieve relevant documents with custom settings using parallel processing
        results = await self.retrieve_async(
            query, 
            top_k=top_k,
            bm25_top_k=bm25_top_k,
            embedding_top_k=embedding_top_k,
            rerank_top_k=rerank_top_k
        )
        
        if not results:
            return {
                "answer": "No relevant documents found.",
                "citations": []
            }
        
        # Build context
        context_parts = []
        for i, result in enumerate(results, 1):
            doc_id = result['metadata'].get('doc_id', 'unknown')
            page = result['metadata'].get('page', 'N/A')
            section = result['metadata'].get('section', 'N/A')
            context_parts.append(
                f"[Source {i} - {doc_id}, Page {page}, {section}]\n{result['text']}\n"
            )
        
        context = "\n".join(context_parts)
        
        # Generate answer with Ollama
        answer = self._generate_answer(query, context, conversation_history, model)
        
        # Build citations
        citations = [
            Citation(
                text=result['text'][:200] + "...",
                doc_id=result['metadata'].get('doc_id') or result['metadata'].get('file_name', 'unknown'),
                page=result['metadata'].get('page'),
                section=result['metadata'].get('section') or result['metadata'].get('doc_type', 'unknown'),
                score=result['rerank_score']
            )
            for result in results
        ]
        
        return {
            "answer": answer,
            "citations": citations
        }
    
    def _generate_answer(self, query: str, context: str, conversation_history: Optional[List[Dict[str, str]]] = None, 
                         model: Optional[str] = None, system_prompt: Optional[str] = None, 
                         temperature: Optional[float] = None, max_tokens: Optional[int] = None, 
                         top_k_sampling: Optional[int] = None) -> str:
        """Generate comprehensive trading analysis using production-grade LLM."""
        from app.config import PRODUCTION_LLM_MODEL, MAX_TOKENS, TEMPERATURE, TOP_P, TIMEOUT
        
        # Use provided model or fallback to default
        llm_model = model or PRODUCTION_LLM_MODEL
        
        # Use provided parameters or fallback to config defaults
        llm_temperature = temperature if temperature is not None else TEMPERATURE
        llm_max_tokens = max_tokens if max_tokens is not None else MAX_TOKENS
        llm_top_k = top_k_sampling if top_k_sampling is not None else OLLAMA_TOP_K
        
        # Build conversation context if provided
        conversation_context = ""
        if conversation_history:
            conversation_context = "\n\nPREVIOUS CONVERSATION:\n"
            for msg in conversation_history[-10:]:  # Limit to last 10 messages
                role = "User" if msg.get('role') == 'user' else "Assistant"
                conversation_context += f"{role}: {msg.get('content', '')}\n"
            conversation_context += "\n"

        # Use system prompt if provided, otherwise use default
        if system_prompt:
            prompt = f"""{system_prompt}

CONTEXT FROM DOCUMENTATION:
{context}

{conversation_context}USER QUESTION: {query}"""
        else:
            prompt = f"""CONTEXT FROM DOCUMENTATION:
{context}

{conversation_context}USER QUESTION: {query}"""

        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": llm_model,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": llm_temperature,
                        "num_predict": llm_max_tokens,
                        "top_k": llm_top_k,
                        "top_p": TOP_P,
                        "repeat_penalty": 1.1,
                        "stop": ["Human:", "User:", "Question:"]
                    }
                },
                timeout=TIMEOUT
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            logger.error(f"Production LLM generation failed: {e}")
            return f"Error generating trading analysis: {str(e)}"
    
    def get_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        try:
            count = self.collection.count()
            return {
                "total_documents": count,
                "collection_name": self.collection.name,
                "bm25_indexed": len(self.bm25_docs) if self.bm25_docs else 0
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}
