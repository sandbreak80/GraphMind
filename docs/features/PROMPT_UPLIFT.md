# Prompt Uplift Feature Guide

**Feature**: Prompt Uplift + Query Expansion  
**Status**: ✅ Production Ready  
**Impact**: +10-20% retrieval relevance  

---

## 🎯 What is Prompt Uplift?

Prompt Uplift automatically transforms vague or poorly-formed queries into optimal retrieval queries. This improves RAG performance by:

- **Adding clarity** - Transforms "trading strategies" → "Provide 3-5 specific trading strategies with risk profiles. Include: strategy name, entry/exit criteria, risk management. Cite sources."
- **Adding structure** - Includes format directives, citation requirements, and specific objectives
- **Generating expansions** - Creates 3 diverse query variants for better recall

---

## ✨ Features

### 1. Automatic Query Classification

Detects query characteristics:
- **Task type**: Q&A, summarize, compare, code
- **Entities**: Tickers, indicators, dates
- **Complexity**: Simple, medium, complex
- **Required sources**: RAG, Obsidian, Web

### 2. Query Uplift

Transforms vague queries into clear, actionable prompts:
- Preserves user intent (no fact injection)
- Adds citation directives automatically
- Includes format requirements
- Adds structure and objectives

### 3. Query Expansion

Generates 3 diverse query variants:
1. **Paraphrase** - Same meaning, different words
2. **Aspect Query** - Focused sub-question
3. **HyDE** - Hypothetical answer for semantic matching

---

## 🔧 How It Works

### Automatic Processing

When you ask a question, the system automatically:

1. **Classifies** your query (task type, entities, complexity)
2. **Uplifts** vague queries into clear prompts
3. **Expands** queries into 3 variants
4. **Retrieves** documents using improved query + expansions
5. **Deduplicates** and reranks results

### Example Transformation

**Your Query:**
```
trading strategies
```

**System Processing:**
- Classification: Q&A, medium complexity
- Uplifted: "Provide 3-5 specific trading strategies with risk profiles. Include: strategy name, entry/exit criteria, risk management. Cite sources."
- Expansions:
  1. "What are effective trading approaches?"
  2. "Which indicators are used in momentum trading?"
  3. "Momentum trading strategies typically use RSI and MACD..."

**Result**: Better retrieval with more relevant documents

---

## 📊 Metadata

The system adds metadata to responses showing:

```json
{
  "search_metadata": {
    "prompt_uplift": {
      "original_query": "trading strategies",
      "improved_query": "Provide 3-5 specific trading strategies...",
      "expansions": ["...", "...", "..."],
      "uplift_confidence": 0.85,
      "used_expansion": true,
      "classification": "Q&A",
      "used_original": false
    }
  }
}
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# Enable/disable feature
PROMPT_UPLIFT_ENABLED=true

# Number of expansions (1-5)
PROMPT_EXPANSION_COUNT=3

# Confidence threshold (0.0-1.0)
PROMPT_CONFIDENCE_THRESHOLD=0.75

# Enable HyDE expansion
PROMPT_ENABLE_HYDE=true

# Skip expansion threshold
PROMPT_SKIP_THRESHOLD=3

# Model for uplift
PROMPT_UPLIFTER_MODEL=llama3.2:3b-instruct

# Latency budget (ms)
PROMPT_LATENCY_BUDGET_MS=600
```

---

## 🎯 When It Helps Most

### High Impact Queries

- ✅ **Vague queries**: "trading strategies", "momentum", "RSI"
- ✅ **Short queries**: "explain", "compare", "summarize"
- ✅ **Ambiguous queries**: "best practices", "how to"

### Lower Impact Queries

- ✅ **Already specific**: "Compare RSI versus MACD for ES futures trading, including optimal parameter settings"
- ✅ **Very complex**: Already detailed queries see minimal changes

---

## 📈 Performance

### Expected Improvements

- **+10-20% nDCG@10** (retrieval relevance)
- **<600ms added latency** (p95)
- **Zero fact injection** violations
- **>50% cache hit rate** for repeated queries

---

## 🔍 Troubleshooting

### Query Not Being Uplifted

1. Check feature flag: `PROMPT_UPLIFT_ENABLED=true`
2. Check logs for uplift activity
3. Verify confidence threshold (default: 0.75)

### Latency Too High

1. Check latency budget: `PROMPT_LATENCY_BUDGET_MS=600`
2. Reduce expansion count: `PROMPT_EXPANSION_COUNT=2`
3. Check cache hit rate (should be >50%)

### Uplift Not Effective

1. Check uplift confidence scores
2. Review original vs. improved queries in metadata
3. Adjust confidence threshold if needed

---

## 📚 Technical Details

### Pipeline Stages

1. **Classification** (<100ms) - Rule-based + LLM fallback
2. **Uplift** (<300ms) - LLM-based with template fallback
3. **Expansion** (<200ms) - 3 parallel expansions
4. **Total** (<600ms p95) - Including caching

### Fallback Logic

- **Low confidence** (<0.75) → Use original query
- **LLM unavailable** → Use template-based uplift
- **Cache hit** → Return cached result (<10ms)

---

## 🚀 Best Practices

### For Users

1. **Write naturally** - Don't overthink your queries
2. **Use clear language** - Better queries → better uplift
3. **Check metadata** - See how your query was improved

### For Developers

1. **Monitor metrics** - Track latency, confidence, cache hit rate
2. **Tune thresholds** - Adjust confidence threshold based on data
3. **Review logs** - Check uplift transformations for quality

---

## 📞 Support

For issues or questions:
- Check logs: `docker logs graphmind-rag | grep "prompt_uplift"`
- Review metrics: `/metrics` endpoint
- Check documentation: `docs/api/PROMPT_UPLIFT_API.md`

---

**Last Updated**: October 30, 2025  
**Version**: 3.0.0
