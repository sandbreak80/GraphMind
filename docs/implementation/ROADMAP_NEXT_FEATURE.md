# 🚀 Next Feature: Prompt Uplift + Query Expansion

**Priority**: ⭐️ #1 Highest Impact Feature  
**Timeline**: 1-2 weeks (10 working days)  
**Impact**: +10-20% retrieval relevance (nDCG@10: 0.65 → 0.75)  
**Effort**: Low-Medium (90/10 move - high ROI)  
**Status**: 📋 Ready to implement immediately

---

## 🎯 What Is It?

**Prompt Uplift + Query Expansion** is a pre-processing layer that makes your RAG system **understand vague questions better**.

### The Problem

Users ask vague questions:
- ❌ "trading strategies"
- ❌ "RSI"
- ❌ "momentum"

These get poor retrieval results because they're too broad/ambiguous.

### The Solution

Transform them into **optimal retrieval queries**:

```
User Input: "trading strategies"
              ↓
    [PROMPT CLASSIFIER]
         ↓
Task: Q&A, Complexity: simple, Format: markdown
              ↓
    [PROMPT UPLIFTER]
         ↓
Improved: "Provide 3-5 specific trading strategies with risk profiles.
           Include: strategy name, entry/exit criteria, risk management.
           Cite sources. Format as markdown list."
              ↓
    [QUERY EXPANDER]
         ↓
Expansion 1: "What are effective trading strategies with entry/exit rules?"
Expansion 2: "Which indicators are used in momentum trading strategies?"
Expansion 3: [HyDE] "Momentum strategies use RSI and MACD indicators..."
              ↓
    [HYBRID RETRIEVAL] (existing)
         ↓
4x better results with same documents! 🎯
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    USER QUERY                            │
│           "trading strategies"                           │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  STEP 1: CLASSIFY (100ms)                               │
│  ────────────────────────────────────────────           │
│  Rule-based: Extract tickers, dates, indicators         │
│  LLM fallback: Classify ambiguous queries               │
│  Output: {task_type, entities, format, confidence}      │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  STEP 2: UPLIFT (300ms)                                 │
│  ────────────────────────────────────────────           │
│  Add: objective, structure, citation requirement        │
│  Validate: No fact injection, preserve intent           │
│  Score: Confidence 0.0-1.0                              │
│  Fallback: Template-based if LLM fails                  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  STEP 3: EXPAND (200ms)                                 │
│  ────────────────────────────────────────────           │
│  Generate 3 variants:                                   │
│    1. Paraphrase (synonym matching)                     │
│    2. Aspect query (specific facet)                     │
│    3. HyDE (hypothetical answer for semantic search)    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  STEP 4: RETRIEVE (existing hybrid retrieval)           │
│  ────────────────────────────────────────────           │
│  Query improved + 3 expansions = 4 retrievals           │
│  Merge results, deduplicate                             │
│  Rerank with cross-encoder                              │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  RESULT: 10-20% better relevance! 🎯                    │
└─────────────────────────────────────────────────────────┘

Total Added Latency: ≤600ms (classify + uplift + expand in parallel)
```

---

## 📋 10-Day Implementation Plan

### 📅 **Week 1: Core Implementation**

#### Day 1: Prompt Classifier
- **AM**: Create `app/prompt_classifier.py`
- **PM**: Implement rule-based signal extraction
- **Deliverable**: Classification working for 80% of queries

#### Day 2: Classifier Testing + LLM Fallback
- **AM**: Add LLM-based classification for ambiguous cases
- **PM**: Create 8 unit tests, benchmark speed (<100ms)
- **Deliverable**: Complete classifier with tests

#### Day 3: Prompt Uplifter (Template-based)
- **AM**: Create `app/prompt_uplifter.py` with templates
- **PM**: Implement template-based uplift for all task types
- **Deliverable**: Basic uplift working

#### Day 4: Prompt Uplifter (LLM-based)
- **AM**: Add LLM-based uplift for better quality
- **PM**: Implement fact injection detection
- **Deliverable**: Smart uplift with validation

#### Day 5: Query Expander
- **AM**: Create `app/query_expander.py`
- **PM**: Implement all 3 expansion strategies (paraphrase, aspect, HyDE)
- **Deliverable**: Expansion generating 3 diverse queries

---

### 📅 **Week 2: Integration & Validation**

#### Day 6: Pipeline Integration
- **AM**: Create `app/prompt_uplift_pipeline.py` - complete pipeline
- **PM**: Integrate with `/ask` endpoint in `main.py`
- **Deliverable**: End-to-end pipeline working

