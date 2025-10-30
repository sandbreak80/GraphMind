# Prompt Uplift API Documentation

**Endpoint**: `/ask` (enhanced with prompt uplift)  
**Method**: POST  
**Authentication**: Required (JWT token)

---

## Overview

The `/ask` endpoint now includes automatic prompt uplift and query expansion. Vague queries are transformed into optimal retrieval queries for better results.

---

## Request

```json
{
  "query": "trading strategies",
  "mode": "qa",
  "model": "llama3.2:3b-instruct",
  "top_k": 5,
  "temperature": 0.1,
  "max_tokens": 2000
}
```

### Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | User query (will be uplifted automatically) |
| `mode` | string | No | "qa" | Mode: "qa" or "spec" |
| `model` | string | No | auto | LLM model for generation |
| `top_k` | int | No | 5 | Number of results to return |
| `temperature` | float | No | 0.1 | Sampling temperature |
| `max_tokens` | int | No | 8000 | Maximum tokens |

---

## Response

```json
{
  "query": "Provide 3-5 specific trading strategies...",
  "answer": "Based on the documents...",
  "citations": [
    {
      "text": "Momentum trading strategies...",
      "doc_id": "doc_123",
      "page": 5,
      "section": "PDF: Trading_Guide.pdf",
      "score": 0.92
    }
  ],
  "sources": [...],
  "mode": "qa",
  "search_metadata": {
    "prompt_uplift": {
      "original_query": "trading strategies",
      "improved_query": "Provide 3-5 specific trading strategies...",
      "expansions": [
        "What are effective trading approaches?",
        "Which indicators are used in momentum trading?",
        "Momentum trading strategies typically use..."
      ],
      "uplift_confidence": 0.85,
      "used_expansion": true,
      "classification": "Q&A",
      "used_original": false
    }
  }
}
```

### Response Fields

#### Main Response

- `query`: Final query used (may be uplifted)
- `answer`: Generated answer
- `citations`: List of source citations
- `sources`: List of sources (same as citations)
- `mode`: Query mode ("qa" or "spec")

#### Prompt Uplift Metadata

Located in `search_metadata.prompt_uplift`:

- `original_query`: Your original query
- `improved_query`: Uplifted query used for retrieval
- `expansions`: List of expansion queries (0-3)
- `uplift_confidence`: Confidence score (0.0-1.0)
- `used_expansion`: Whether expansions were used
- `classification`: Task type (Q&A, summarize, compare, code)
- `used_original`: Whether original query was used (fallback)

---

## Examples

### Example 1: Vague Query

**Request:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "momentum",
    "mode": "qa"
  }'
```

**Response:**
```json
{
  "query": "Explain momentum trading strategies...",
  "answer": "Momentum trading involves...",
  "search_metadata": {
    "prompt_uplift": {
      "original_query": "momentum",
      "improved_query": "Explain momentum trading strategies...",
      "uplift_confidence": 0.88,
      "used_expansion": true
    }
  }
}
```

### Example 2: Specific Query (Minimal Uplift)

**Request:**
```bash
curl -X POST http://localhost:8000/ask \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "query": "Compare RSI versus MACD for ES futures trading, including optimal parameter settings",
    "mode": "qa"
  }'
```

**Response:**
```json
{
  "query": "Compare RSI versus MACD for ES futures trading. Include: optimal parameter settings, signal accuracy, performance comparison. Cite sources.",
  "search_metadata": {
    "prompt_uplift": {
      "original_query": "Compare RSI versus MACD...",
      "improved_query": "Compare RSI versus MACD...",
      "uplift_confidence": 0.92,
      "used_expansion": false
    }
  }
}
```

---

## Configuration

### Environment Variables

```bash
# Enable/disable
PROMPT_UPLIFT_ENABLED=true

# Expansion count
PROMPT_EXPANSION_COUNT=3

# Confidence threshold
PROMPT_CONFIDENCE_THRESHOLD=0.75

# Model
PROMPT_UPLIFTER_MODEL=llama3.2:3b-instruct

# Latency budget
PROMPT_LATENCY_BUDGET_MS=600
```

---

## Performance

### Latency

- **Classification**: <100ms (p95)
- **Uplift**: <300ms (p95)
- **Expansion**: <200ms total
- **Total pipeline**: <600ms (p95)
- **Cache hit**: <10ms

### Quality

- **nDCG@10 improvement**: +10-20%
- **Fact injection violations**: 0
- **Confidence calibration**: ≥90%

---

## Error Handling

### Graceful Degradation

If prompt uplift fails:
- Falls back to original query
- No error returned to user
- Logs warning for debugging

### Common Issues

1. **LLM unavailable**: Falls back to template-based uplift
2. **Low confidence**: Uses original query
3. **Cache miss**: Proceeds with uplift

---

## Monitoring

### Metrics Endpoint

```bash
GET /metrics
```

Returns Prometheus metrics:
- `rag_prompt_uplift_latency_seconds` - Latency by stage
- `rag_prompt_uplift_confidence` - Confidence scores
- `rag_prompt_expansion_count` - Expansion counts
- `rag_uplift_cache_hits_total` - Cache hits
- `rag_uplift_cache_misses_total` - Cache misses
- `rag_uplift_fallback_original_total` - Fallbacks

---

## Best Practices

### Query Writing

1. **Write naturally** - Don't overthink
2. **Be specific when possible** - Better queries → better uplift
3. **Use clear language** - Avoid ambiguity

### Integration

1. **Check metadata** - Use `search_metadata.prompt_uplift` for insights
2. **Monitor metrics** - Track latency and confidence
3. **Adjust thresholds** - Tune based on your use case

---

## Troubleshooting

### Query Not Being Uplifted

1. Check `PROMPT_UPLIFT_ENABLED=true`
2. Check logs: `grep "prompt_uplift" logs/app.log`
3. Verify confidence threshold

### Latency Too High

1. Check cache hit rate
2. Reduce expansion count
3. Check latency budget setting

---

**Last Updated**: October 30, 2025  
**API Version**: 3.0.0
