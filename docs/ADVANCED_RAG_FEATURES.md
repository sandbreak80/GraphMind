# Advanced RAG Features - Implementation Plan

**Last Updated:** October 25, 2025  
**Status:** Planned - Path to World-Class (A+) Performance  
**Target:** Top 1% of production RAG systems

---

## Overview

This document outlines five cutting-edge RAG features that will elevate GraphMind from B+ (Top 20%) to A+ (Top 1%) performance. These features represent state-of-the-art RAG architecture and will provide significant competitive advantages.

**Expected Impact:**
- +40-60% retrieval accuracy (nDCG@10)
- +25-35% faithfulness rate
- Better user experience (smart routing, verified answers)
- Production-grade observability

---

## 1. Prompt Uplift + Query Expansion

**Goal:** Transform user queries into optimal retrieval queries using a small, fast pre-processor

### Features

#### 1.1 Prompt Linting & Classification
```python
class PromptClassifier:
    """Detect task type, required sources, entities, and output format."""
    
    def classify(self, prompt: str) -> Classification:
        return {
            "task_type": "Q&A" | "summarize" | "compare" | "code",
            "required_sources": ["Obsidian", "RAG", "Web"],
            "entities": ["AAPL", "today", "Q3 2024"],
            "output_format": "JSON" | "table" | "markdown",
            "tickers": ["AAPL", "MSFT"],
            "dates": ["2024-10-25"],
            "confidence": 0.95
        }
```

#### 1.2 Uplift/Normalization
- Rewrite low-detail prompts into clear, constrained form
- Add objective, audience, length, and citation requirements
- Preserve user intent (no new facts)
- Auto-inject "cite sources" directive for knowledge tasks

**Example:**
```
User: "trading strategies"
Uplifted: "Provide 3-5 specific trading strategies with risk profiles. 
           Include: strategy name, entry/exit criteria, risk management. 
           Cite specific documents/sources. Format as markdown list."
```

#### 1.3 Multi-Query Expansion (Cap: 3 queries)
```python
def expand_query(original: str) -> List[str]:
    """Generate diverse expansions for maximum recall."""
    return [
        paraphrase(original),           # Variant 1: Paraphrase
        generate_sub_query(original),   # Variant 2: Aspect/facet
        generate_hyde(original)         # Variant 3: HyDE (hypothetical answer)
    ]
```

**Example:**
```
Original: "What are momentum trading indicators?"
Expansions:
  1. "Which technical indicators help identify momentum in trading?"
  2. "RSI, MACD, and Stochastic indicators for momentum analysis"
  3. [HyDE] "Momentum indicators like RSI (>70 overbought) and MACD 
      crossovers signal trend strength..."
```

#### 1.4 Confidence + Fallback
```python
{
    "improved_prompt": "...",
    "original_prompt": "...",
    "expansions": [...],
    "confidence": 0.92,
    "use_original": False  # Fall back if confidence < threshold
}
```

### Requirements

**Inputs:**
- Raw user prompt
- Conversation metadata (mode, user prefs)
- Optional prior context

**Outputs:**
```json
{
    "improved_prompt": "Optimized query...",
    "expansions": ["query1", "query2", "query3"],
    "entities": ["AAPL", "today"],
    "constraints": {
        "output_format": "markdown",
        "cite_sources": true,
        "max_length": 500
    },
    "confidence": 0.95
}
```

**Performance:**
- Latency budget: ≤ 400-600ms p95 added end-to-end
- Skip expansion if baseline retrieval returns ≥3 high-confidence hits

**Policies:**
- ❌ May NOT add new facts
- ✅ MUST preserve user intent
- ✅ MUST include "cite sources" directive for knowledge tasks

### Configuration

```python
# Config knobs
EXPANSION_COUNT = 3  # Max expansions (1-3)
ENABLE_HYDE = True
MAX_TOKENS_UPLIFT = 200
CONFIDENCE_THRESHOLD = 0.75  # Fallback to original if lower
SKIP_EXPANSION_THRESHOLD = 3  # Skip if baseline finds 3+ good hits
```

### Best Practices

1. **Keep expansions diverse** - Use synonyms, structural variations
2. **Maintain domain synonym map** - Trading acronyms (e.g., "ES" → "E-mini S&P 500")
3. **Inject into BM25** - Feed synonyms to keyword search
4. **Batch process** - Process multiple expansions in parallel