#### Day 7: Caching & Optimization
- **AM**: Add Redis caching for classifications and uplifts
- **PM**: Optimize latency (parallel execution, skip logic)
- **Deliverable**: Pipeline <600ms p95

#### Day 8: Testing
- **AM**: Create 25 unit tests for all components
- **PM**: Create 10 integration tests
- **Deliverable**: All tests passing

#### Day 9: Golden Set Evaluation
- **AM**: Create golden question set (50-100 Q&A pairs)
- **PM**: Run evaluation, measure nDCG improvement
- **Deliverable**: +10-20% nDCG improvement validated

#### Day 10: Documentation & Deployment
- **AM**: Documentation, API updates, user guide
- **PM**: Deploy with feature flag, monitor metrics
- **Deliverable**: Feature in production with A/B testing

---

## 🎯 Technical Specifications

### Models to Use

| Purpose | Model | Speed | Quality | When to Use |
|---------|-------|-------|---------|-------------|
| **Classification** | llama3.2:3b | 50ms | Good | Ambiguous queries |
| **Uplift** | llama3.2:3b | 200ms | Good | Primary uplifter |
| **Expansion** | llama3.2:3b | 50ms/exp | Good | All expansions |
| **Fallback** | phi3:mini | 30ms | Fair | If llama unavailable |

**Why small models?**
- Fast inference (<100ms per call)
- Simple task (not complex reasoning)
- Running locally (no API costs)
- Can upgrade to 7b later if needed

### API Changes

**New Endpoint**: `/ask` (enhanced)

**Request** (no changes needed - backward compatible):
```json
{
  "request": {
    "query": "trading strategies",
    "mode": "qa",
    "top_k": 5
  }
}
```

**Response** (enhanced with metadata):
```json
{
  "answer": "...",
  "sources": [...],
  "metadata": {
    "original_query": "trading strategies",
    "improved_query": "Provide 3-5 specific trading strategies...",
    "expansions": ["...", "...", "..."],
    "uplift_confidence": 0.92,
    "used_expansion": true,
    "retrieval_stats": {
      "primary_results": 10,
      "expansion_results": 8,
      "merged_results": 12,
      "final_reranked": 5
    }
  }
}
```

---

## 📊 Expected Impact Analysis

### Baseline (Current B+ System)

```
Query: "momentum"
Retrieved Documents: 3 relevant, 7 semi-relevant
nDCG@10: 0.62
User Satisfaction: Medium
```

### With Prompt Uplift (Target A- System)

```
Original: "momentum"
Improved: "Explain momentum trading: indicators, entry/exit criteria, cite sources"
Expansions:
  1. "Which technical indicators identify momentum in trading?"
  2. "RSI, MACD, and momentum oscillators for trend identification"
  3. [HyDE] "Momentum trading uses RSI >70 for overbought..."

Retrieved Documents: 8 relevant, 2 semi-relevant
nDCG@10: 0.78 (+26%! 🎯)
User Satisfaction: High
```

### Impact by Query Type

| Query Type | Baseline nDCG | With Uplift | Improvement |
|------------|---------------|-------------|-------------|
| **Vague** (1-2 words) | 0.45 | 0.70 | +56% 🚀 |
| **Simple** (3-10 words) | 0.65 | 0.75 | +15% |
| **Good** (10+ words, specific) | 0.80 | 0.85 | +6% |
| **Average** | 0.65 | 0.75-0.78 | **+15-20%** ✅ |

---

## 💡 Example Transformations

### Example 1: Very Vague Query

**User Input**: `"RSI"`

**Classifier Output**:
```json
{
  "task_type": "Q&A",
  "complexity": "simple",
  "entities": {"indicators": ["RSI"]},
  "confidence": 0.90
}
```

**Uplifted Query**:
```
"Explain the RSI (Relative Strength Index) indicator: how it's calculated, 
how to interpret readings (overbought >70, oversold <30), and practical 
trading applications with examples. Cite sources."
```

**Expansions**:
1. "What is the Relative Strength Index and how is it used in trading?"
2. "How do traders interpret RSI overbought and oversold levels?"
3. [HyDE] "The RSI indicator measures momentum on a 0-100 scale, with readings above 70 indicating overbought conditions and below 30 indicating oversold conditions..."

**Result**: Finds comprehensive RSI documents instead of just any mention of "RSI"

---

### Example 2: Ambiguous Query

**User Input**: `"compare strategies"`

**Classifier Output**:
```json
{
  "task_type": "compare",
  "complexity": "medium",
  "entities": {},
  "needs_clarification": true,
  "confidence": 0.65
}
```

