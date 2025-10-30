"""
Query Expander for GraphMind.

Generates diverse query variants for maximum recall.
"""
import logging
import asyncio
from typing import List, Optional
from app.models import Classification
from app.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class QueryExpander:
    """Generate diverse query expansions for better recall."""
    
    def __init__(self, model: str = "llama3.2:3b-instruct"):
        """
        Initialize query expander.
        
        Args:
            model: LLM model for expansion generation (default: llama3.2:3b-instruct)
        """
        self.llm = OllamaClient(default_model=model)
        self.model = model
    
    def expand(self, query: str, classification: Classification, max_expansions: int = 3) -> List[str]:
        """
        Generate diverse query expansions.
        
        Args:
            query: Improved query from uplifter
            classification: Query classification
            max_expansions: Maximum number of expansions (default: 3)
            
        Returns:
            List of expanded queries (up to max_expansions)
        """
        expansions = []
        
        # Expansion 1: Paraphrase
        if len(expansions) < max_expansions:
            try:
                paraphrase = self._generate_paraphrase(query)
                if paraphrase and paraphrase != query:
                    expansions.append(paraphrase)
            except Exception as e:
                logger.warning(f"Paraphrase generation failed: {e}")
        
        # Expansion 2: Aspect/Facet Sub-query
        if len(expansions) < max_expansions:
            try:
                aspect_query = self._generate_aspect_query(query, classification)
                if aspect_query and aspect_query != query:
                    expansions.append(aspect_query)
            except Exception as e:
                logger.warning(f"Aspect query generation failed: {e}")
        
        # Expansion 3: HyDE (Hypothetical Document Embeddings)
        if len(expansions) < max_expansions:
            try:
                hyde_query = self._generate_hyde(query, classification)
                if hyde_query and hyde_query != query:
                    expansions.append(hyde_query)
            except Exception as e:
                logger.warning(f"HyDE generation failed: {e}")
        
        # Ensure diversity (remove duplicates)
        unique_expansions = self._ensure_diversity(expansions, query)
        
        return unique_expansions[:max_expansions]
    
    def _generate_paraphrase(self, query: str) -> str:
        """Generate paraphrase of query."""
        system = """Generate a paraphrase of the user's query.
Use synonyms and different phrasing but preserve the exact meaning.
Output ONLY the paraphrased query, nothing else.
Do not add explanations or additional text."""
        
        try:
            response = self.llm.generate(
                prompt=f"Paraphrase: {query}",
                model=self.model,
                temperature=0.3,
                max_tokens=100,
                timeout=10
            )
            
            # Clean response
            paraphrase = response.strip()
            # Remove quotes if present
            if paraphrase.startswith('"') and paraphrase.endswith('"'):
                paraphrase = paraphrase[1:-1]
            if paraphrase.startswith("'") and paraphrase.endswith("'"):
                paraphrase = paraphrase[1:-1]
            
            # Remove explanatory prefixes
            for prefix in ["Paraphrase:", "Paraphrased query:", "Here's the paraphrase:", "Query:"]:
                if paraphrase.lower().startswith(prefix.lower()):
                    paraphrase = paraphrase[len(prefix):].strip()
            
            return paraphrase
            
        except Exception as e:
            logger.error(f"Paraphrase generation failed: {e}")
            return ""
    
    def _generate_aspect_query(self, query: str, classification: Classification) -> str:
        """Generate aspect/facet-based sub-query."""
        # Determine focus area based on classification
        focus_areas = {
            "Q&A": "strategy, indicators, risk management, or market conditions",
            "compare": "specific comparison criteria, performance metrics, or use cases",
            "summarize": "key points, main findings, or critical insights",
            "code": "implementation details, code structure, or specific functions"
        }
        
        focus = focus_areas.get(classification.task_type, "specific aspects")
        
        system = f"""Generate a focused sub-query that explores a specific aspect of the main query.
Focus on: {focus}
Task type: {classification.task_type}

Output ONLY the sub-query, nothing else.
Do not add explanations or additional text."""
        
        try:
            response = self.llm.generate(
                prompt=f"Main query: {query}\n\nGenerate focused sub-query:",
                model=self.model,
                temperature=0.4,
                max_tokens=80,
                timeout=10
            )
            
            # Clean response
            aspect_query = response.strip()
            # Remove quotes if present
            if aspect_query.startswith('"') and aspect_query.endswith('"'):
                aspect_query = aspect_query[1:-1]
            if aspect_query.startswith("'") and aspect_query.endswith("'"):
                aspect_query = aspect_query[1:-1]
            
            # Remove explanatory prefixes
            for prefix in ["Sub-query:", "Focused query:", "Aspect query:", "Query:", "Here"]:
                if aspect_query.lower().startswith(prefix.lower()):
                    aspect_query = aspect_query[len(prefix):].strip()
                    # Remove colon if present
                    if aspect_query.startswith(":"):
                        aspect_query = aspect_query[1:].strip()
            
            return aspect_query
            
        except Exception as e:
            logger.error(f"Aspect query generation failed: {e}")
            return ""
    
    def _generate_hyde(self, query: str, classification: Classification) -> str:
        """Generate HyDE (Hypothetical Document Embedding) - a sample answer."""
        system = """Generate a hypothetical answer to the query as it might appear in a relevant document.
This should be factual-sounding text that would help retrieve similar documents.
Include specific terminology and concepts.
Use 2-3 sentences.

Output ONLY the hypothetical answer, nothing else.
Do not add explanations or additional text."""
        
        try:
            response = self.llm.generate(
                prompt=f"Generate hypothetical answer for query: {query}",
                model=self.model,
                temperature=0.3,
                max_tokens=150,
                timeout=10
            )
            
            # Clean response
            hyde = response.strip()
            # Remove quotes if present
            if hyde.startswith('"') and hyde.endswith('"'):
                hyde = hyde[1:-1]
            if hyde.startswith("'") and hyde.endswith("'"):
                hyde = hyde[1:-1]
            
            # Remove explanatory prefixes
            for prefix in ["Hypothetical answer:", "Answer:", "Here's", "The hypothetical"]:
                if hyde.lower().startswith(prefix.lower()):
                    hyde = hyde[len(prefix):].strip()
                    # Remove colon if present
                    if hyde.startswith(":"):
                        hyde = hyde[1:].strip()
            
            return hyde
            
        except Exception as e:
            logger.error(f"HyDE generation failed: {e}")
            return ""
    
    def _ensure_diversity(self, expansions: List[str], original: str) -> List[str]:
        """
        Ensure expansions are diverse (different from each other and original).
        
        Args:
            expansions: List of expansion queries
            original: Original query
            
        Returns:
            List of diverse expansions
        """
        if not expansions:
            return []
        
        unique_expansions = []
        
        for expansion in expansions:
            # Check similarity to original (basic word overlap)
            if self._similarity(expansion, original) < 0.8:  # Allow some similarity
                # Check similarity to existing expansions
                is_diverse = True
                for existing in unique_expansions:
                    if self._similarity(expansion, existing) > 0.8:
                        is_diverse = False
                        break
                
                if is_diverse:
                    unique_expansions.append(expansion)
        
        return unique_expansions
    
    def _similarity(self, query1: str, query2: str) -> float:
        """
        Calculate simple similarity between two queries (0.0-1.0).
        
        Uses word overlap as a simple similarity measure.
        """
        words1 = set(word.lower() for word in query1.split() if len(word) > 2)
        words2 = set(word.lower() for word in query2.split() if len(word) > 2)
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        if union == 0:
            return 0.0
        
        return intersection / union
