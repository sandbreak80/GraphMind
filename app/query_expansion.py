"""Intelligent query expansion with synonyms and context awareness."""

import re
import logging
from typing import List, Dict, Any, Set, Tuple
from dataclasses import dataclass
import asyncio
import aiohttp
from collections import defaultdict

logger = logging.getLogger(__name__)

@dataclass
class ExpandedQuery:
    """Represents an expanded query with multiple variations."""
    original_query: str
    expanded_queries: List[str]
    synonyms: Dict[str, List[str]]
    context_terms: List[str]
    trading_terms: List[str]
    technical_terms: List[str]
    confidence_score: float
    expansion_strategy: str

class QueryExpander:
    """Intelligent query expansion with trading domain expertise."""
    
    def __init__(self):
        # Trading-specific synonym mappings
        self.trading_synonyms = {
            # Technical Analysis
            'moving average': ['ma', 'sma', 'ema', 'trend line', 'price average'],
            'rsi': ['relative strength index', 'momentum oscillator', 'overbought oversold'],
            'macd': ['moving average convergence divergence', 'trend momentum'],
            'bollinger bands': ['bb', 'volatility bands', 'price channels'],
            'support': ['support level', 'floor', 'demand zone'],
            'resistance': ['resistance level', 'ceiling', 'supply zone'],
            'trend': ['directional movement', 'price direction', 'market bias'],
            'momentum': ['rate of change', 'velocity', 'acceleration'],
            'volatility': ['price fluctuation', 'market uncertainty', 'risk measure'],
            
            # Trading Strategies
            'scalping': ['micro trading', 'quick trades', 'short term trading'],
            'swing trading': ['position trading', 'medium term', 'trend following'],
            'day trading': ['intraday trading', 'same day trading'],
            'arbitrage': ['price difference trading', 'risk free profit'],
            'hedging': ['risk management', 'portfolio protection', 'insurance'],
            'mean reversion': ['contrarian trading', 'bounce trading', 'reversion to mean'],
            
            # Market Instruments
            'futures': ['derivatives', 'forward contracts', 'commodity contracts'],
            'options': ['derivative contracts', 'rights to buy/sell'],
            'stocks': ['equities', 'shares', 'securities'],
            'bonds': ['fixed income', 'debt securities', 'treasury'],
            'forex': ['foreign exchange', 'currency trading', 'fx'],
            'crypto': ['cryptocurrency', 'digital currency', 'bitcoin'],
            
            # Risk Management
            'stop loss': ['stop order', 'protective stop', 'risk control'],
            'position sizing': ['portfolio allocation', 'risk per trade', 'money management'],
            'diversification': ['portfolio spread', 'risk distribution', 'asset allocation'],
            'leverage': ['margin trading', 'borrowed capital', 'amplified exposure'],
            
            # Market Conditions
            'bull market': ['uptrend', 'rising market', 'positive sentiment'],
            'bear market': ['downtrend', 'falling market', 'negative sentiment'],
            'sideways': ['ranging', 'consolidation', 'horizontal movement'],
            'volatile': ['unstable', 'erratic', 'high fluctuation'],
            'liquid': ['active trading', 'high volume', 'easy to trade'],
            
            # Time Frames
            'intraday': ['same day', 'within day', 'short term'],
            'daily': ['end of day', 'daily basis', '24 hour'],
            'weekly': ['7 day', 'weekly basis', 'medium term'],
            'monthly': ['30 day', 'monthly basis', 'long term'],
            
            # Analysis Types
            'fundamental': ['economic analysis', 'company analysis', 'value analysis'],
            'technical': ['chart analysis', 'pattern analysis', 'indicator analysis'],
            'quantitative': ['mathematical', 'statistical', 'algorithmic'],
            'sentiment': ['market psychology', 'investor mood', 'crowd behavior']
        }
        
        # Technical indicator synonyms
        self.technical_indicators = {
            'sma': ['simple moving average', 'ma', 'moving average'],
            'ema': ['exponential moving average', 'exponential ma'],
            'rsi': ['relative strength index', 'momentum oscillator'],
            'macd': ['moving average convergence divergence'],
            'stochastic': ['stochastic oscillator', 'stoch'],
            'bollinger': ['bollinger bands', 'bb', 'volatility bands'],
            'atr': ['average true range', 'volatility measure'],
            'adx': ['average directional index', 'trend strength'],
            'cci': ['commodity channel index', 'momentum indicator'],
            'williams': ['williams %r', 'momentum oscillator']
        }
        
        # Context-aware expansion patterns
        self.context_patterns = {
            'how_to': ['implementation', 'steps', 'process', 'methodology', 'approach'],
            'what_is': ['definition', 'explanation', 'concept', 'meaning', 'description'],
            'why': ['reason', 'purpose', 'benefit', 'advantage', 'rationale'],
            'when': ['timing', 'conditions', 'circumstances', 'situations'],
            'where': ['location', 'platform', 'market', 'exchange', 'venue'],
            'compare': ['comparison', 'versus', 'vs', 'difference', 'contrast'],
            'analyze': ['analysis', 'evaluation', 'assessment', 'examination'],
            'strategy': ['approach', 'method', 'technique', 'system', 'plan'],
            'risk': ['danger', 'hazard', 'exposure', 'vulnerability', 'uncertainty'],
            'profit': ['gain', 'return', 'earnings', 'revenue', 'income']
        }
        
        # Trading-specific context terms
        self.trading_context = {
            'market_hours': ['trading hours', 'session times', 'market open', 'market close'],
            'trading_platforms': ['broker', 'platform', 'software', 'terminal', 'interface'],
            'order_types': ['market order', 'limit order', 'stop order', 'bracket order'],
            'chart_patterns': ['head and shoulders', 'double top', 'triangle', 'flag', 'pennant'],
            'candlestick': ['candle', 'bar chart', 'price action', 'ohlc'],
            'volume': ['trading volume', 'liquidity', 'participation', 'activity'],
            'slippage': ['execution cost', 'spread', 'commission', 'fees'],
            'backtesting': ['historical testing', 'strategy validation', 'paper trading'],
            'live_trading': ['real money', 'actual trading', 'live account', 'production']
        }
        
        # Performance tracking
        self.expansion_stats = {
            'total_expansions': 0,
            'avg_expansion_ratio': 0.0,
            'synonym_hits': 0,
            'context_hits': 0,
            'trading_term_hits': 0
        }
    
    def expand_query(self, query: str, expansion_level: str = 'medium') -> ExpandedQuery:
        """Expand query with synonyms and context awareness."""
        self.expansion_stats['total_expansions'] += 1
        
        original_query = query.lower().strip()
        expanded_queries = [original_query]
        synonyms = {}
        context_terms = []
        trading_terms = []
        technical_terms = []
        
        # Determine expansion strategy based on level
        if expansion_level == 'minimal':
            strategies = ['basic_synonyms']
        elif expansion_level == 'medium':
            strategies = ['basic_synonyms', 'trading_synonyms', 'context_awareness']
        else:  # aggressive
            strategies = ['basic_synonyms', 'trading_synonyms', 'context_awareness', 'technical_indicators', 'phrase_expansion']
        
        # Apply expansion strategies
        for strategy in strategies:
            if strategy == 'basic_synonyms':
                synonyms.update(self._extract_basic_synonyms(original_query))
            elif strategy == 'trading_synonyms':
                trading_synonyms = self._extract_trading_synonyms(original_query)
                synonyms.update(trading_synonyms)
                trading_terms.extend(list(trading_synonyms.keys()))
            elif strategy == 'context_awareness':
                context_terms.extend(self._extract_context_terms(original_query))
            elif strategy == 'technical_indicators':
                tech_synonyms = self._extract_technical_indicators(original_query)
                synonyms.update(tech_synonyms)
                technical_terms.extend(list(tech_synonyms.keys()))
            elif strategy == 'phrase_expansion':
                self._expand_phrases(original_query, expanded_queries)
        
        # Generate expanded query variations
        expanded_queries.extend(self._generate_query_variations(original_query, synonyms, context_terms))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for q in expanded_queries:
            if q not in seen:
                seen.add(q)
                unique_queries.append(q)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(original_query, synonyms, context_terms)
        
        # Update stats
        self._update_expansion_stats(synonyms, context_terms, trading_terms)
        
        return ExpandedQuery(
            original_query=query,
            expanded_queries=unique_queries,
            synonyms=synonyms,
            context_terms=context_terms,
            trading_terms=trading_terms,
            technical_terms=technical_terms,
            confidence_score=confidence_score,
            expansion_strategy=expansion_level
        )
    
    def _extract_basic_synonyms(self, query: str) -> Dict[str, List[str]]:
        """Extract basic synonyms from the query."""
        synonyms = {}
        words = query.split()
        
        for word in words:
            if len(word) > 3:  # Skip short words
                # Simple synonym expansion (can be enhanced with WordNet or similar)
                if word in ['strategy', 'strategies']:
                    synonyms[word] = ['approach', 'method', 'technique', 'system']
                elif word in ['analysis', 'analyze']:
                    synonyms[word] = ['evaluation', 'assessment', 'examination', 'study']
                elif word in ['trading', 'trade']:
                    synonyms[word] = ['buying', 'selling', 'transactions', 'investing']
                elif word in ['market', 'markets']:
                    synonyms[word] = ['exchange', 'venue', 'platform', 'arena']
                elif word in ['price', 'prices']:
                    synonyms[word] = ['cost', 'value', 'rate', 'level']
        
        return synonyms
    
    def _extract_trading_synonyms(self, query: str) -> Dict[str, List[str]]:
        """Extract trading-specific synonyms."""
        synonyms = {}
        query_lower = query.lower()
        
        for term, synonym_list in self.trading_synonyms.items():
            if term in query_lower:
                synonyms[term] = synonym_list
                self.expansion_stats['trading_term_hits'] += 1
        
        return synonyms
    
    def _extract_context_terms(self, query: str) -> List[str]:
        """Extract context-aware terms based on query patterns."""
        context_terms = []
        query_lower = query.lower()
        
        # Check for question patterns
        for pattern, terms in self.context_patterns.items():
            if pattern in query_lower:
                context_terms.extend(terms)
                self.expansion_stats['context_hits'] += 1
        
        # Check for trading context
        for context, terms in self.trading_context.items():
            if any(term in query_lower for term in context.split('_')):
                context_terms.extend(terms)
        
        return list(set(context_terms))  # Remove duplicates
    
    def _extract_technical_indicators(self, query: str) -> Dict[str, List[str]]:
        """Extract technical indicator synonyms."""
        synonyms = {}
        query_lower = query.lower()
        
        for indicator, synonym_list in self.technical_indicators.items():
            if indicator in query_lower:
                synonyms[indicator] = synonym_list
        
        return synonyms
    
    def _expand_phrases(self, query: str, expanded_queries: List[str]) -> None:
        """Expand common trading phrases."""
        phrase_expansions = {
            'moving average crossover': ['ma crossover', 'sma crossover', 'ema crossover', 'trend change signal'],
            'support and resistance': ['s&r', 'key levels', 'price levels', 'trading levels'],
            'risk management': ['risk control', 'money management', 'position sizing', 'stop losses'],
            'technical analysis': ['chart analysis', 'pattern analysis', 'indicator analysis', 'ta'],
            'fundamental analysis': ['fa', 'economic analysis', 'company analysis', 'value analysis'],
            'backtesting strategy': ['strategy testing', 'historical testing', 'paper trading', 'validation'],
            'live trading': ['real trading', 'actual trading', 'live account', 'production trading'],
            'portfolio optimization': ['asset allocation', 'diversification', 'risk distribution', 'rebalancing']
        }
        
        query_lower = query.lower()
        for phrase, expansions in phrase_expansions.items():
            if phrase in query_lower:
                expanded_queries.extend(expansions)
    
    def _generate_query_variations(self, original_query: str, synonyms: Dict[str, List[str]], 
                                 context_terms: List[str]) -> List[str]:
        """Generate query variations using synonyms and context terms."""
        variations = []
        
        # Create variations with synonyms
        for term, synonym_list in synonyms.items():
            for synonym in synonym_list[:2]:  # Limit to top 2 synonyms per term
                variation = original_query.replace(term, synonym)
                if variation != original_query:
                    variations.append(variation)
        
        # Create variations with context terms
        if context_terms:
            # Add context terms as additional keywords
            context_query = f"{original_query} {' '.join(context_terms[:3])}"
            variations.append(context_query)
        
        # Create question variations
        if original_query.startswith(('what', 'how', 'why', 'when', 'where')):
            # Add alternative question words
            question_variations = [
                original_query.replace('what', 'how'),
                original_query.replace('how', 'what'),
                original_query.replace('why', 'what'),
            ]
            variations.extend([q for q in question_variations if q != original_query])
        
        return variations
    
    def _calculate_confidence_score(self, query: str, synonyms: Dict[str, List[str]], 
                                  context_terms: List[str]) -> float:
        """Calculate confidence score for the expansion."""
        score = 0.5  # Base score
        
        # Boost for trading-specific terms
        trading_terms_found = len([term for term in self.trading_synonyms.keys() if term in query.lower()])
        score += min(trading_terms_found * 0.1, 0.3)
        
        # Boost for synonyms found
        score += min(len(synonyms) * 0.05, 0.2)
        
        # Boost for context terms
        score += min(len(context_terms) * 0.02, 0.1)
        
        return min(score, 1.0)
    
    def _update_expansion_stats(self, synonyms: Dict[str, List[str]], 
                              context_terms: List[str], trading_terms: List[str]) -> None:
        """Update expansion statistics."""
        if synonyms:
            self.expansion_stats['synonym_hits'] += len(synonyms)
        if context_terms:
            self.expansion_stats['context_hits'] += len(context_terms)
        
        # Update average expansion ratio
        total_expansions = self.expansion_stats['total_expansions']
        if total_expansions > 0:
            total_synonyms = sum(len(syns) for syns in synonyms.values())
            self.expansion_stats['avg_expansion_ratio'] = total_synonyms / total_expansions
    
    def get_expansion_stats(self) -> Dict[str, Any]:
        """Get query expansion statistics."""
        return {
            'total_expansions': self.expansion_stats['total_expansions'],
            'avg_expansion_ratio': self.expansion_stats['avg_expansion_ratio'],
            'synonym_hits': self.expansion_stats['synonym_hits'],
            'context_hits': self.expansion_stats['context_hits'],
            'trading_term_hits': self.expansion_stats['trading_term_hits']
        }
    
    async def expand_query_async(self, query: str, expansion_level: str = 'medium') -> ExpandedQuery:
        """Async version of query expansion."""
        # For now, just call the sync version
        # In the future, this could include async API calls for synonym lookup
        return self.expand_query(query, expansion_level)

# Global instance
query_expander = QueryExpander()