**Uplifted Query**:
```
"Compare different trading strategies. For each strategy, include: approach, 
entry/exit criteria, risk management, typical timeframe, and success indicators. 
Format as comparison table with citations."
```

**Expansions**:
1. "What are the differences between momentum, mean-reversion, and breakout trading strategies?"
2. "Compare risk-adjusted returns of different trading approaches"
3. [HyDE] "Momentum strategies enter on strong trends with trailing stops, while mean-reversion strategies enter on extreme moves expecting reversal..."

**Result**: Structured comparison across multiple strategy types

---

### Example 3: Already Good Query

**User Input**: `"What are the optimal RSI settings for day trading ES futures, and how do they compare to swing trading settings?"`

**Classifier Output**:
```json
{
  "task_type": "compare",
  "complexity": "complex",
  "entities": {"indicators": ["RSI"], "tickers": ["ES"], "timeframes": ["day trading", "swing trading"]},
  "confidence": 0.95
}
```

**Uplifted Query**: (minimal changes)
```
"What are the optimal RSI settings for day trading ES futures, and how do 
they compare to swing trading settings? Include specific parameter values, 
cite sources."
```
*(Only added "cite sources")*

**Expansions**: Might skip expansion since baseline query is already excellent

**Result**: Minimal overhead for good queries, maximum benefit for vague ones

---

## ⚙️ Configuration Examples

### Conservative Setup (Week 1)
```python
PROMPT_UPLIFT_CONFIG = {
    "enabled": True,
    "expansion_count": 2,              # Start with 2 expansions
    "confidence_threshold": 0.80,       # Higher threshold = safer
    "enable_hyde": True,
    "skip_expansion_threshold": 3,      # Skip if 3+ baseline hits
    "uplifter_model": "llama3.2:3b-instruct",
    "max_tokens_uplift": 150,
}
```

### Optimized Setup (Week 2+)
```python
PROMPT_UPLIFT_CONFIG = {
    "enabled": True,
    "expansion_count": 3,              # Full 3 expansions
    "confidence_threshold": 0.75,       # More aggressive
    "enable_hyde": True,
    "skip_expansion_threshold": 3,
    "uplifter_model": "qwen2.5:7b-instruct",  # Better quality
    "max_tokens_uplift": 200,
    "parallel_expansion": True,         # Faster execution
}
```

---

## 📊 Success Metrics

### Week 1 Targets (MVP)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **nDCG@10 Improvement** | ≥10% | Golden set evaluation |
| **Added Latency (p95)** | ≤800ms | Prometheus histogram |
| **Fact Injection Rate** | 0% | Automated validation |
| **Uptime** | 99.9% | No crashes/errors |

### Week 2 Targets (Optimized)

| Metric | Target | Measurement |
|--------|--------|-------------|
| **nDCG@10 Improvement** | ≥15% | Golden set evaluation |
| **Added Latency (p95)** | ≤600ms | Optimized pipeline |
| **Confidence Accuracy** | ≥90% | Calibration testing |
| **User Satisfaction** | ↑ | Fewer re-phrasings |

---

## 🧪 Testing Plan

### Unit Tests (25 tests)

```
tests/unit/test_prompt_classifier.py      - 8 tests
tests/unit/test_prompt_uplifter.py        - 10 tests
tests/unit/test_query_expander.py         - 7 tests
tests/unit/test_prompt_uplift_pipeline.py - 5 tests
```

**Coverage Target**: 95%+

### Integration Tests (10 tests)

```
tests/integration/test_prompt_uplift_integration.py

- test_improved_retrieval_relevance()
- test_expansion_improves_recall()
- test_latency_within_budget()
- test_hyde_semantic_matching()
- test_no_fact_injection_violations()
- test_confidence_fallback_logic()
- test_skip_expansion_on_good_baseline()
- test_cache_hit_performance()
- test_multiple_expansions_deduplication()
- test_end_to_end_user_query()
```

### Golden Set Evaluation

```
tests/evaluation/golden_set_prompt_uplift.py

Dataset: 50-100 trading questions with ground truth
- Simple vague queries (30)
- Medium complexity queries (40)
- Complex specific queries (30)

Metrics:
- nDCG@5, nDCG@10
- Precision@k, Recall@k
- Mean Reciprocal Rank (MRR)
- Latency distribution
```

---

## 📅 Detailed Day-by-Day Plan

### 📆 Day 1: Prompt Classifier