### Tools & Integrations

- **Small LLMs (Ollama):**
  - `llama3.2:3b-instruct` (fastest)
  - `qwen2.5:3b-instruct` (balanced)
  - `qwen2.5:7b-instruct` (best quality)
  
- **Entity/Date Parsing:**
  - spaCy for entities
  - Regex for dates
  - Custom financial ticker detector
  
- **Policy Enforcement:**
  - Pydantic JSON schema validation
  - Template-based uplift

### Acceptance Criteria

- ✅ ≥10% nDCG@10 improvement on golden set
- ✅ ≤600ms added p95 latency
- ✅ 0 fact injection violations (policy enforcement)
- ✅ Confidence calibration: ≥90% accurate at threshold

---

## 2. Self-Check Verification (Sentence-Level Faithfulness)

**Goal:** Verify every claim in LLM responses against retrieved sources

### Features

#### 2.1 Two-Pass Answering

**Pass 1: Synthesis with Citations**
```python
def synthesize_with_citations(query: str, chunks: List[Chunk]) -> Response:
    """Generate answer with per-sentence citations."""
    prompt = f"""
    Answer this query using ONLY the provided sources.
    Cite the source after EVERY sentence using [1], [2], etc.
    
    Query: {query}
    Sources:
    [1] {chunks[0].text}
    [2] {chunks[1].text}
    ...
    """
    return {
        "answer": "Momentum indicators help identify trend strength. [1] 
                   RSI above 70 indicates overbought conditions. [2]",
        "citations": {1: chunk_id_1, 2: chunk_id_2}
    }
```

**Pass 2: Verification**
```python
def verify_answer(answer: str, chunks: Dict) -> Verification:
    """Check each sentence against cited chunks."""
    sentences = split_sentences(answer)
    
    for sentence in sentences:
        citation_id = extract_citation(sentence)
        cited_chunk = chunks[citation_id]
        
        verdict = verifier_llm.check(
            claim=sentence,
            source=cited_chunk.text
        )
        
        yield {
            "sentence": sentence,
            "supported": verdict.supported,  # True/False
            "missing_spans": verdict.missing_spans,
            "offending_claim": verdict.claim if not verdict.supported else None
        }
```

#### 2.2 Auto-Repair

```python
def auto_repair(unsupported_sentences: List[Sentence]) -> Response:
    """Re-retrieve and re-synthesize failing sentences."""
    for sentence in unsupported_sentences:
        # Widen retrieval
        more_chunks = retrieve(
            query=sentence.claim,
            k=original_k + RETRIEVE_WIDEN_STEP  # e.g., k=5 → k=10
        )
        
        # Enable graph expansion if available
        if GRAPH_ENABLED:
            more_chunks += expand_via_graph(more_chunks)
        
        # Re-synthesize only this sentence
        repaired = synthesize_sentence(sentence.claim, more_chunks)
        
        # Verify again
        if verify(repaired, more_chunks).supported:
            yield repaired
        else:
            yield f"⚠️ {sentence.original} [Unverified claim]"
```

#### 2.3 User Trust UX

```python
# Mark unsupported claims
"RSI above 70 indicates overbought. [✓]
⚠️ This always predicts market reversals. [Sources insufficient]
MACD crossovers confirm momentum. [✓]"

# Expose "Open Sources" quickview
[View sources for this claim →]
```

### Requirements

**Inputs:**
- Model answer (split into sentences)
- Citation chunk IDs
- Retrieved chunk texts

**Outputs:**
```json
{
    "verified_answer": "Momentum indicators help... [✓]",
    "sentence_verdicts": [
        {"sentence": "...", "supported": true, "confidence": 0.95},
        {"sentence": "...", "supported": false, "missing": "specific timeframe"}
    ],
    "faithfulness_score": 0.92
}
```

**Performance:**
- Latency budget: ≤ +20% median over baseline
- Verifier runs on small local model (fast)
- Batch verify sentences to minimize overhead

### Configuration

```python
VERIFY_ENABLED = True
RETRIEVE_WIDEN_STEP = 5  # Add 5 more chunks on retry
MAX_RETRY = 1  # Max re-synthesis attempts
FAIL_MARKER = "⚠️"  # Mark unverified claims
MIN_FAITHFULNESS = 0.95  # Block deploys if below this
```

