"""
Prompt Uplifter for GraphMind.

Transforms vague prompts into clear, actionable queries for better retrieval.
"""
import logging
import re
from typing import Dict, Optional
from app.models import Classification, UpliftedPrompt
from app.ollama_client import OllamaClient

logger = logging.getLogger(__name__)


class PromptUplifter:
    """Transform vague prompts into clear, constrained forms."""
    
    def __init__(self, model: str = "llama3.2:3b-instruct"):
        """
        Initialize prompt uplifter.
        
        Args:
            model: LLM model for uplift generation (default: llama3.2:3b-instruct)
        """
        self.llm = OllamaClient(default_model=model)
        self.model = model
        self.templates = self._load_templates()
    
    def uplift(self, prompt: str, classification: Classification) -> UpliftedPrompt:
        """
        Uplift a prompt to be more specific and actionable.
        
        Args:
            prompt: Original user query
            classification: Classification from PromptClassifier
            
        Returns:
            UpliftedPrompt with improved version
        """
        try:
            # Build uplift prompt based on classification
            uplift_system = self._build_uplift_system_prompt(classification)
            
            # Generate improved prompt
            response = self.llm.generate(
                prompt=f"Original query: {prompt}\n\nImprove this query for better retrieval:",
                model=self.model,
                temperature=0.2,
                max_tokens=200,
                timeout=30
            )
            
            improved = self._parse_uplift_response(response, prompt)
            
            # Validate improvement
            if not self._validate_uplift(prompt, improved):
                logger.warning(f"Uplift validation failed, using template fallback")
                # Fall back to template-based uplift
                improved = self._template_uplift(prompt, classification)
            
            # Check for fact injection
            if self._detect_fact_injection(prompt, improved):
                logger.warning(f"Fact injection detected, using template fallback")
                improved = self._template_uplift(prompt, classification)
            
            # Score uplift quality
            confidence = self._score_uplift_quality(prompt, improved)
            
            return UpliftedPrompt(
                original=prompt,
                improved=improved,
                classification=classification,
                confidence=confidence
            )
            
        except Exception as e:
            logger.error(f"Uplift failed: {e}, using template fallback")
            # Fall back to template-based uplift
            improved = self._template_uplift(prompt, classification)
            confidence = self._score_uplift_quality(prompt, improved)
            
            return UpliftedPrompt(
                original=prompt,
                improved=improved,
                classification=classification,
                confidence=confidence
            )
    
    def _build_uplift_system_prompt(self, classification: Classification) -> str:
        """Build system prompt for uplift based on classification."""
        base = """You are a query optimization specialist. Transform vague queries into clear, specific prompts.

RULES:
1. Preserve user intent (NO NEW FACTS)
2. Add clarity and structure
3. Include: objective, audience, length, citation requirements
4. Auto-inject "cite sources" for knowledge tasks
5. Keep it concise (max 2-3 sentences added)
6. Do NOT add specific facts, numbers, names, or details not in the original query

Example transformations:
- "trading strategies" → "Provide 3-5 specific trading strategies with risk profiles. Include: strategy name, entry/exit criteria, risk management. Cite specific documents/sources. Format as markdown list."
- "RSI" → "Explain the RSI (Relative Strength Index) indicator: calculation, interpretation (overbought >70, oversold <30), and practical trading applications. Include specific examples and cite sources."

"""
        
        # Add task-specific guidance
        if classification.task_type == "Q&A":
            base += "\nFor Q&A: Add specificity, expected answer structure, and citation directive."
        elif classification.task_type == "summarize":
            base += "\nFor summaries: Specify summary length (3-5 bullets), key topics to cover, and citation requirement."
        elif classification.task_type == "compare":
            base += "\nFor comparisons: List specific comparison criteria, format (table or structured list), cite sources for each item."
        elif classification.task_type == "code":
            base += "\nFor code: Specify programming language, code structure, and include comments/examples."
        
        # Add output format guidance
        if classification.output_format == "table":
            base += "\nOutput format: Use a comparison table format."
        elif classification.output_format == "json":
            base += "\nOutput format: Request structured JSON response."
        
        return base
    
    def _parse_uplift_response(self, response: str, original: str) -> str:
        """Parse LLM response to extract improved query."""
        # Remove common prefixes/suffixes that LLMs might add
        response = response.strip()
        
        # Remove quotes if present
        if response.startswith('"') and response.endswith('"'):
            response = response[1:-1]
        if response.startswith("'") and response.endswith("'"):
            response = response[1:-1]
        
        # Remove explanatory text before/after the query
        # Look for patterns like "Improved query:" or "Here's the improved version:"
        lines = response.split('\n')
        query_lines = []
        in_query = False
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this looks like the start of the query
            if any(phrase in line.lower() for phrase in ['improved query:', 'here', 'the improved', 'query:', 'version:']):
                # Take everything after this line
                in_query = True
                # Extract the query part after the colon
                parts = line.split(':', 1)
                if len(parts) > 1 and parts[1].strip():
                    query_lines.append(parts[1].strip())
                continue
            
            if in_query or not any(phrase in line.lower() for phrase in ['improved', 'query', 'version', 'here']):
                query_lines.append(line)
        
        if query_lines:
            improved = ' '.join(query_lines)
        else:
            improved = response
        
        # If improved is shorter than original, something went wrong
        if len(improved.split()) < len(original.split()):
            improved = original
        
        return improved.strip()
    
    def _template_uplift(self, prompt: str, classification: Classification) -> str:
        """Template-based uplift as fallback."""
        templates = {
            "Q&A": f"Provide a detailed answer to: {prompt}. Include specific examples, cite sources, and format as markdown.",
            "summarize": f"Summarize the following topic in 3-5 key points: {prompt}. Cite sources for each point.",
            "compare": f"Compare and contrast: {prompt}. Use a structured format, cite sources, include pros/cons.",
            "code": f"Provide code implementation for: {prompt}. Include comments and examples. Cite sources if applicable.",
        }
        
        template = templates.get(classification.task_type, templates["Q&A"])
        
        # Ensure citation directive is present
        if "cite" not in template.lower() and "source" not in template.lower():
            template += " Cite sources."
        
        return template
    
    def _validate_uplift(self, original: str, improved: str) -> bool:
        """Validate that uplift preserves intent and doesn't add facts."""
        # Check that improved is longer but not TOO much longer
        original_words = len(original.split())
        improved_words = len(improved.split())
        
        if improved_words > original_words * 3:
            return False  # Too verbose
        
        if improved_words < original_words:
            return False  # Didn't actually improve
        
        # Check that original query is contained or paraphrased
        # Remove common words and check overlap
        original_keywords = set(word.lower() for word in original.split() if len(word) > 3)
        improved_keywords = set(word.lower() for word in improved.split() if len(word) > 3)
        
        # Should have some overlap (at least 30% of original keywords)
        overlap = len(original_keywords & improved_keywords)
        if len(original_keywords) > 0 and overlap < len(original_keywords) * 0.3:
            return False  # Not enough overlap
        
        return True
    
    def _detect_fact_injection(self, original: str, improved: str) -> bool:
        """
        Detect if uplift added new facts (POLICY VIOLATION).
        
        Returns:
            True if fact injection detected, False otherwise
        """
        # Extract entities/numbers from both
        original_numbers = set(re.findall(r'\b\d+\.?\d*\b', original))
        improved_numbers = set(re.findall(r'\b\d+\.?\d*\b', improved))
        
        # Check for new numbers (excluding common ones like "3-5", "2024", etc.)
        new_numbers = improved_numbers - original_numbers
        # Filter out common structural numbers
        structural_numbers = {'1', '2', '3', '4', '5', '10', '20', '30', '100', '200', '2024', '2025'}
        fact_numbers = new_numbers - structural_numbers
        
        if fact_numbers:
            logger.warning(f"Detected new numbers in uplift: {fact_numbers}")
            return True
        
        # Extract tickers/indicators from original
        original_tickers = set(re.findall(r'\b[A-Z]{1,5}\b', original))
        improved_tickers = set(re.findall(r'\b[A-Z]{1,5}\b', improved))
        
        # Check for new tickers (excluding common words)
        common_words = {'RSI', 'MACD', 'EMA', 'SMA', 'VWAP', 'ATR', 'BB', 'ADX', 'CCI'}
        new_tickers = (improved_tickers - original_tickers) - common_words
        
        if new_tickers:
            logger.warning(f"Detected new tickers in uplift: {new_tickers}")
            return True
        
        return False
    
    def _score_uplift_quality(self, original: str, improved: str) -> float:
        """Score the quality of uplift (0.0-1.0)."""
        score = 0.0
        
        # Has citation directive?
        if "cite" in improved.lower() or "source" in improved.lower():
            score += 0.3
        
        # Has format directive?
        if any(word in improved.lower() for word in ["markdown", "list", "table", "json", "format"]):
            score += 0.2
        
        # Increased specificity?
        original_words = len(original.split())
        improved_words = len(improved.split())
        if improved_words > original_words * 1.5:
            score += 0.3
        
        # Has structure indicators?
        if any(word in improved.lower() for word in ["include:", "format:", "criteria:", "provide:", "explain:"]):
            score += 0.2
        
        return min(1.0, score)
    
    def _load_templates(self) -> Dict[str, str]:
        """Load uplift templates."""
        return {
            "Q&A": "Provide a detailed answer to: {prompt}. Include specific examples, cite sources, and format as markdown.",
            "summarize": "Summarize the following topic in 3-5 key points: {prompt}. Cite sources for each point.",
            "compare": "Compare and contrast: {prompt}. Use a structured format, cite sources, include pros/cons.",
            "code": "Provide code implementation for: {prompt}. Include comments and examples. Cite sources if applicable.",
        }
