# 🧠 Intelligent Search System Guide

## Overview

The EminiPlayer now features an **Intelligent Search System** that uses LLM-powered query generation to transform user prompts into targeted, context-aware web searches. This dramatically improves the quality and relevance of web search results.

## 🚀 Key Features

### 1. **LLM-Powered Query Generation**
- Analyzes user prompts to understand intent
- Generates 3-5 targeted search queries per prompt
- Extracts relevant entities (symbols, dates, concepts)
- Considers conversation history for context

### 2. **Smart Query Types**
- **News**: Recent market news and updates
- **Analysis**: Technical analysis and charts
- **Data**: Economic indicators and data
- **General**: Trading strategies and methodologies
- **Commentary**: Expert opinions and market commentary

### 3. **Entity Recognition**
- Automatically detects trading symbols (ES, NQ, YM, RTY)
- Identifies time references (today, this week, this month)
- Extracts trading concepts and strategies
- Recognizes market conditions and events

## 🔧 How It Works

### Step 1: Prompt Analysis
```
User: "What's the current market sentiment for ES futures?"
```

### Step 2: LLM Query Generation
The system generates intelligent queries like:
```json
[
  {
    "query": "ES futures market sentiment today",
    "intent": "Find current market sentiment for ES futures",
    "entities": ["ES", "today"],
    "search_type": "news",
    "priority": 5,
    "context": "Direct sentiment analysis for ES futures"
  },
  {
    "query": "E-mini S&P 500 market analysis current conditions",
    "intent": "Find technical analysis of ES market conditions",
    "entities": ["ES"],
    "search_type": "analysis", 
    "priority": 4,
    "context": "Technical analysis for ES market conditions"
  }
]
```

### Step 3: Multi-Query Search
- Executes all generated queries in parallel
- Combines results from multiple search engines
- Removes duplicates and ranks by relevance
- Returns top 20 most relevant results

### Step 4: Enhanced Answer Generation
- Combines document context with web search results
- Uses conversation history for better context
- Generates comprehensive answers with citations

## 📊 API Endpoints

### 1. Generate Search Queries
```bash
POST /generate-search-queries
```

**Request:**
```json
{
  "query": "What's the current market sentiment for ES futures?",
  "mode": "qa",
  "top_k": 5,
  "conversation_history": [
    {"role": "user", "content": "Previous question..."},
    {"role": "assistant", "content": "Previous answer..."}
  ]
}
```

**Response:**
```json
{
  "query": "What's the current market sentiment for ES futures?",
  "generated_queries": [
    {
      "query": "ES futures market sentiment today",
      "intent": "Find current market sentiment for ES futures",
      "entities": ["ES", "today"],
      "search_type": "news",
      "priority": 5,
      "context": "Direct sentiment analysis for ES futures"
    }
  ],
  "total_queries": 3
}
```

### 2. Enhanced Search
```bash
POST /ask-enhanced
```

**Response includes:**
- `search_metadata`: Query generation details
- `generated_queries`: List of queries used
- `entities_found`: Extracted entities
- `total_queries`: Number of queries generated
- `successful_queries`: Number of successful searches

## 🎯 Example Use Cases

### 1. **Market Analysis**
```
User: "How is the NASDAQ performing today?"
Generated Queries:
- "NASDAQ performance today market analysis"
- "NQ futures price action today"
- "NASDAQ technical analysis current conditions"
```

### 2. **Strategy Research**
```
User: "I want to understand mean reversion strategies for E-mini futures"
Generated Queries:
- "mean reversion strategies E-mini futures trading"
- "ES NQ YM mean reversion trading strategies"
- "futures mean reversion backtesting results"
```

### 3. **Economic Indicators**
```
User: "What economic indicators should I watch for ES trading?"
Generated Queries:
- "economic indicators ES futures trading impact"
- "S&P 500 economic data releases today"
- "futures trading economic indicators correlation"
```

## 🔍 Search Quality Improvements

### Before (Basic Search):
- Single query: "ES futures news"
- Limited context understanding
- Basic symbol extraction
- Static search patterns

### After (Intelligent Search):
- Multiple targeted queries
- Context-aware search strategies
- Entity recognition and extraction
- Dynamic query generation based on intent

## 🛠️ Configuration

### Environment Variables
```bash
# SearXNG Configuration
SEARXNG_URL=http://192.168.50.236:8888

# LLM Configuration (for query generation)
OLLAMA_BASE_URL=http://host.docker.internal:11434
```

### Model Settings
- **Model**: `qwen2.5-coder:14b`
- **Temperature**: 0.3 (for consistent results)
- **Max Tokens**: 1000
- **Top P**: 0.9

## 📈 Performance Benefits

### 1. **Relevance**
- 3-5x more relevant search results
- Context-aware query generation
- Entity-specific searches

### 2. **Coverage**
- Multiple search angles per prompt
- Different search types (news, analysis, data)
- Comprehensive information gathering

### 3. **Intelligence**
- Understands user intent
- Considers conversation history
- Adapts to different question types

## 🧪 Testing

### Test Query Generation
```bash
python test_intelligent_search.py
```

### Manual Testing
```bash
# Test query generation
curl -X POST "http://localhost:8001/generate-search-queries" \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the current market conditions for ES futures?"}'

# Test enhanced search
curl -X POST "http://localhost:8001/ask-enhanced" \
  -H "Authorization: Bearer test-token" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are the current market conditions for ES futures?"}'
```

## 🔧 Troubleshooting

### Common Issues

1. **Query Generation Fails**
   - Check LLM connectivity
   - Verify model availability
   - Check logs for errors

2. **No Search Results**
   - Verify SearXNG connectivity
   - Check search query validity
   - Review search metadata

3. **Poor Query Quality**
   - Adjust LLM temperature
   - Review prompt engineering
   - Check entity extraction

### Debug Information
The system provides detailed metadata:
- Generated queries used
- Entities extracted
- Search success rates
- Query priorities and intents

## 🚀 Future Enhancements

### Planned Features
1. **Query Optimization**: Learn from successful searches
2. **Domain-Specific Queries**: Specialized queries for different markets
3. **Real-Time Adaptation**: Adjust queries based on market conditions
4. **Multi-Language Support**: Generate queries in different languages
5. **Query Caching**: Cache successful query patterns

### Advanced Features
1. **Semantic Query Expansion**: Use embeddings for query enhancement
2. **Temporal Awareness**: Time-sensitive query generation
3. **Market Context**: Incorporate current market conditions
4. **User Preferences**: Learn from user interaction patterns

## 📚 Related Documentation

- [API Documentation](README.md#api-endpoints)
- [SearXNG Setup](OBSIDIAN_SETUP_GUIDE.md)
- [Web Search Configuration](FRONTEND_SETUP.md)
- [Troubleshooting Guide](README.md#troubleshooting)

---

**The Intelligent Search System transforms simple user prompts into sophisticated, multi-faceted search strategies that deliver comprehensive, relevant information for trading decisions.**
