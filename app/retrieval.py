"""Hybrid retrieval with BM25, embeddings, and reranking."""
import logging
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import requests

from app.config import (
    CHROMA_DIR, EMBEDDING_MODEL, RERANKER_MODEL,
    BM25_TOP_K, EMBEDDING_TOP_K, RERANK_TOP_K,
    MIN_SIMILARITY_THRESHOLD,
    OLLAMA_BASE_URL, OLLAMA_MODEL
)
from app.models import Citation
from app.metrics import RetrievalMetrics

logger = logging.getLogger(__name__)


class HybridRetriever:
    """Hybrid retrieval combining BM25, embeddings, and reranking."""
    
    def __init__(self):
        """Initialize retriever with models and Chroma."""
        self.chroma_client = chromadb.PersistentClient(
            path=str(CHROMA_DIR),
            settings=Settings(anonymized_telemetry=False)
        )
        self.collection = self.chroma_client.get_or_create_collection(
            name="emini_docs",
            metadata={"hnsw:space": "cosine"}
        )
        
        self.embedding_model = SentenceTransformer(EMBEDDING_MODEL)
        self.reranker = CrossEncoder(RERANKER_MODEL)
        self.metrics = RetrievalMetrics()
        
        # Initialize BM25 index
        self._build_bm25_index()
        logger.info("Hybrid retriever initialized")
        logger.info(f"Retrieval config: BM25={BM25_TOP_K}, Embedding={EMBEDDING_TOP_K}, Rerank={RERANK_TOP_K}")
    
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
    
    def retrieve(self, query: str, top_k: int = RERANK_TOP_K, compute_metrics: bool = False) -> List[Dict[str, Any]]:
        """
        Hybrid retrieval pipeline:
        1. BM25 prefilter
        2. Embedding-based KNN
        3. Rerank with cross-encoder
        
        Args:
            query: Search query
            top_k: Number of final results
            compute_metrics: If True, compute and log retrieval metrics
        """
        # Stage 1: BM25 prefilter
        bm25_results = self._bm25_search(query, top_k=BM25_TOP_K)
        logger.info(f"BM25 retrieved: {len(bm25_results)} results")
        
        # Stage 2: Embedding search
        embedding_results = self._embedding_search(query, top_k=EMBEDDING_TOP_K)
        logger.info(f"Embedding retrieved: {len(embedding_results)} results")
        
        # Combine and deduplicate
        combined = self._merge_results(bm25_results, embedding_results)
        logger.info(f"Combined unique results: {len(combined)}")
        
        # Stage 3: Rerank
        reranked = self._rerank(query, combined, top_k=top_k)
        logger.info(f"Final reranked results: {len(reranked)}")
        
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
        """Rerank results using cross-encoder."""
        if not results:
            return []
        
        # Prepare pairs for reranking
        pairs = [[query, result['text']] for result in results]
        
        # Get reranking scores
        rerank_scores = self.reranker.predict(pairs)
        
        # Sort by rerank score
        for i, result in enumerate(results):
            result['rerank_score'] = float(rerank_scores[i])
        
        results.sort(key=lambda x: x['rerank_score'], reverse=True)
        
        return results[:top_k]
    
    def answer_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Answer query using retrieved context and Ollama."""
        # Retrieve relevant documents
        results = self.retrieve(query, top_k=top_k)
        
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
        answer = self._generate_answer(query, context)
        
        # Build citations
        citations = [
            Citation(
                text=result['text'][:200] + "...",
                doc_id=result['metadata'].get('doc_id', 'unknown'),
                page=result['metadata'].get('page'),
                section=result['metadata'].get('section'),
                score=result['rerank_score']
            )
            for result in results
        ]
        
        return {
            "answer": answer,
            "citations": citations
        }
    
    def _generate_answer(self, query: str, context: str) -> str:
        """Generate answer using Ollama."""
        prompt = f"""Based on the following context from EminiPlayer documentation, answer the question.

Context:
{context}

Question: {query}

Provide a clear, accurate answer based on the context. If the context doesn't contain enough information, say so.

Answer:"""
        
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "num_predict": 500
                    }
                },
                timeout=60
            )
            response.raise_for_status()
            return response.json()['response']
        except Exception as e:
            logger.error(f"Ollama generation failed: {e}")
            return f"Error generating answer: {str(e)}"
    
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