**Morning (4 hours)**
```
[ ] Create app/prompt_classifier.py
[ ] Implement __init__, classify() method
[ ] Add _extract_signals() for rule-based detection
[ ] Implement ticker extraction (_extract_tickers)
[ ] Implement indicator extraction (_extract_indicators)
[ ] Add task type inference (_infer_task_type)
[ ] Add complexity estimation (_estimate_complexity)
```

**Afternoon (4 hours)**
```
[ ] Test classifier with sample queries
[ ] Add _is_ambiguous() logic
[ ] Create unit tests (5 tests)
[ ] Benchmark performance (target: <100ms)
[ ] Document API and usage
```

**Deliverable**: ✅ Classifier working with 85%+ accuracy

---

### 📆 Day 2: LLM Fallback & More Tests

**Morning (4 hours)**
```
[ ] Implement _llm_classify() for ambiguous queries
[ ] Add prompt template for LLM classification
[ ] Test LLM fallback accuracy
[ ] Add entity extraction helpers
```

**Afternoon (4 hours)**
```
[ ] Create remaining unit tests (3 more tests)
[ ] Add integration tests for classification
[ ] Optimize LLM prompts
[ ] Test edge cases (empty query, very long query, special chars)
```

**Deliverable**: ✅ Robust classifier with fallback, 8 tests passing

---

### 📆 Day 3: Prompt Uplifter (Templates)

**Morning (4 hours)**
```
[ ] Create app/prompt_uplifter.py
[ ] Implement __init__, uplift() method
[ ] Create uplift templates for each task type
[ ] Add _template_uplift() method
[ ] Implement _validate_uplift()
```

**Afternoon (4 hours)**
```
[ ] Test template-based uplift
[ ] Create uplift quality scorer
[ ] Add 5 unit tests
[ ] Test with sample queries
```

**Deliverable**: ✅ Template-based uplift working

---

### 📆 Day 4: Prompt Uplifter (LLM-based)

**Morning (4 hours)**
```
[ ] Implement LLM-based uplift
[ ] Create _build_uplift_system_prompt()
[ ] Add fact injection detection
[ ] Implement confidence scoring
```

**Afternoon (4 hours)**
```
[ ] Test LLM uplift quality
[ ] Create 5 more unit tests (total: 10)
[ ] Benchmark latency (target: <300ms)
[ ] Test fallback mechanisms
```

**Deliverable**: ✅ Complete uplifter with validation

---

### 📆 Day 5: Query Expander

**Morning (4 hours)**
```
[ ] Create app/query_expander.py
[ ] Implement _generate_paraphrase()
[ ] Implement _generate_aspect_query()
[ ] Implement _generate_hyde()
```

**Afternoon (4 hours)**
```
[ ] Test all 3 expansion types
[ ] Ensure diversity (cosine similarity check)
[ ] Create 7 unit tests
[ ] Benchmark per-expansion latency (<70ms each)
```

**Deliverable**: ✅ Expansion generating diverse queries

---

### 📆 Day 6: Complete Pipeline

**Morning (4 hours)**
```
[ ] Create app/prompt_uplift_pipeline.py
[ ] Implement process() method
[ ] Add confidence checking and fallback
[ ] Add skip logic for simple/good queries
[ ] Implement caching
```

**Afternoon (4 hours)**
```
[ ] Test complete pipeline end-to-end
[ ] Create 5 pipeline tests
[ ] Measure total latency
[ ] Optimize if >600ms
```

**Deliverable**: ✅ Complete pipeline <600ms

---

### 📆 Day 7: Integration with RAG

**Morning (4 hours)**
```
[ ] Modify app/main.py /ask endpoint
[ ] Integrate pipeline before retrieval
[ ] Handle multiple query variants
[ ] Merge and deduplicate results
```

**Afternoon (4 hours)**
```
[ ] Test integrated system
[ ] Verify retrieval improvements
[ ] Add error handling
[ ] Create integration tests (5 tests)
```

**Deliverable**: ✅ Integrated with existing RAG system

---

### 📆 Day 8: Golden Set Evaluation

**Morning (4 hours)**
```
[ ] Create golden question dataset
  - 30 vague queries (1-2 words)
  - 40 medium queries (3-10 words)
  - 30 specific queries (10+ words)
[ ] Add ground truth documents for each
```

**Afternoon (4 hours)**
```
[ ] Run evaluation: baseline vs uplift
[ ] Calculate nDCG@5, nDCG@10
[ ] Measure latency distribution
[ ] Validate fact injection = 0
[ ] Generate evaluation report
```

**Deliverable**: ✅ +10-20% nDCG improvement measured

---

### 📆 Day 9: Optimization & Monitoring