### Best Practices

1. **Keep verifier deterministic** - Use temperature=0.1
2. **Batch verify sentences** - Process 5-10 sentences in parallel
3. **Block deploys on regressions** - Use golden set for CI/CD gate
4. **Log all failures** - Build dataset for verifier fine-tuning

### Tools & Integrations

- **Verifier LLM:**
  - `qwen2.5:7b-instruct` (balanced)
  - `llama3.2:3b` (fastest)
  
- **Citations:**
  - Preserve: `doc_id`, `heading_path`, `page`, `table`
  - Format: `document.pdf#Section-2.3 [Page 15]`
  
- **Metrics:**
  - Export: `faithfulness_rate`, `retry_percent`, `added_latency_ms`
  - Prometheus counters for monitoring

### Acceptance Criteria

- ✅ ≥95% faithfulness rate on golden set
- ✅ ≤20% median latency increase
- ✅ Unsupported claims either repaired OR marked with ⚠️
- ✅ CI/CD gate: Block deploys if faithfulness < threshold

---

## 3. Obsidian GraphRAG (Link-Aware Retrieval)

**Goal:** Leverage Obsidian's graph structure for better retrieval

### Features

#### 3.1 Obsidian Parser

```python
class ObsidianParser:
    """Parse Obsidian-specific syntax and metadata."""
    
    def parse_note(self, path: Path) -> Note:
        """Extract content, links, and metadata."""
        content = path.read_text()
        
        return {
            "id": note_id,
            "path": str(path),
            "title": extract_title(content),
            "aliases": extract_yaml_field(content, "aliases"),
            "tags": extract_tags(content),  # #tag or YAML
            "created": extract_yaml_field(content, "created"),
            "updated": extract_yaml_field(content, "updated"),
            "wikilinks": extract_wikilinks(content),  # [[Note]]
            "aliases_links": extract_aliased_links(content),  # [[Note|Alias]]
            "embeds": extract_embeds(content),  # ![[Image]] or ![[Note]]
            "headings": extract_headings(content)  # ## Heading
        }
```

**Supported Syntax:**
- `[[Note]]` - Wikilinks
- `[[Note|Alias]]` - Aliased links
- `![[Embed]]` - Embeds
- YAML front-matter (aliases, tags, dates)

#### 3.2 Graph Store

**Schema (Postgres):**
```sql
-- Notes
CREATE TABLE notes (
    id UUID PRIMARY KEY,
    path TEXT NOT NULL,
    title TEXT NOT NULL,
    aliases TEXT[],
    tags TEXT[],
    created TIMESTAMP,
    updated TIMESTAMP
);

-- Edges
CREATE TABLE edges (
    src UUID REFERENCES notes(id),
    dst UUID REFERENCES notes(id),
    type TEXT CHECK (type IN ('link', 'embed', 'tag')),
    weight FLOAT DEFAULT 1.0,
    heading_src TEXT,  -- Source heading context
    heading_dst TEXT,  -- Destination heading
    PRIMARY KEY (src, dst, type)
);

-- Indexes
CREATE INDEX idx_edges_src ON edges(src);
CREATE INDEX idx_edges_dst ON edges(dst);
CREATE INDEX idx_notes_tags ON notes USING GIN(tags);
```

**OR Neo4j (for advanced queries):**
```cypher
// Nodes
CREATE (n:Note {
    id: "...",
    title: "...",
    aliases: [...],
    tags: [...]
})

// Relationships
CREATE (n1)-[:LINKS_TO {heading_src: "..."}]->(n2)
CREATE (n1)-[:EMBEDS {heading_src: "..."}]->(n2)
CREATE (n1)-[:TAGGED {tag: "..."}]->(n2)
```

#### 3.3 Heading-Aware Chunking

```python
def chunk_obsidian_note(note: Note) -> List[Chunk]:
    """Chunk note while preserving heading hierarchy."""
    chunks = []
    
    for section in note.sections:
        # Chunk size: 300-800 tokens, 10-15% overlap
        section_chunks = semantic_chunk(
            text=section.content,
            chunk_size=512,
            overlap=50,
            heading_path=section.heading_path  # e.g., "## Trading > ### Momentum"
        )
        
        for chunk in section_chunks:
            chunks.append({
                "text": chunk.text,
                "note_id": note.id,
                "note_title": note.title,
                "heading_path": section.heading_path,
                "tags": note.tags,
                "aliases": note.aliases,
                "backlinks_count": len(note.backlinks)
            })
    
    return chunks
```

