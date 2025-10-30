# 🤖 For Cursor-Agent: Build Instructions

**Task**: Implement Prompt Uplift + Query Expansion  
**Timeline**: 10 working days  
**Expected Impact**: +10-20% retrieval relevance

---

## 🎯 Your Mission

Build a query pre-processing pipeline that makes GraphMind understand vague questions better.

**What you're building**:
```
"trading strategies" 
    ↓ [classify → uplift → expand]
"Provide 3-5 specific trading strategies with risk profiles..." + 3 variants
    ↓ [retrieve better results]
10-20% better relevance! 🎯
```

---

## 📋 Build Specification

**PRIMARY DOCUMENT**: `/home/brad/cursor_code/GraphMind/CURSOR_AGENT_BUILD_SPEC.md`

This contains:
- ✅ 10 detailed tickets (TICKET 1 through TICKET 10)
- ✅ Complete requirements for each
- ✅ Code skeletons and examples
- ✅ Test specifications (40+ tests)
- ✅ Acceptance criteria
- ✅ Data models
- ✅ Configuration requirements

**READ THIS FIRST** ⭐️⭐️⭐️

---

## 📐 Implementation Order

### Phase 1: Core Components (Day 1-5)

**TICKET 1** (Day 1-2): Create `app/prompt_classifier.py`
- Rule-based query classification
- LLM fallback for ambiguous queries
- Extract: tickers, indicators, dates, task type
- Tests: 8 unit tests
- Performance: <100ms target

**TICKET 2** (Day 3-4): Create `app/prompt_uplifter.py`
- Template-based uplift (fallback)
- LLM-based uplift (primary)
- Fact injection detection
- Tests: 10 unit tests
- Performance: <300ms target

**TICKET 3** (Day 5): Create `app/query_expander.py`
- 3 expansion strategies (paraphrase, aspect, HyDE)
- Diversity validation
- Tests: 7 unit tests
- Performance: <200ms for 3 expansions

### Phase 2: Integration (Day 6-7)

**TICKET 4** (Day 6-7): Create `app/prompt_uplift_pipeline.py`
- Orchestrate classifier → uplifter → expander
- Caching with Redis
- Confidence-based fallback
- Skip logic for good baseline
- Tests: 5 unit tests
- Performance: <600ms total

**TICKET 5** (Day 6-7): Modify `app/main.py`
- Integrate pipeline into `/ask` endpoint
- Handle multiple query variants
- Merge and deduplicate results
- Add uplift metadata to response

**TICKET 6** (Day 6): Create `app/prompt_uplift_config.py`
- Configuration management
- Feature flags
- Tunable parameters

### Phase 3: Validation (Day 8)

**TICKET 7** (Day 8): Create tests + golden set
- 30 unit tests total
- 10 integration tests
- Golden set (50-100 questions)
- Measure nDCG improvement ≥10%

### Phase 4: Production (Day 9-10)

**TICKET 8** (Day 9): Monitoring
- Create `app/monitoring/prompt_uplift_metrics.py`
- Add Prometheus metrics
- Create Grafana dashboard

**TICKET 9** (Day 10): Documentation
- User guide
- API documentation
- Update README

**TICKET 10** (Day 10): Deployment
- Feature flag
- Gradual rollout (10% → 50% → 100%)
- Production monitoring

---

## ✅ Acceptance Criteria (Must Meet All)

### Functional
- [ ] All 4 components working (classifier, uplifter, expander, pipeline)
- [ ] Integration with /ask endpoint complete
- [ ] Feature flag implemented
- [ ] Caching working
- [ ] Fallback logic working

### Performance
- [ ] Total pipeline latency: <600ms p95
- [ ] Classification: <100ms p95
- [ ] Uplift: <300ms p95
- [ ] Expansion: <200ms total

### Quality
- [ ] nDCG@10 improvement: **≥10%** on golden set
- [ ] Fact injection violations: **0** (zero tolerance)
- [ ] Confidence calibration: ≥90% accurate
- [ ] Test coverage: ≥95%
- [ ] All 40+ tests: **100% passing**

### Operational
- [ ] Prometheus metrics exporting
- [ ] Grafana dashboard created
- [ ] Documentation complete
- [ ] Feature flag rollback tested

---

## 📚 Reference Documents

### Complete Implementation Details
**docs/implementation/PROMPT_UPLIFT_IMPLEMENTATION_PLAN.md** (30+ pages)
- Full code for all 4 components
- Complete testing strategy
- Configuration examples
- Best practices
- Monitoring setup

### Day-by-Day Breakdown
**docs/implementation/ROADMAP_NEXT_FEATURE.md** (20+ pages)
- Hour-by-hour task breakdown
- Example transformations
- Visual diagrams
- Checkpoint criteria

### Original Specification
**docs/ADVANCED_RAG_FEATURES.md**
- Feature context
- Research papers
- Related features

---

## 🧪 Testing Requirements