**Morning (4 hours)**
```
[ ] Parallel expansion generation
[ ] Optimize LLM prompts for speed
[ ] Add smart skip logic
[ ] Tune confidence thresholds
```

**Afternoon (4 hours)**
```
[ ] Add Prometheus metrics
[ ] Create Grafana dashboard
[ ] Set up alerting (latency, errors)
[ ] Run performance benchmarks
```

**Deliverable**: ✅ Optimized pipeline + monitoring

---

### 📆 Day 10: Documentation & Deployment

**Morning (4 hours)**
```
[ ] Update API documentation
[ ] Create user guide
[ ] Write technical docs
[ ] Create runbook for ops
```

**Afternoon (4 hours)**
```
[ ] Deploy with feature flag (10% traffic)
[ ] Monitor metrics for 1 hour
[ ] Ramp to 50% if healthy
[ ] Ramp to 100% if successful
[ ] Celebrate! 🎉
```

**Deliverable**: ✅ Feature in production

---

## 🎓 Learning Resources

### Key Papers

1. **HyDE (Hypothetical Document Embeddings)**
   - Paper: "Precise Zero-Shot Dense Retrieval without Relevance Labels"
   - Authors: Gao et al., 2022
   - Key Insight: Generate hypothetical answers for better semantic matching

2. **Query Expansion Techniques**
   - Paper: "ColBERTv2: Effective and Efficient Retrieval via Lightweight Late Interaction"
   - Key Insight: Multi-query retrieval improves recall

3. **Prompt Engineering**
   - Paper: "Large Language Models are Zero-Shot Reasoners"
   - Key Insight: Better prompts = better results

### Reference Implementations

- LangChain: `MultiQueryRetriever`
- LlamaIndex: `QueryTransform`
- DSPy: `ChainOfThought` with query optimization

---

## 🎯 Success Criteria Checklist

### Functional Requirements ✅

- [ ] Classifier detects task type correctly (>85% accuracy)
- [ ] Uplifter preserves user intent (100%)
- [ ] Uplifter adds no new facts (0 violations)
- [ ] Expansions are diverse (similarity <0.7)
- [ ] Pipeline has confidence scoring
- [ ] Fallback to original on low confidence

### Performance Requirements ✅

- [ ] Classification: <100ms p95
- [ ] Uplift: <300ms p95
- [ ] Expansion: <200ms total (3 queries)
- [ ] Total pipeline: <600ms p95
- [ ] No impact on existing system when disabled

### Quality Requirements ✅

- [ ] +10% nDCG@10 on golden set (minimum)
- [ ] +15% nDCG@10 on golden set (target)
- [ ] Confidence calibration: 90% accurate
- [ ] Zero fact injection violations
- [ ] 95%+ test coverage

### Operational Requirements ✅

- [ ] Feature flag for easy rollback
- [ ] Prometheus metrics exported
- [ ] Grafana dashboard created
- [ ] Alerts configured
- [ ] Documentation complete
- [ ] Runbook for troubleshooting

---

## 🚦 Go/No-Go Criteria

### Before Production Deployment

**GO** if:
- ✅ All tests passing (40+ tests)
- ✅ nDCG improvement ≥10% measured
- ✅ Latency <600ms p95
- ✅ Zero fact injection in validation
- ✅ Monitoring dashboards working
- ✅ Feature flag implemented

**NO-GO** if:
- ❌ nDCG improvement <5%
- ❌ Latency >1000ms p95
- ❌ Any fact injection detected
- ❌ Tests failing
- ❌ No rollback plan

---

## 🎯 Summary

### What You're Building

A **query pre-processing pipeline** that:
1. Understands what the user is asking (classify)
2. Makes the query better (uplift)
3. Generates variants for better recall (expand)
4. Validates quality and falls back if needed

### Why It Matters

- **Biggest impact** for least effort (90/10 rule)
- **Foundation** for other features (self-check, routing)
- **User experience** win (vague questions work better)
- **Measurable** improvement (+10-20% nDCG)

### Timeline

- **Week 1**: Core implementation
- **Week 2**: Testing, optimization, deployment
- **Total**: 10 days to production

### Expected Result

**GraphMind RAG Grade**: B+ (85/100) → A- (88-90/100) 🎯

Ready to move from **Top 20%** to **Top 10%** of RAG systems globally!

---

**Status**: 📋 **READY TO START**  
**Next Step**: Create `app/prompt_classifier.py` (Day 1) 
**End Goal**: +15-20% better retrieval with minimal latency  
**Let's build world-class RAG!** 🚀

