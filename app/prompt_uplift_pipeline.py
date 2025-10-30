"""
Prompt Uplift Pipeline for GraphMind.

Orchestrates prompt classification, uplift, and expansion.
"""
import logging
import hashlib
import json
import time
from typing import Dict, Optional, Any
from app.models import Classification, UpliftedPrompt, ProcessedQuery
from app.prompt_classifier import PromptClassifier
from app.prompt_uplifter import PromptUplifter
from app.query_expander import QueryExpander
from app.caching import RedisQueryCache
from app.monitoring.prompt_uplift_metrics import prompt_uplift_metrics

logger = logging.getLogger(__name__)


class PromptUpliftPipeline:
    """Complete prompt uplift and expansion pipeline."""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize prompt uplift pipeline.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or self._default_config()
        
        # Initialize components
        self.classifier = PromptClassifier(model=self.config.get("classifier_model", "llama3.2:3b-instruct"))
        self.uplifter = PromptUplifter(model=self.config.get("uplifter_model", "llama3.2:3b-instruct"))
        self.expander = QueryExpander(model=self.config.get("expander_model", "llama3.2:3b-instruct"))
        
        # Initialize cache if enabled
        self.cache = None
        if self.config.get("cache_enabled", True):
            try:
                from app.caching import redis_query_cache
                self.cache = redis_query_cache  # Use global instance
            except Exception as e:
                logger.warning(f"Redis cache initialization failed: {e}, caching disabled")
                self.cache = None
    
    def process(self, prompt: str, context: Optional[Dict] = None) -> ProcessedQuery:
        """
        Process a user prompt through the complete pipeline.
        
        Args:
            prompt: Raw user query
            context: Optional context dictionary (user_id, conversation_id, previous_hits, etc.)
            
        Returns:
            ProcessedQuery with improved prompt, expansions, and metadata
        """
        start_time = time.time()
        context = context or {}
        
        # Check cache first
        cache_key = self._get_cache_key(prompt, context)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for prompt: {prompt[:50]}")
            prompt_uplift_metrics.record_cache_hit()
            return cached_result
        
        prompt_uplift_metrics.record_cache_miss()
        
        # Step 1: Classify
        classify_start = time.time()
        classification = self.classifier.classify(prompt, context)
        classify_latency = time.time() - classify_start
        prompt_uplift_metrics.record_latency("classify", classify_latency)
        prompt_uplift_metrics.record_classification(classification.task_type)
        
        # Step 2: Uplift
        uplift_start = time.time()
        uplifted = self.uplifter.uplift(prompt, classification)
        uplift_latency = time.time() - uplift_start
        prompt_uplift_metrics.record_latency("uplift", uplift_latency)
        prompt_uplift_metrics.record_confidence(uplifted.confidence)
        
        # Step 3: Confidence check
        if uplifted.confidence < self.config.get("confidence_threshold", 0.75):
            logger.debug(f"Low confidence ({uplifted.confidence:.2f}), falling back to original")
            prompt_uplift_metrics.record_fallback()
            # Low confidence - fall back to original
            result = ProcessedQuery(
                final_query=prompt,
                expansions=[],
                used_original=True,
                classification=classification,
                uplift_confidence=uplifted.confidence,
                metadata={
                    "original": prompt,
                    "task_type": classification.task_type,
                    "entities": classification.entities,
                    "complexity": classification.complexity,
                    "latency_ms": (time.time() - start_time) * 1000,
                    "cache_hit": False
                }
            )
            self._set_cache(cache_key, result)
            prompt_uplift_metrics.record_latency("total", time.time() - start_time)
            return result
        
        # Step 4: Expand (if not skipped)
        expansions = []
        if not self._should_skip_expansion(classification, context):
            try:
                expand_start = time.time()
                expansions = self.expander.expand(
                    uplifted.improved,
                    classification,
                    max_expansions=self.config.get("expansion_count", 3)
                )
                expand_latency = time.time() - expand_start
                prompt_uplift_metrics.record_latency("expand", expand_latency)
                prompt_uplift_metrics.record_expansion_count(len(expansions))
            except Exception as e:
                logger.warning(f"Expansion failed: {e}")
                expansions = []
        else:
            prompt_uplift_metrics.record_skip_expansion()
        
        # Build result
        total_latency = time.time() - start_time
        result = ProcessedQuery(
            final_query=uplifted.improved,
            expansions=expansions,
            used_original=False,
            classification=classification,
            uplift_confidence=uplifted.confidence,
            metadata={
                "original": prompt,
                "task_type": classification.task_type,
                "entities": classification.entities,
                "complexity": classification.complexity,
                "latency_ms": total_latency * 1000,
                "cache_hit": False
            }
        )
        
        # Record total latency
        prompt_uplift_metrics.record_latency("total", total_latency)
        prompt_uplift_metrics.record_improvement_score(uplifted.confidence)
        
        # Cache result
        self._set_cache(cache_key, result)
        
        return result
    
    def _should_skip_expansion(self, classification: Classification, context: Dict) -> bool:
        """Determine if expansion should be skipped."""
        # Skip if previous query had ≥3 high-confidence hits
        if context.get("previous_hits", 0) >= self.config.get("skip_expansion_threshold", 3):
            logger.debug("Skipping expansion: previous query had good baseline")
            return True
        
        # Skip for very complex queries (they're already detailed)
        if classification.complexity == "complex" and classification.confidence > 0.9:
            logger.debug("Skipping expansion: query is already complex and high-confidence")
            return False  # Actually, let's still expand complex queries for better recall
        
        return False
    
    def _get_cache_key(self, prompt: str, context: Dict) -> str:
        """Generate cache key for prompt and context."""
        # Include user_id and conversation_id if present
        cache_data = {
            "prompt": prompt.lower().strip(),
            "user_id": context.get("user_id", ""),
            "conversation_id": context.get("conversation_id", "")
        }
        
        cache_string = json.dumps(cache_data, sort_keys=True)
        return f"uplift::{hashlib.md5(cache_string.encode()).hexdigest()}"
    
    def _get_from_cache(self, cache_key: str) -> Optional[ProcessedQuery]:
        """Get result from cache."""
        if not self.cache:
            return None
        
        try:
            # Use cache key as query, with special model identifier
            cached_data = self.cache.get(cache_key, "uplift_pipeline", {})
            if cached_data and isinstance(cached_data, dict):
                response = cached_data.get("response", cached_data)
                if response:
                    # Reconstruct ProcessedQuery from cached data
                    return self._deserialize_result(response)
        except Exception as e:
            logger.warning(f"Cache get failed: {e}")
        
        return None
    
    def _set_cache(self, cache_key: str, result: ProcessedQuery) -> None:
        """Store result in cache."""
        if not self.cache:
            return
        
        try:
            # Serialize result for caching
            cache_data = {
                "final_query": result.final_query,
                "expansions": result.expansions,
                "used_original": result.used_original,
                "uplift_confidence": result.uplift_confidence,
                "metadata": result.metadata,
                # Classification stored as dict for serialization
                "classification": {
                    "task_type": result.classification.task_type,
                    "required_sources": result.classification.required_sources,
                    "entities": result.classification.entities,
                    "output_format": result.classification.output_format,
                    "complexity": result.classification.complexity,
                    "confidence": result.classification.confidence
                }
            }
            self.cache.set(cache_key, "uplift_pipeline", cache_data, {})
        except Exception as e:
            logger.warning(f"Cache set failed: {e}")
    
    def _deserialize_result(self, data: Dict) -> ProcessedQuery:
        """Deserialize cached result into ProcessedQuery."""
        from app.models import Classification
        
        classification_data = data.get("classification", {})
        classification = Classification(
            task_type=classification_data.get("task_type", "Q&A"),
            required_sources=classification_data.get("required_sources", ["RAG"]),
            entities=classification_data.get("entities", {}),
            output_format=classification_data.get("output_format", "markdown"),
            complexity=classification_data.get("complexity", "medium"),
            confidence=classification_data.get("confidence", 0.75)
        )
        
        return ProcessedQuery(
            final_query=data.get("final_query", ""),
            expansions=data.get("expansions", []),
            used_original=data.get("used_original", False),
            classification=classification,
            uplift_confidence=data.get("uplift_confidence", 0.0),
            metadata=data.get("metadata", {})
        )
    
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration."""
        return {
            "expansion_count": 3,           # Max expansions
            "confidence_threshold": 0.75,   # Fallback to original if lower
            "enable_hyde": True,            # Enable HyDE expansion
            "max_tokens_uplift": 200,       # Max tokens for uplift
            "skip_expansion_threshold": 3,  # Skip if baseline finds 3+ hits
            "uplifter_model": "llama3.2:3b-instruct",
            "expander_model": "llama3.2:3b-instruct",
            "classifier_model": "llama3.2:3b-instruct",
            "cache_enabled": True,
            "cache_ttl_seconds": 3600,      # 1 hour
            "latency_budget_ms": 600        # Max acceptable latency
        }