#### 3.4 Query-Time Graph Expansion

```python
def graph_expand_retrieval(query: str, initial_chunks: List[Chunk]) -> List[Chunk]:
    """Expand retrieval using graph structure."""
    
    # Step 1: Get initial candidates (BM25 + dense)
    candidates = hybrid_retrieve(query, k=10)
    
    # Step 2: Extract note IDs from candidates
    note_ids = {chunk.note_id for chunk in candidates}
    
    # Step 3: Expand 1-2 hops with decay
    expanded = []
    for note_id in note_ids:
        neighbors = get_neighbors(
            note_id=note_id,
            hops=GRAPH_HOPS,  # 1 or 2
            max_neighbors=GRAPH_K  # e.g., 5 per note
        )
        
        for neighbor in neighbors:
            # Apply decay based on hop distance
            neighbor.score *= (GRAPH_DECAY ** neighbor.hop_distance)
            expanded.append(neighbor)
    
    # Step 4: Fetch chunks from neighbor notes
    neighbor_chunks = []
    for neighbor in expanded:
        chunks = get_chunks_from_note(neighbor.id)
        for chunk in chunks:
            chunk.score = neighbor.score
            neighbor_chunks.append(chunk)
    
    # Step 5: Merge and rerank
    all_candidates = candidates + neighbor_chunks
    reranked = cross_encoder_rerank(query, all_candidates, top_k=8)
    
    return reranked
```

**Expansion Strategy:**
```
Initial: [Note A] (score: 0.95)
  → 1-hop: [Note B] (linked, score: 0.95 * 0.65 = 0.62)
          [Note C] (tagged, score: 0.95 * 0.65 = 0.62)
  → 2-hop: [Note D] (linked from B, score: 0.62 * 0.65 = 0.40)
```

#### 3.5 Related Notes UI

```typescript
interface RelatedNotes {
  note: {
    title: string
    path: string
    citation: string  // "Momentum Trading#Indicators"
  }
  hop_count: number
  edge_type: "link" | "embed" | "tag"
  relevance_score: number
}

// Display in UI
"📚 Related Notes:
  • Momentum Trading → Indicators (1 hop, linked)
  • RSI Deep Dive (1 hop, tagged: #trading)
  • Technical Analysis → Chart Patterns (2 hops)"
```

### Requirements

**Inputs:**
- User query
- Initial candidate chunks (BM25 + dense)
- Graph structure (notes + edges)

**Outputs:**
- Merged candidate set with graph scores
- Same synthesis step as current system
- Related notes metadata for UI

**Config Knobs:**
```python
GRAPH_ENABLED = True
GRAPH_HOPS = 1  # or 2 (more hops = more latency)
GRAPH_DECAY = 0.65  # Score decay per hop
GRAPH_K = 5  # Extra chunks per neighbor note
TAG_EDGE_WEIGHT = 0.8  # Tags weighted slightly lower than links
```

### KPIs

- ✅ +10-20% nDCG@10 on concept queries
- ✅ No drop in faithfulness (must maintain source quality)
- ✅ Latency: ≤ +15% after graph expansion + reranking

### Best Practices

1. **Start with Postgres** - Adjacency lists are simple and fast
2. **Add Neo4j later** - Only if you need Cypher analytics or visualizations
3. **Normalize aliases/titles** - Build backlinks in second pass
4. **Cache adjacency lists** - Keep hot notes in memory (Redis)
5. **FS watcher** - Incrementally update notes/edges on file changes

### Tools & Integrations

- **Storage:**
  - Postgres (adjacency lists) - Simple, fast
  - Neo4j Community (graph DB) - Advanced queries
  
- **Embedder:** BAAI/bge-m3 (already in stack)
- **Reranker:** BAAI/bge-reranker-large (already in stack)
- **Watcher:** Python `watchdog` for FS monitoring

### Acceptance Criteria

