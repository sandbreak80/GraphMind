"""Enhanced metadata extraction and filtering capabilities."""

import logging
import re
import time
from typing import List, Dict, Any, Optional, Set, Tuple
from dataclasses import dataclass
from collections import Counter, defaultdict
import json

logger = logging.getLogger(__name__)

@dataclass
class EnhancedMetadata:
    """Enhanced metadata with comprehensive extraction and filtering."""
    document_id: str
    title: str
    content_type: str
    trading_domain: str
    complexity_level: str
    key_concepts: List[str]
    trading_strategies: List[str]
    technical_indicators: List[str]
    risk_factors: List[str]
    time_frames: List[str]
    market_conditions: List[str]
    quality_indicators: Dict[str, Any]
    sentiment: str
    confidence_scores: Dict[str, float]
    extraction_timestamp: str
    version: str

class MetadataEnhancer:
    """Advanced metadata extraction and filtering system."""
    
    def __init__(self):
        # Trading domain classification
        self.trading_domains = {
            'technical_analysis': [
                'chart patterns', 'indicators', 'support resistance', 'trend analysis',
                'momentum', 'oscillators', 'moving averages', 'bollinger bands'
            ],
            'fundamental_analysis': [
                'earnings', 'revenue', 'financial statements', 'valuation',
                'economic indicators', 'company analysis', 'industry analysis'
            ],
            'risk_management': [
                'position sizing', 'stop loss', 'portfolio management', 'diversification',
                'risk assessment', 'drawdown', 'volatility management'
            ],
            'strategy_development': [
                'algorithmic trading', 'backtesting', 'optimization', 'signal generation',
                'entry exit rules', 'strategy implementation', 'performance metrics'
            ],
            'market_analysis': [
                'market conditions', 'volatility', 'liquidity', 'sector analysis',
                'market trends', 'economic outlook', 'market sentiment'
            ]
        }
        
        # Complexity level indicators
        self.complexity_indicators = {
            'beginner': [
                'basic', 'introduction', 'overview', 'fundamentals', 'simple',
                'getting started', 'first steps', 'basics of'
            ],
            'intermediate': [
                'advanced', 'detailed', 'comprehensive', 'in-depth', 'thorough',
                'implementation', 'practical', 'real-world'
            ],
            'expert': [
                'sophisticated', 'complex', 'algorithmic', 'quantitative', 'mathematical',
                'statistical', 'optimization', 'advanced techniques'
            ]
        }
        
        # Trading strategies patterns
        self.strategy_patterns = {
            'momentum': [
                'momentum trading', 'trend following', 'breakout trading', 'swing trading',
                'momentum strategy', 'trend strategy'
            ],
            'mean_reversion': [
                'mean reversion', 'contrarian', 'bounce trading', 'reversion strategy',
                'oversold overbought', 'range trading'
            ],
            'arbitrage': [
                'arbitrage', 'statistical arbitrage', 'pairs trading', 'spread trading',
                'risk-free profit', 'price differences'
            ],
            'scalping': [
                'scalping', 'micro trading', 'quick trades', 'short term', 'intraday',
                'high frequency', 'rapid trading'
            ],
            'swing_trading': [
                'swing trading', 'position trading', 'medium term', 'multi-day',
                'swing strategy', 'position strategy'
            ]
        }
        
        # Technical indicators patterns
        self.indicator_patterns = {
            'trend_indicators': [
                'moving average', 'ma', 'sma', 'ema', 'macd', 'adx', 'parabolic sar'
            ],
            'momentum_indicators': [
                'rsi', 'stochastic', 'cci', 'williams %r', 'roc', 'momentum'
            ],
            'volatility_indicators': [
                'bollinger bands', 'atr', 'volatility', 'standard deviation', 'vix'
            ],
            'volume_indicators': [
                'volume', 'obv', 'ad line', 'money flow', 'volume profile'
            ]
        }
        
        # Risk factors patterns
        self.risk_patterns = {
            'market_risk': [
                'market risk', 'systematic risk', 'beta', 'correlation', 'market exposure'
            ],
            'liquidity_risk': [
                'liquidity risk', 'slippage', 'bid ask spread', 'market depth', 'volume'
            ],
            'credit_risk': [
                'credit risk', 'default risk', 'counterparty risk', 'credit rating'
            ],
            'operational_risk': [
                'operational risk', 'system failure', 'human error', 'process risk'
            ]
        }
        
        # Time frame patterns
        self.timeframe_patterns = {
            'intraday': ['intraday', 'same day', 'within day', 'short term', 'minutes', 'hours'],
            'daily': ['daily', 'end of day', 'daily basis', '24 hour', 'overnight'],
            'weekly': ['weekly', '7 day', 'weekly basis', 'medium term', 'multi-day'],
            'monthly': ['monthly', '30 day', 'monthly basis', 'long term', 'quarterly']
        }
        
        # Market conditions patterns
        self.market_condition_patterns = {
            'trending': ['trending', 'uptrend', 'downtrend', 'directional', 'momentum'],
            'ranging': ['ranging', 'sideways', 'consolidation', 'horizontal', 'flat'],
            'volatile': ['volatile', 'high volatility', 'erratic', 'unstable', 'choppy'],
            'calm': ['calm', 'low volatility', 'stable', 'quiet', 'peaceful']
        }
        
        # Quality indicators
        self.quality_indicators = {
            'code_examples': r'```[\s\S]*?```|def\s+\w+|class\s+\w+',
            'formulas': r'[=+\-*/()0-9]+|formula|equation|calculation',
            'step_by_step': r'step\s+\d+|first|second|third|finally|next|then',
            'examples': r'example|for instance|such as|like|consider',
            'case_studies': r'case study|real world|actual|practical',
            'best_practices': r'best practice|recommended|should|must|always',
            'warnings': r'warning|caution|avoid|never|don\'t|risk'
        }
        
        # Sentiment analysis patterns
        self.sentiment_patterns = {
            'positive': [
                'profitable', 'successful', 'effective', 'beneficial', 'advantageous',
                'good', 'excellent', 'outstanding', 'positive', 'optimistic'
            ],
            'negative': [
                'loss', 'risk', 'danger', 'warning', 'caution', 'avoid', 'negative',
                'bad', 'poor', 'unsuccessful', 'harmful', 'detrimental'
            ],
            'neutral': [
                'analysis', 'evaluation', 'assessment', 'review', 'study', 'research',
                'examination', 'investigation', 'observation', 'description'
            ]
        }
        
        # Performance tracking
        self.extraction_stats = {
            'total_extractions': 0,
            'avg_extraction_time': 0.0,
            'domain_distribution': defaultdict(int),
            'complexity_distribution': defaultdict(int),
            'strategy_distribution': defaultdict(int),
            'quality_scores': []
        }
    
    async def extract_enhanced_metadata(self, document_id: str, title: str, 
                                      text: str, source: str = 'unknown') -> EnhancedMetadata:
        """Extract comprehensive metadata from document."""
        start_time = time.time()
        self.extraction_stats['total_extractions'] += 1
        
        # Basic metadata
        content_type = self._classify_content_type(text)
        trading_domain = self._classify_trading_domain(text)
        complexity_level = self._assess_complexity_level(text)
        
        # Extract key concepts
        key_concepts = self._extract_key_concepts(text)
        trading_strategies = self._extract_trading_strategies(text)
        technical_indicators = self._extract_technical_indicators(text)
        risk_factors = self._extract_risk_factors(text)
        time_frames = self._extract_time_frames(text)
        market_conditions = self._extract_market_conditions(text)
        
        # Quality assessment
        quality_indicators = self._assess_quality_indicators(text)
        
        # Sentiment analysis
        sentiment = self._analyze_sentiment(text)
        
        # Confidence scores
        confidence_scores = self._calculate_confidence_scores(
            text, trading_domain, complexity_level, key_concepts
        )
        
        # Update statistics
        extraction_time = time.time() - start_time
        self._update_extraction_stats(extraction_time, trading_domain, complexity_level, trading_strategies)
        
        return EnhancedMetadata(
            document_id=document_id,
            title=title,
            content_type=content_type,
            trading_domain=trading_domain,
            complexity_level=complexity_level,
            key_concepts=key_concepts,
            trading_strategies=trading_strategies,
            technical_indicators=technical_indicators,
            risk_factors=risk_factors,
            time_frames=time_frames,
            market_conditions=market_conditions,
            quality_indicators=quality_indicators,
            sentiment=sentiment,
            confidence_scores=confidence_scores,
            extraction_timestamp=time.strftime('%Y-%m-%d %H:%M:%S'),
            version='1.0'
        )
    
    def _classify_content_type(self, text: str) -> str:
        """Classify the type of content."""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['tutorial', 'guide', 'how to', 'step by step']):
            return 'tutorial'
        elif any(word in text_lower for word in ['strategy', 'method', 'approach', 'system']):
            return 'strategy'
        elif any(word in text_lower for word in ['analysis', 'research', 'study', 'report']):
            return 'analysis'
        elif any(word in text_lower for word in ['news', 'update', 'announcement', 'alert']):
            return 'news'
        elif any(word in text_lower for word in ['definition', 'explanation', 'concept', 'overview']):
            return 'educational'
        else:
            return 'general'
    
    def _classify_trading_domain(self, text: str) -> str:
        """Classify the trading domain."""
        text_lower = text.lower()
        domain_scores = {}
        
        for domain, keywords in self.trading_domains.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            domain_scores[domain] = score
        
        if domain_scores:
            return max(domain_scores, key=domain_scores.get)
        else:
            return 'general'
    
    def _assess_complexity_level(self, text: str) -> str:
        """Assess the complexity level of the content."""
        text_lower = text.lower()
        complexity_scores = {}
        
        for level, indicators in self.complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in text_lower)
            complexity_scores[level] = score
        
        # Additional complexity factors
        word_count = len(text.split())
        if word_count > 1000:
            complexity_scores['expert'] += 1
        elif word_count > 500:
            complexity_scores['intermediate'] += 1
        else:
            complexity_scores['beginner'] += 1
        
        if complexity_scores:
            return max(complexity_scores, key=complexity_scores.get)
        else:
            return 'intermediate'
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """Extract key trading concepts."""
        text_lower = text.lower()
        concepts = []
        
        # Extract trading concepts
        trading_concepts = [
            'portfolio', 'diversification', 'asset allocation', 'risk management',
            'position sizing', 'stop loss', 'take profit', 'leverage', 'margin',
            'volatility', 'liquidity', 'correlation', 'beta', 'alpha', 'sharpe ratio',
            'drawdown', 'maximum drawdown', 'var', 'value at risk', 'backtesting',
            'forward testing', 'paper trading', 'live trading', 'strategy optimization'
        ]
        
        for concept in trading_concepts:
            if concept in text_lower:
                concepts.append(concept)
        
        return list(set(concepts))  # Remove duplicates
    
    def _extract_trading_strategies(self, text: str) -> List[str]:
        """Extract trading strategies mentioned."""
        text_lower = text.lower()
        strategies = []
        
        for strategy_type, patterns in self.strategy_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    strategies.append(strategy_type)
                    break
        
        return list(set(strategies))
    
    def _extract_technical_indicators(self, text: str) -> List[str]:
        """Extract technical indicators mentioned."""
        text_lower = text.lower()
        indicators = []
        
        for indicator_type, patterns in self.indicator_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    indicators.append(pattern)
        
        return list(set(indicators))
    
    def _extract_risk_factors(self, text: str) -> List[str]:
        """Extract risk factors mentioned."""
        text_lower = text.lower()
        risk_factors = []
        
        for risk_type, patterns in self.risk_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    risk_factors.append(risk_type)
                    break
        
        return list(set(risk_factors))
    
    def _extract_time_frames(self, text: str) -> List[str]:
        """Extract time frames mentioned."""
        text_lower = text.lower()
        time_frames = []
        
        for timeframe, patterns in self.timeframe_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    time_frames.append(timeframe)
                    break
        
        return list(set(time_frames))
    
    def _extract_market_conditions(self, text: str) -> List[str]:
        """Extract market conditions mentioned."""
        text_lower = text.lower()
        conditions = []
        
        for condition, patterns in self.market_condition_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    conditions.append(condition)
                    break
        
        return list(set(conditions))
    
    def _assess_quality_indicators(self, text: str) -> Dict[str, Any]:
        """Assess quality indicators in the content."""
        quality_scores = {}
        
        for indicator, pattern in self.quality_indicators.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            quality_scores[indicator] = len(matches)
        
        # Overall quality score
        total_indicators = sum(quality_scores.values())
        quality_scores['overall_score'] = min(total_indicators / 10, 1.0)  # Normalize to 0-1
        
        return quality_scores
    
    def _analyze_sentiment(self, text: str) -> str:
        """Analyze sentiment of the content."""
        text_lower = text.lower()
        sentiment_scores = {}
        
        for sentiment, patterns in self.sentiment_patterns.items():
            score = sum(1 for pattern in patterns if pattern in text_lower)
            sentiment_scores[sentiment] = score
        
        if sentiment_scores:
            return max(sentiment_scores, key=sentiment_scores.get)
        else:
            return 'neutral'
    
    def _calculate_confidence_scores(self, text: str, trading_domain: str, 
                                   complexity_level: str, key_concepts: List[str]) -> Dict[str, float]:
        """Calculate confidence scores for extracted metadata."""
        scores = {}
        
        # Domain classification confidence
        domain_keywords = self.trading_domains.get(trading_domain, [])
        domain_matches = sum(1 for keyword in domain_keywords if keyword in text.lower())
        scores['domain_confidence'] = min(domain_matches / 5, 1.0)  # Normalize to 0-1
        
        # Complexity assessment confidence
        complexity_indicators = self.complexity_indicators.get(complexity_level, [])
        complexity_matches = sum(1 for indicator in complexity_indicators if indicator in text.lower())
        scores['complexity_confidence'] = min(complexity_matches / 3, 1.0)
        
        # Key concepts confidence
        scores['concepts_confidence'] = min(len(key_concepts) / 10, 1.0)
        
        # Overall confidence
        scores['overall_confidence'] = sum(scores.values()) / len(scores)
        
        return scores
    
    def _update_extraction_stats(self, extraction_time: float, trading_domain: str, 
                               complexity_level: str, trading_strategies: List[str]) -> None:
        """Update extraction statistics."""
        total_extractions = self.extraction_stats['total_extractions']
        
        # Update average extraction time
        if total_extractions > 0:
            self.extraction_stats['avg_extraction_time'] = (
                (self.extraction_stats['avg_extraction_time'] * (total_extractions - 1) + extraction_time) 
                / total_extractions
            )
        
        # Update distributions
        self.extraction_stats['domain_distribution'][trading_domain] += 1
        self.extraction_stats['complexity_distribution'][complexity_level] += 1
        
        for strategy in trading_strategies:
            self.extraction_stats['strategy_distribution'][strategy] += 1
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get metadata extraction statistics."""
        return {
            'total_extractions': self.extraction_stats['total_extractions'],
            'avg_extraction_time': self.extraction_stats['avg_extraction_time'],
            'domain_distribution': dict(self.extraction_stats['domain_distribution']),
            'complexity_distribution': dict(self.extraction_stats['complexity_distribution']),
            'strategy_distribution': dict(self.extraction_stats['strategy_distribution'])
        }
    
    def filter_by_metadata(self, documents: List[Dict[str, Any]], 
                          filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Filter documents based on metadata criteria."""
        filtered_docs = []
        
        for doc in documents:
            metadata = doc.get('metadata', {})
            
            # Apply filters
            include_doc = True
            
            if 'trading_domain' in filters:
                if metadata.get('trading_domain') != filters['trading_domain']:
                    include_doc = False
            
            if 'complexity_level' in filters:
                if metadata.get('complexity_level') != filters['complexity_level']:
                    include_doc = False
            
            if 'content_type' in filters:
                if metadata.get('content_type') != filters['content_type']:
                    include_doc = False
            
            if 'sentiment' in filters:
                if metadata.get('sentiment') != filters['sentiment']:
                    include_doc = False
            
            if 'min_quality_score' in filters:
                quality_score = metadata.get('quality_indicators', {}).get('overall_score', 0)
                if quality_score < filters['min_quality_score']:
                    include_doc = False
            
            if include_doc:
                filtered_docs.append(doc)
        
        return filtered_docs

# Global instance
metadata_enhancer = MetadataEnhancer()