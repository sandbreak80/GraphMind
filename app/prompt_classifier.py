"""
Prompt Classifier for GraphMind.

Classifies user queries to guide uplift and expansion strategies.
"""
import re
import logging
import json
from typing import Dict, List, Optional
from app.models import Classification
from app.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class PromptClassifier:
    """Classify prompts to guide uplift and expansion."""
    
    def __init__(self, model: str = "llama3.2:3b-instruct"):
        """
        Initialize prompt classifier.
        
        Args:
            model: LLM model for ambiguous queries (default: llama3.2:3b-instruct)
        """
        self.llm = OllamaClient(default_model=model)
        self.model = model
        
    def classify(self, prompt: str, context: Optional[Dict] = None) -> Classification:
        """
        Classify a user prompt.
        
        Args:
            prompt: Raw user query
            context: Optional conversation context
            
        Returns:
            Classification with task type, entities, requirements, etc.
        """
        # Rule-based signal extraction (fast, deterministic)
        signals = self._extract_signals(prompt)
        
        # LLM-based classification for ambiguous cases
        if self._is_ambiguous(signals):
            logger.debug(f"Query is ambiguous, using LLM classification: {prompt[:50]}")
            llm_classification = self._llm_classify(prompt)
            signals.update(llm_classification)
        
        # Determine required sources based on signals
        required_sources = self._determine_sources(signals)
        
        # Determine output format
        output_format = self._determine_output_format(signals, prompt)
        
        return Classification(
            task_type=signals.get("task_type", "Q&A"),
            required_sources=required_sources,
            entities={
                "tickers": signals.get("tickers", []),
                "indicators": signals.get("indicators", []),
                "dates": signals.get("dates", [])
            },
            output_format=output_format,
            complexity=signals.get("complexity", "medium"),
            confidence=signals.get("confidence", 0.75)
        )
    
    def _extract_signals(self, prompt: str) -> Dict:
        """Extract rule-based signals from prompt."""
        prompt_lower = prompt.lower()
        
        signals = {
            "has_urls": bool(re.search(r'https?://', prompt)),
            "has_dates": bool(re.search(r'today|this week|yesterday|Q[1-4]|202[0-9]|january|february|march|april|may|june|july|august|september|october|november|december', prompt_lower)),
            "has_tickers": self._extract_tickers(prompt),
            "has_vault_tags": bool(re.search(r'#\w+', prompt)),  # Obsidian tags
            "has_doc_refs": bool(re.search(r'pdf|report|transcript|document', prompt_lower)),
            "is_realtime": bool(re.search(r'latest|current|now|breaking|recent', prompt_lower)),
            "is_comparison": bool(re.search(r'compare|versus|vs|difference between|better than', prompt_lower)),
            "is_summary": bool(re.search(r'summarize|overview|summary|brief', prompt_lower)),
            "is_code": bool(re.search(r'code|function|class|implementation|debug|script|program', prompt_lower)),
            "indicators": self._extract_indicators(prompt_lower),
            "tickers": self._extract_tickers(prompt),
            "dates": self._extract_dates(prompt),
            "task_type": self._infer_task_type(prompt_lower),
            "complexity": self._estimate_complexity(prompt),
            "confidence": 0.85  # High for rule-based
        }
        
        return signals
    
    def _extract_tickers(self, prompt: str) -> List[str]:
        """Extract ticker symbols (ES, NQ, AAPL, etc.)."""
        # Match 1-5 uppercase letters (common ticker pattern)
        matches = re.findall(r'\b[A-Z]{1,5}\b', prompt)
        
        # Filter out common words (THE, AND, etc.)
        stopwords = {'THE', 'AND', 'OR', 'BUT', 'FOR', 'TO', 'OF', 'IN', 'ON', 'AT', 'BY', 'FROM', 'WITH', 'AS', 'IS', 'IT', 'ARE', 'WAS', 'WERE', 'BE', 'BEEN', 'BEING', 'HAVE', 'HAS', 'HAD', 'DO', 'DOES', 'DID', 'WILL', 'WOULD', 'SHOULD', 'COULD', 'MAY', 'MIGHT', 'CAN', 'MUST', 'SHALL'}
        
        # Also filter out common trading terms that aren't tickers
        trading_words = {'RSI', 'MACD', 'EMA', 'SMA', 'VWAP', 'ATR', 'BB', 'ADX', 'CCI', 'STOCH', 'RSI', 'MACD'}
        
        tickers = []
        for m in matches:
            if m not in stopwords and m not in trading_words:
                tickers.append(m)
        
        return list(set(tickers))  # Remove duplicates
    
    def _extract_indicators(self, prompt_lower: str) -> List[str]:
        """Extract technical indicators."""
        indicators = {
            'rsi': 'RSI',
            'macd': 'MACD',
            'ema': 'EMA',
            'sma': 'SMA',
            'vwap': 'VWAP',
            'atr': 'ATR',
            'bollinger': 'Bollinger',
            'stochastic': 'Stochastic',
            'adx': 'ADX',
            'cci': 'CCI',
            'williams': 'Williams',
            'moving average': 'MA',
            'relative strength index': 'RSI',
            'moving average convergence divergence': 'MACD'
        }
        
        found = []
        for keyword, indicator_name in indicators.items():
            if keyword in prompt_lower:
                if indicator_name not in found:
                    found.append(indicator_name)
        
        return found
    
    def _extract_dates(self, prompt: str) -> List[str]:
        """Extract date references."""
        date_patterns = [
            r'\b\d{4}\b',  # Years like 2024
            r'\bQ[1-4]\s*\d{4}\b',  # Quarters like Q3 2024
            r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}',  # Month dates
            r'\btoday\b',
            r'\byesterday\b',
            r'\bthis week\b',
            r'\blast week\b',
            r'\bthis month\b',
            r'\blast month\b'
        ]
        
        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, prompt, re.IGNORECASE)
            dates.extend(matches)
        
        return list(set(dates))
    
    def _infer_task_type(self, prompt_lower: str) -> str:
        """Infer task type from prompt."""
        if any(word in prompt_lower for word in ['summarize', 'overview', 'summary', 'brief']):
            return "summarize"
        elif any(word in prompt_lower for word in ['compare', 'versus', 'vs', 'difference', 'contrast']):
            return "compare"
        elif any(word in prompt_lower for word in ['code', 'implement', 'function', 'debug', 'script', 'program']):
            return "code"
        elif any(word in prompt_lower for word in ['how', 'what', 'why', 'when', 'where', 'explain', 'describe']):
            return "Q&A"
        else:
            return "Q&A"  # Default
    
    def _estimate_complexity(self, prompt: str) -> str:
        """Estimate query complexity."""
        word_count = len(prompt.split())
        
        if word_count < 10:
            return "simple"
        elif word_count < 30:
            return "medium"
        else:
            return "complex"
    
    def _is_ambiguous(self, signals: Dict) -> bool:
        """Check if classification is ambiguous (needs LLM)."""
        # If no clear signals, use LLM for classification
        has_clear_signals = (
            signals.get("has_doc_refs", False) or
            signals.get("has_vault_tags", False) or
            signals.get("is_realtime", False) or
            len(signals.get("tickers", [])) > 0 or
            len(signals.get("indicators", [])) > 0 or
            signals.get("task_type") != "Q&A"  # Non-default task type is a clear signal
        )
        return not has_clear_signals
    
    def _llm_classify(self, prompt: str) -> Dict:
        """Use LLM to classify ambiguous prompts."""
        system_prompt = """You are a query classifier. Analyze the user's query and return a JSON object with:
{
  "task_type": "Q&A|summarize|compare|code",
  "output_format": "markdown|json|table",
  "confidence": 0.0-1.0
}

Task types:
- Q&A: Questions asking for information or explanations
- summarize: Requests to summarize content
- compare: Requests to compare items
- code: Requests involving code or programming

Output format:
- markdown: General text formatting
- json: Structured data requests
- table: Comparison or tabular data

Return ONLY valid JSON, no other text."""

        try:
            response = self.llm.generate(
                prompt=f"Classify this query: {prompt}",
                model=self.model,
                temperature=0.1,
                max_tokens=100,
                timeout=10  # Short timeout for classification
            )
            
            # Try to extract JSON from response
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
                return {
                    "task_type": result.get("task_type", "Q&A"),
                    "output_format": result.get("output_format", "markdown"),
                    "confidence": float(result.get("confidence", 0.7))
                }
        except Exception as e:
            logger.warning(f"LLM classification failed: {e}, using defaults")
        
        # Fallback to defaults
        return {
            "task_type": "Q&A",
            "output_format": "markdown",
            "confidence": 0.5
        }
    
    def _determine_sources(self, signals: Dict) -> List[str]:
        """Determine required data sources based on signals."""
        sources = []
        
        if signals.get("has_doc_refs", False) or signals.get("has_tickers", []) or signals.get("indicators", []):
            sources.append("RAG")
        
        if signals.get("has_vault_tags", False):
            sources.append("Obsidian")
        
        if signals.get("is_realtime", False) or signals.get("has_urls", False):
            sources.append("Web")
        
        # Default to RAG if no clear signals
        if not sources:
            sources = ["RAG"]
        
        return sources
    
    def _determine_output_format(self, signals: Dict, prompt: str) -> str:
        """Determine expected output format."""
        prompt_lower = prompt.lower()
        
        if "json" in prompt_lower or "api" in prompt_lower:
            return "json"
        elif any(word in prompt_lower for word in ["table", "tabulate", "compare", "comparison"]):
            return "table"
        else:
            return signals.get("output_format", "markdown")