- ✅ +10-20% nDCG@10 on conceptual queries
- ✅ Equal or better latency after rerank
- ✅ Backlinks correctly resolved
- ✅ Heading paths preserved in citations

---

## 4. Automatic Mode & Model Routing (Planner)

**Goal:** Intelligently route queries to the best mode and model

### Features

#### 4.1 Mode Planner

```python
class ModePlanner:
    """Choose optimal mode based on prompt signals."""
    
    def plan(self, prompt: str, context: Context) -> Mode:
        """Heuristic + tiny classifier for mode selection."""
        
        # Rule-based detection
        signals = {
            "has_urls": bool(re.search(r'https?://', prompt)),
            "has_dates": bool(re.search(r'today|this week|yesterday', prompt, re.I)),
            "has_tickers": bool(re.search(r'\b[A-Z]{1,5}\b', prompt)),
            "has_vault_tags": bool(re.search(r'#\w+', prompt)),
            "has_doc_refs": bool(re.search(r'PDF|report|transcript|document', prompt, re.I)),
            "is_realtime": bool(re.search(r'latest|current|now|breaking', prompt, re.I))
        }
        
        # Decision logic
        if signals["has_vault_tags"] or "obsidian" in prompt.lower():
            return Mode.OBSIDIAN
        
        if signals["is_realtime"] or signals["has_urls"]:
            return Mode.WEB_SEARCH
        
        if signals["has_doc_refs"] or signals["has_tickers"]:
            return Mode.RAG
        
        # Ambiguous → classifier or default to comprehensive
        if self.is_ambiguous(signals):
            return self.classifier.predict(prompt)
        
        return Mode.COMPREHENSIVE
```

**Signals:**
- URLs → Web Search
- "today", "this week" → Web Search
- Tickers (AAPL, MSFT) → RAG
- `#tags` → Obsidian
- "PDF", "report", "transcript" → RAG
- "latest", "breaking" → Web Search

#### 4.2 Model/Engine Router

```python
class ModelRouter:
    """Pick optimal model and runtime."""
    
    def route(self, task: Task) -> ModelConfig:
        """Select model based on context window, task type, latency needs."""
        
        # Context window requirements
        if task.context_length > 32000:
            return ModelConfig(
                model_id="qwen2.5:14b",
                engine="vllm",  # Better for long context
                max_tokens=8192
            )
        
        # Task type optimization
        if task.type == "code":
            return ModelConfig(
                model_id="qwen2.5-coder:14b",
                engine="ollama"
            )
        
        # Latency-sensitive
        if task.requires_fast_response:
            return ModelConfig(
                model_id="llama3.2:3b",
                engine="ollama"
            )
        
        # Default
        return ModelConfig(
            model_id="qwen2.5:14b",
            engine="ollama"
        )
```

#### 4.3 Policy & Profiles

```python
# Per-mode defaults
MODE_PROFILES = {
    "web": {
        "context_window": 32000,  # Longer for web results
        "style": "conversational",
        "cite_format": "URL"
    },
    "obsidian": {
        "enable_graph": True,
        "graph_hops": 2,
        "cite_format": "[[Note#Heading]]"
    },
    "rag": {
        "faithfulness_check": True,
        "cite_format": "document.pdf [Page X]"
    },
    "comprehensive": {
        "enable_graph": True,
        "enable_web": True,
        "max_sources": 20
    }
}
```

#### 4.4 Telemetry

```python
# Log every decision
logger.info({
    "planner_decision": "rag",
    "confidence": 0.92,
    "signals": {"has_tickers": True, "has_doc_refs": True},
    "model_selected": "qwen2.5:14b",
    "engine": "ollama",
    "user_override": False
})
```

### Requirements