### Tests to Create (40+ tests)

```
tests/unit/
├── test_prompt_classifier.py          # 8 tests
├── test_prompt_uplifter.py            # 10 tests
├── test_query_expander.py             # 7 tests
└── test_prompt_uplift_pipeline.py     # 5 tests

tests/integration/
└── test_prompt_uplift_integration.py  # 10 tests

tests/evaluation/
├── golden_questions.json              # 50-100 Q&A pairs
└── test_golden_set_uplift.py          # Evaluation script
```

### Validation Steps

**After Each Component**:
```bash
pytest tests/unit/test_prompt_*.py -v --cov=app
```

**After Integration**:
```bash
pytest tests/integration/test_prompt_uplift_integration.py -v
```

**Final Validation**:
```bash
python tests/evaluation/test_golden_set_uplift.py
# Must show: ≥10% nDCG improvement ✅
```

---

## 🎯 Success Metrics

### Must Achieve

| Metric | Target | Validation Method |
|--------|--------|-------------------|
| **nDCG@10 Improvement** | ≥10% | Golden set evaluation |
| **Added Latency (p95)** | ≤600ms | Performance benchmarks |
| **Fact Injection** | 0 violations | Automated validation |
| **Confidence Accuracy** | ≥90% | Calibration testing |
| **Test Coverage** | ≥95% | pytest-cov |
| **Tests Passing** | 100% | All 40+ tests |

### Impact

**Before**: B+ (85/100) - Top 20%  
**After**: A- (88-90/100) - Top 10%  
**Path to**: A+ (95/100) - Top 1%

---

## 🚀 How to Start

### For Cursor-Agent

**Option 1 - Auto Build**:
```bash
cursor-agent build --spec CURSOR_AGENT_BUILD_SPEC.md
```

**Option 2 - Resume Session**:
```bash
cursor-agent --resume=422da8fd-5c19-43fd-8cdc-41ad2736a26c
```

Then provide:
```
Task: Implement Prompt Uplift + Query Expansion
Spec: CURSOR_AGENT_BUILD_SPEC.md
Follow: Tickets 1-10 in order
```

### First File to Create
`app/prompt_classifier.py` - Start with TICKET 1 requirements

---

## 📦 Everything You Need

### Build Specification ✅
- **CURSOR_AGENT_BUILD_SPEC.md** - 10 detailed tickets with all requirements

### Implementation Details ✅
- **docs/implementation/PROMPT_UPLIFT_IMPLEMENTATION_PLAN.md** - Complete code examples
- **docs/implementation/ROADMAP_NEXT_FEATURE.md** - Day-by-day breakdown

### Supporting Infrastructure ✅
- 231+ existing tests (validation framework)
- CI/CD pipeline configured
- Test fixtures and helpers ready
- Performance benchmarks established

### Quality Gates ✅
- Automated testing required
- Coverage >95% enforced
- Performance targets defined
- Golden set evaluation mandatory

---

## 🎓 Context for Cursor-Agent

### What Was Just Completed
- ✅ Fixed 3 P1 bugs (dark mode, chat deletion, prompt persistence)
- ✅ Created 131+ new tests (unit, integration, E2E, performance)
- ✅ Set up complete CI/CD pipeline
- ✅ Achieved 90-95% test coverage infrastructure
- ✅ Validated all fixes with automated tests

### What's Ready to Build
- ✅ Detailed specification (10 tickets)
- ✅ Complete code examples
- ✅ Test requirements defined
- ✅ Success criteria clear
- ✅ All dependencies available
- ✅ Infrastructure ready

### Confidence Level
**VERY HIGH** - Comprehensive planning + solid foundation + clear requirements

---

## 📊 Expected Deliverables

After cursor-agent completes:

**Files Created**: 15 new files
- 5 core implementation files
- 6 test files
- 2 evaluation files
- 1 monitoring file
- 1 documentation file

**Files Modified**: 3 files
- app/main.py (integration)
- app/config.py (configuration)
- app/models.py (data models)

**Test Results**:
- ✅ 40+ tests passing (100%)
- ✅ 95%+ code coverage
- ✅ ≥10% nDCG improvement
- ✅ <600ms latency validated

**Impact**:
- RAG Grade: B+ → A- (88-90/100)
- Retrieval Quality: +15-20% improvement
- User Experience: Better (vague queries work well)

---

## 🎉 Summary

**All documentation saved to `docs/`** ✅  
**Build specification ready** ✅  
**Cursor-agent can start immediately** ✅

### Key Files
1. **CURSOR_AGENT_START_HERE.md** - Cursor-agent entry point
2. **CURSOR_AGENT_BUILD_SPEC.md** - Complete build specification
3. **docs/implementation/** - Detailed implementation plans
4. **docs/sprints/** - Latest session summaries

---

**Ready to build world-class RAG!** 🚀🎯

**Next command**: `cursor-agent build --spec CURSOR_AGENT_BUILD_SPEC.md`

