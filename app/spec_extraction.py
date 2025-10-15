"""YAML strategy specification extraction."""
import logging
from typing import Dict, Any
from pathlib import Path
import yaml
import requests
from datetime import datetime

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OUTPUT_DIR
from app.retrieval import HybridRetriever
from app.models import Citation, StrategySpec

logger = logging.getLogger(__name__)


class SpecExtractor:
    """Extracts structured strategy specs as YAML."""
    
    def __init__(self, retriever: HybridRetriever):
        """Initialize with retriever instance."""
        self.retriever = retriever
    
    def extract_spec(self, query: str, top_k: int = 10) -> Dict[str, Any]:
        """
        Extract strategy specification from documents.
        
        Uses retrieval to find relevant strategy docs, then prompts
        Ollama to extract structured YAML spec.
        """
        # Retrieve relevant documents
        results = self.retriever.retrieve(query, top_k=top_k)
        
        if not results:
            return {
                "answer": "No relevant strategy documents found.",
                "citations": [],
                "spec_file": None
            }
        
        # Build context
        context = self._build_strategy_context(results)
        
        # Generate structured spec
        spec_yaml = self._generate_spec_yaml(query, context)
        
        # Validate and save spec
        spec_file = self._save_spec(spec_yaml, query)
        
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
            "answer": f"Strategy spec extracted and saved to {spec_file}",
            "citations": citations,
            "spec_file": str(spec_file) if spec_file else None
        }
    
    def _build_strategy_context(self, results: list) -> str:
        """Build focused context for strategy extraction."""
        context_parts = []
        
        for i, result in enumerate(results, 1):
            doc_id = result['metadata'].get('doc_id', 'unknown')
            page = result['metadata'].get('page', 'N/A')
            context_parts.append(
                f"--- Source {i}: {doc_id} (Page {page}) ---\n{result['text']}\n"
            )
        
        return "\n".join(context_parts)
    
    def _generate_spec_yaml(self, query: str, context: str) -> str:
        """Generate YAML spec using Ollama."""
        schema_example = """
name: Example Strategy
description: Brief description of the strategy
timeframe: 5min / 15min / 1hour / daily
markets:
  - ES
  - NQ
entry_rules:
  - Price breaks above resistance
  - Volume confirms breakout
  - RSI > 50
exit_rules:
  - Target: 2x initial risk
  - Stop: Below entry support
  - Time-based: End of session
risk_management:
  max_risk_per_trade: 1.0%
  max_daily_loss: 3.0%
  position_size: Based on ATR
indicators:
  - name: EMA
    params:
      period: 20
  - name: RSI
    params:
      period: 14
notes: Additional context or considerations
"""
        
        prompt = f"""You are an expert trading strategy analyst. Based on the provided documentation, extract a complete trading strategy specification.

Documentation Context:
{context}

Query: {query}

Extract the strategy details and output ONLY valid YAML following this schema:
{schema_example}

Be precise and extract actual values from the documentation. If information is missing, use reasonable defaults or note it in the 'notes' field.

Output YAML only, no additional text:
"""
        
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 800
                    }
                },
                timeout=90
            )
            response.raise_for_status()
            
            # Extract YAML from response
            generated = response.json()['response']
            
            # Clean up response - extract YAML block if wrapped
            yaml_text = generated.strip()
            if "```yaml" in yaml_text:
                yaml_text = yaml_text.split("```yaml")[1].split("```")[0]
            elif "```" in yaml_text:
                yaml_text = yaml_text.split("```")[1].split("```")[0]
            
            return yaml_text.strip()
            
        except Exception as e:
            logger.error(f"Spec generation failed: {e}")
            # Return minimal valid YAML on error
            return f"""name: Error Extracting Strategy
description: Failed to extract strategy from documentation
timeframe: unknown
markets: []
entry_rules:
  - Error: {str(e)}
exit_rules: []
risk_management: {{}}
notes: Generation failed, please check logs
"""
    
    def _save_spec(self, spec_yaml: str, query: str) -> Path:
        """Validate and save spec to file."""
        try:
            # Validate YAML
            spec_dict = yaml.safe_load(spec_yaml)
            
            # Optional: Validate against Pydantic model
            try:
                StrategySpec(**spec_dict)
            except Exception as e:
                logger.warning(f"Spec validation warning: {e}")
            
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_query = "".join(c if c.isalnum() else "_" for c in query[:30])
            filename = f"strategy_spec_{safe_query}_{timestamp}.yaml"
            
            spec_file = OUTPUT_DIR / filename
            spec_file.write_text(spec_yaml)
            
            logger.info(f"Saved spec to {spec_file}")
            return spec_file
            
        except Exception as e:
            logger.error(f"Failed to save spec: {e}")
            # Save anyway as raw YAML
            fallback_file = OUTPUT_DIR / f"spec_raw_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml"
            fallback_file.write_text(spec_yaml)
            return fallback_file
