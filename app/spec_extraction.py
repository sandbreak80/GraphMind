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
    
    def extract_spec(self, query: str, top_k: int = 15) -> Dict[str, Any]:
        """
        Extract comprehensive trading strategy specification for production bot development.
        
        Uses enhanced retrieval and production-grade LLM to extract detailed,
        actionable trading strategy specifications suitable for automated trading.
        """
        # Retrieve relevant documents with higher k for better coverage
        results = self.retriever.retrieve(query, top_k=top_k)
        
        if not results:
            return {
                "answer": "No relevant strategy documents found.",
                "citations": [],
                "spec_file": None,
                "strategy_quality": "No data"
            }
        
        # Build comprehensive context
        context = self._build_production_strategy_context(results)
        
        # Generate detailed production spec
        spec_yaml = self._generate_production_spec_yaml(query, context)
        
        # Validate and save spec
        spec_file = self._save_spec(spec_yaml, query)
        
        # Build detailed citations
        citations = [
            Citation(
                text=result['text'][:300] + "...",
                doc_id=result['metadata'].get('doc_id') or result['metadata'].get('file_name', 'unknown'),
                page=result['metadata'].get('page'),
                section=result['metadata'].get('section'),
                score=result['rerank_score']
            )
            for result in results
        ]
        
        # Analyze strategy completeness
        strategy_quality = self._analyze_strategy_completeness(spec_yaml)
        
        return {
            "answer": f"Production-ready strategy spec extracted and saved to {spec_file}",
            "citations": citations,
            "spec_file": str(spec_file) if spec_file else None,
            "strategy_quality": strategy_quality,
            "total_sources": len(results),
            "extraction_timestamp": datetime.now().isoformat()
        }
    
    def _build_production_strategy_context(self, results: list) -> str:
        """Build comprehensive context for production strategy extraction."""
        context_parts = []
        
        for i, result in enumerate(results, 1):
            doc_id = result['metadata'].get('doc_id', 'unknown')
            page = result['metadata'].get('page', 'N/A')
            section = result['metadata'].get('section', 'N/A')
            content_type = result['metadata'].get('content_type', 'unknown')
            ai_enriched = result['metadata'].get('ai_enriched', False)
            
            context_parts.append(
                f"--- Source {i}: {doc_id} (Page {page}, Section: {section}, Type: {content_type}, AI-Enhanced: {ai_enriched}) ---\n{result['text']}\n"
            )
        
        return "\n".join(context_parts)
    
    def _analyze_strategy_completeness(self, spec_yaml: str) -> str:
        """Analyze the completeness of the extracted strategy."""
        try:
            spec_dict = yaml.safe_load(spec_yaml)
            
            required_fields = ['name', 'entry_rules', 'exit_rules', 'risk_management']
            missing_fields = [field for field in required_fields if not spec_dict.get(field)]
            
            if not missing_fields:
                return "Complete - Ready for production"
            elif len(missing_fields) <= 2:
                return f"Mostly complete - Missing: {', '.join(missing_fields)}"
            else:
                return f"Incomplete - Missing: {', '.join(missing_fields)}"
        except:
            return "Unable to analyze - Invalid YAML"
    
    def _generate_production_spec_yaml(self, query: str, context: str) -> str:
        """Generate comprehensive production-ready YAML spec using advanced LLM."""
        from app.config import PRODUCTION_LLM_MODEL, MAX_TOKENS, TEMPERATURE, TOP_P, TIMEOUT
        
        schema_example = """
name: "Strategy Name"
description: "Detailed strategy description"
timeframe: "5min"  # 1min, 5min, 15min, 1hour, 4hour, daily
markets:
  - "ES"  # E-mini S&P 500
  - "NQ"  # E-mini NASDAQ
entry_rules:
  - condition: "Price breaks above resistance level"
    parameters:
      resistance_level: "Previous high + 2 ticks"
      confirmation: "Volume > 1.5x average"
  - condition: "RSI crosses above 50"
    parameters:
      rsi_period: 14
      timeframe: "5min"
  - condition: "EMA alignment"
    parameters:
      fast_ema: 9
      slow_ema: 21
      direction: "bullish"
exit_rules:
  - type: "profit_target"
    condition: "Price reaches 2:1 risk/reward ratio"
    parameters:
      target_distance: "2x stop_loss_distance"
  - type: "stop_loss"
    condition: "Price breaks below entry support"
    parameters:
      stop_distance: "10 ticks"
  - type: "time_based"
    condition: "End of trading session"
    parameters:
      exit_time: "15:45 CT"
risk_management:
  max_risk_per_trade: "1.0%"
  max_daily_loss: "3.0%"
  position_sizing_method: "ATR_based"
  atr_multiplier: 2.0
  max_positions: 3
indicators:
  - name: "EMA"
    parameters:
      period: 21
      timeframe: "5min"
  - name: "RSI"
    parameters:
      period: 14
      timeframe: "5min"
  - name: "Volume"
    parameters:
      period: 20
      threshold: 1.5
market_conditions:
  trend: "uptrend"
  volatility: "normal"
  session: "regular_hours"
  news_events: "avoid_high_impact"
implementation_notes:
  - "Requires real-time data feed"
  - "Backtest on 6+ months of data"
  - "Paper trade for 2 weeks before live"
  - "Monitor for 1 hour after entry"
edge_cases:
  - "Gap openings: Skip trade"
  - "Low volume: Reduce position size"
  - "News events: Close positions"
performance_metrics:
  win_rate_target: ">60%"
  profit_factor_target: ">1.5"
  max_drawdown_limit: "<10%"
"""
        
        prompt = f"""You are an expert quantitative trading analyst specializing in Emini futures strategies. Extract a comprehensive, production-ready trading strategy specification from the provided documentation.

DOCUMENTATION CONTEXT:
{context}

TRADING QUERY: {query}

REQUIREMENTS FOR PRODUCTION TRADING BOT:
1. Extract specific, quantifiable entry and exit conditions
2. Include precise risk management parameters
3. Specify exact market conditions and timeframes
4. Provide concrete examples with price levels, indicators, and parameters
5. Include implementation considerations for automated trading
6. Address edge cases and risk scenarios
7. Make all rules programmable and measurable

OUTPUT FORMAT: Valid YAML following this comprehensive schema:
{schema_example}

EXTRACTION GUIDELINES:
- Be extremely precise with numbers, percentages, and timeframes
- Extract actual values from the documentation, don't make assumptions
- If information is missing, clearly note it in the 'notes' field
- Focus on rules that can be programmed into a trading bot
- Include specific parameter values for all indicators and conditions
- Ensure all conditions are binary (true/false) for programmability

Output ONLY valid YAML, no additional text or explanations:
"""
        
        try:
            response = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": PRODUCTION_LLM_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": TEMPERATURE,
                        "num_predict": MAX_TOKENS,
                        "top_p": TOP_P,
                        "repeat_penalty": 1.1,
                        "stop": ["Human:", "User:", "Question:", "Context:"]
                    }
                },
                timeout=TIMEOUT
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
            logger.error(f"Production spec generation failed: {e}")
            # Return minimal valid YAML on error
            return f"""name: "Error Extracting Strategy"
description: "Failed to extract strategy from documentation: {str(e)}"
timeframe: "unknown"
markets: []
entry_rules:
  - condition: "Error occurred during extraction"
    parameters: {{}}
exit_rules: []
risk_management: {{}}
indicators: []
market_conditions: {{}}
implementation_notes:
  - "Generation failed, please check logs"
edge_cases: []
performance_metrics: {{}}
notes: "Extraction failed - {str(e)}"
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