**Inputs:**
- Uplift output (improved prompt + entities)
- Mode hints (user's UI selection if explicit)
- Context length estimate
- User preferences

**Outputs:**
```json
{
    "mode": "rag",
    "model_id": "qwen2.5:14b",
    "engine": "ollama",
    "profile": {
        "faithfulness_check": true,
        "cite_format": "document.pdf [Page X]"
    },
    "parameters": {
        "temperature": 0.1,
        "max_tokens": 2048
    }
}
```

**Performance:**
- Latency budget: ≤ 50-100ms
- Cache decisions per conversation

### Configuration

```python
# Thresholds
CONTEXT_LENGTH_THRESHOLD = 32000
MIN_CONFIDENCE_FOR_OVERRIDE = 0.9

# Per-mode defaults
MODE_DEFAULTS = {
    "rag": {"temperature": 0.1, "max_tokens": 2048},
    "web": {"temperature": 0.3, "max_tokens": 4096},
    "obsidian": {"temperature": 0.2, "max_tokens": 3072}
}

# User overrides
ALLOW_USER_OVERRIDE = True  # "Stick with this model for this chat"
```

### Best Practices

1. **Prefer rules first** - Only invoke classifier when ambiguous
2. **Cache decisions** - Per conversation unless prompt materially changes
3. **Provide user override** - "Use this model for next 5 messages"
4. **Graceful fallback** - If model unavailable, fall back to default

### Tools & Integrations

- **Classifier LLM:**
  - `llama3.2:3b` (fast, 50-100ms)
  - Or simple rules (even faster)
  
- **Engines:**
  - Ollama (default for most)
  - vLLM sidecar (long context, batch)
  
- **Registry:**
  - JSON/YAML model registry
  ```yaml
  - id: qwen2.5:14b
    engine: ollama
    endpoint: http://ollama:11434
    context_window: 32768
    capabilities: [general, coding, analysis]
  ```

### Acceptance Criteria

- ✅ Correct mode/model ≥90% on labeled sample (100+ queries)
- ✅ Graceful fallback if model unavailable
- ✅ ≤100ms overhead
- ✅ User override respected

---

## 5. Monitoring & Dashboards (Prometheus/Grafana + Loki)

**Goal:** Production-grade observability for RAG pipeline

### Features

#### 5.1 Metrics by Stage

```python
# Prometheus metrics
from prometheus_client import Counter, Histogram, Gauge

# Retrieval stage
retrieval_latency = Histogram(
    'rag_retrieval_latency_seconds',
    'Retrieval latency by method',
    ['method']  # bm25, dense, graph
)

retrieval_count = Counter(
    'rag_retrieval_total',
    'Total retrievals by method',
    ['method', 'mode']
)

# Reranker stage
rerank_latency = Histogram(
    'rag_rerank_latency_seconds',
    'Cross-encoder reranking latency'
)

# LLM stage
llm_latency = Histogram(
    'rag_llm_latency_seconds',
    'LLM generation latency',
    ['model_id', 'engine']
)

llm_tokens = Counter(
    'rag_llm_tokens_total',
    'Total tokens generated',
    ['model_id', 'type']  # prompt, completion
)

# Cache
cache_hit_rate = Gauge(
    'rag_cache_hit_rate',
    'Cache hit rate by type',
    ['cache_type']  # redis, embeddings, bm25
)

# Errors
error_count = Counter(
    'rag_errors_total',
    'Total errors by stage',
    ['stage', 'error_type']
)
```

#### 5.2 Quality Metrics

```python
# Golden set evaluation (nightly job)
quality_ndcg = Gauge(
    'rag_quality_ndcg_at_10',
    'nDCG@10 on golden set',
    ['mode']
)

quality_faithfulness = Gauge(
    'rag_quality_faithfulness_rate',
    'Faithfulness rate (verified claims)',
    ['mode']
)

quality_retry_rate = Gauge(
    'rag_quality_retry_rate',
    'Percentage of answers needing verifier retry',
    ['mode']
)
```

#### 5.3 Infrastructure Metrics

```python
# GPU (via DCGM exporter)
# - dcgm_gpu_utilization
# - dcgm_gpu_memory_used
# - dcgm_gpu_temp

# CPU/Memory (via node_exporter)
# - node_cpu_seconds_total
# - node_memory_MemAvailable_bytes

# Redis
redis_qps = Gauge('redis_qps', 'Redis queries per second')
redis_latency = Histogram('redis_latency_seconds', 'Redis command latency')

# ChromaDB
chromadb_query_latency = Histogram(
    'chromadb_query_latency_seconds',
    'ChromaDB query latency'
)

# Web crawler
crawler_queue_depth = Gauge(
    'crawler_queue_depth',
    'Number of URLs waiting to be crawled'
)
crawler_freshness = Gauge(
    'crawler_freshness_seconds',
    'Time since last crawl for active sources'
)
```

#### 5.4 Dashboards

**Dashboard 1: SLO Health (Quick Status)**
```
┌─────────────────────────────────────────┐
│  GraphMind RAG - Health Dashboard       │
├─────────────────────────────────────────┤
│  P50 Latency:  1.2s  [Target: <2s]  ✓  │
│  P95 Latency:  3.5s  [Target: <5s]  ✓  │
│  Error Rate:   0.2%  [Target: <1%]  ✓  │
│  Cache Hit:    78%   [Target: >70%] ✓  │
├─────────────────────────────────────────┤
│  Quality (Last 24h):                    │
│  nDCG@10:      0.87  [Target: >0.85] ✓ │
│  Faithfulness: 0.96  [Target: >0.95] ✓ │
└─────────────────────────────────────────┘
```

**Dashboard 2: Quality Deep Dive**
```
┌─────────────────────────────────────────┐
│  GraphMind RAG - Quality Metrics        │
├─────────────────────────────────────────┤
│  nDCG@10 by Mode:                       │
│    RAG:          0.89                   │
│    Obsidian:     0.91                   │
│    Web:          0.82                   │
│    Comprehensive: 0.87                  │
├─────────────────────────────────────────┤
│  Faithfulness Rate:                     │
│    [Graph: 95-98% over 7 days]          │
│                                         │
│  Retry Rate (Verifier):                 │
│    [Graph: 3-5% over 7 days]            │
└─────────────────────────────────────────┘
```

**Dashboard 3: Infrastructure**
```
┌─────────────────────────────────────────┐
│  GraphMind RAG - Infrastructure         │
├─────────────────────────────────────────┤
│  GPU Utilization:  78%  [2x RTX 4090]   │
│  GPU Memory:       18GB / 24GB          │
│  GPU Temp:         72°C / 85°C max      │
├─────────────────────────────────────────┤
│  CPU Usage:        45% [24 cores]       │
│  Memory:           62GB / 100GB         │
│  Redis QPS:        1.2K                 │
│  ChromaDB Latency: 120ms p95            │
└─────────────────────────────────────────┘
```

**Dashboard 4: Web Search**
```
┌─────────────────────────────────────────┐
│  GraphMind RAG - Web Search             │
├─────────────────────────────────────────┤
│  Crawler Queue:    12 URLs pending      │
│  Source Freshness: 2.3h avg             │
│  Domain Mix (24h):                      │
│    .com:  45%                           │
│    .org:  22%                           │
│    .edu:  18%                           │
│    other: 15%                           │
└─────────────────────────────────────────┘
```

#### 5.5 Alerts

```yaml
# Prometheus alert rules
groups:
  - name: rag_slo
    rules:
      - alert: HighLatency
        expr: histogram_quantile(0.95, rag_llm_latency_seconds) > 5
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "P95 latency above 5s"
      
      - alert: FaithfulnessDrop
        expr: rag_quality_faithfulness_rate < 0.95
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Faithfulness dropped below 95%"
      
      - alert: RerankerFailures
        expr: rate(rag_errors_total{stage="reranker"}[5m]) > 0.01
        for: 3m
        labels:
          severity: warning
        annotations:
          summary: "Reranker error rate elevated"
      
      - alert: CrawlerBacklog
        expr: crawler_queue_depth > 1000
        for: 30m
        labels:
          severity: warning
        annotations:
          summary: "Crawler queue backed up"
```

### Requirements

**Instrumentation:**
- Expose Prometheus endpoints in backend services
- Add labels: `{mode, engine, model_id, stage}`
- Use consistent metric names (see "Runbook")

**Golden Set Job:**
```python
# Nightly eval (GitHub Actions cron)
def run_golden_set_eval():
    """Evaluate RAG quality on golden question set."""
    for mode in ["rag", "obsidian", "web", "comprehensive"]:
        # Run 100 queries
        results = evaluate_mode(mode, golden_set)
        
        # Push metrics to Prometheus pushgateway
        push_metric("rag_quality_ndcg_at_10", results.ndcg, {"mode": mode})
        push_metric("rag_quality_faithfulness_rate", results.faithfulness, {"mode": mode})
    
    # Block deployment if regression
    if results.ndcg < NDC_THRESHOLD or results.faithfulness < FAITH_THRESHOLD:
        raise Exception("Quality regression detected - blocking deploy")
```

**Retention:**
- Prometheus: 15-30 days for time-series
- Loki: 30 days for logs (searchable)
- Long-term: Export to S3 for analysis

### Best Practices

1. **Keep metric names stable** - Document in Runbook, version changes
2. **One quick health dashboard** - For on-call, alerts
3. **One deep-dive dashboard** - For R&D, debugging
4. **Add trace IDs** - Correlate slow requests across stages
5. **Test alerts** - Regularly trigger and verify alert routing

### Tools & Integrations

- **Prometheus + Grafana** - Metrics and dashboards
- **Loki** - Log aggregation and search
- **Tempo** (optional) - Distributed tracing
- **NVIDIA DCGM Exporter** - GPU metrics
- **GitHub Actions** - Nightly golden set eval
- **Pushgateway** - For batch job metrics

### Acceptance Criteria

- ✅ Dashboards live and accessible
- ✅ Alerts configured and firing correctly
- ✅ Nightly eval publishing nDCG + faithfulness
- ✅ CI/CD gate: Deploys blocked if quality < threshold
- ✅ Runbook documented with metric definitions

---

## Summary: Acceptance Criteria (All Five Features)

| Feature | Key Metrics | Target | Status |
|---------|-------------|--------|--------|
| **Prompt Uplift** | nDCG@10 improvement | +10% | 📋 Planned |
| | Added latency (p95) | ≤600ms | 📋 Planned |
| | Fact injection violations | 0 | 📋 Planned |
| **Self-Check** | Faithfulness rate | ≥95% | 📋 Planned |
| | Latency increase | ≤20% | 📋 Planned |
| | Unsupported claims | Marked with ⚠️ | 📋 Planned |
| **GraphRAG** | nDCG@10 improvement | +10-20% | 📋 Planned |
| | Latency after rerank | ≤+15% | 📋 Planned |
| | Citation accuracy | 100% | 📋 Planned |
| **Planner/Router** | Mode/model accuracy | ≥90% | 📋 Planned |
| | Overhead | ≤100ms | 📋 Planned |
| | Fallback | Graceful | 📋 Planned |
| **Monitoring** | Dashboards | 4 live | 📋 Planned |
| | Alerts | Configured | 📋 Planned |
| | Nightly eval | Publishing | 📋 Planned |
| | CI/CD gate | Active | 📋 Planned |

---

## Implementation Timeline

### Phase 1: Foundation (Weeks 1-3)
- ✅ Week 1: Semantic chunking + token-based splitting
- ✅ Week 2: HyDE question generation
- ✅ Week 3: Prompt uplift + query expansion

### Phase 2: Verification & Quality (Weeks 4-6)
- ✅ Week 4: Self-check verifier (Pass 1 + Pass 2)
- ✅ Week 5: Auto-repair logic + UI trust markers
- ✅ Week 6: Golden set creation + nightly eval

### Phase 3: Graph & Routing (Weeks 7-10)
- ✅ Week 7: Obsidian parser + graph store (Postgres)
- ✅ Week 8: Query-time graph expansion
- ✅ Week 9: Mode planner + model router
- ✅ Week 10: Policy profiles + telemetry

### Phase 4: Monitoring & Polish (Weeks 11-12)
- ✅ Week 11: Prometheus instrumentation + dashboards
- ✅ Week 12: Alerts + CI/CD gates + documentation

**Total Timeline:** 12 weeks to world-class (A+) RAG system

---

## Resources

- **Related Docs:**
  - `docs/RAG_INGESTION_ANALYSIS.md` - Current RAG analysis
  - `docs/RAG_QUICK_REFERENCE.md` - Quick reference
  - `docs/STRATEGY_AND_ROADMAP.md` - Overall roadmap
  
- **Key Papers:**
  - HyDE: "Precise Zero-Shot Dense Retrieval without Relevance Labels"
  - Self-Check: "SelfCheckGPT: Zero-Resource Black-Box Hallucination Detection"
  - GraphRAG: "From Local to Global: A Graph RAG Approach"

---

**Next Steps:**
1. Review and approve implementation plan
2. Prioritize features (recommend: Uplift → Self-Check → GraphRAG → Router → Monitoring)
3. Begin Phase 1: Semantic chunking + HyDE + Uplift

