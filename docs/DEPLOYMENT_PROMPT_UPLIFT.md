# Prompt Uplift Feature - Deployment Guide

**Feature**: Prompt Uplift + Query Expansion  
**Status**: ✅ Ready for Production  
**Feature Flag**: `PROMPT_UPLIFT_ENABLED`

---

## 🚀 Deployment Strategy

### Phase 1: Deploy with Feature Flag OFF

**Steps:**

1. **Deploy code** with feature flag disabled:
   ```bash
   # Set environment variable
   export PROMPT_UPLIFT_ENABLED=false
   
   # Or in docker-compose
   environment:
     - PROMPT_UPLIFT_ENABLED=false
   ```

2. **Restart services**:
   ```bash
   docker compose -f docker-compose.graphmind.yml restart graphmind-rag
   ```

3. **Verify**:
   - ✅ System still works normally
   - ✅ No errors in logs
   - ✅ Existing queries return same results

### Phase 2: Enable for 10% of Traffic (Optional)

**If using traffic splitting:**

1. Update feature flag logic to enable for 10% of users:
   ```python
   # In app/main.py
   if FEATURES.get("prompt_uplift", False) and hash(user_id) % 10 == 0:
       # Enable uplift for 10% of users
   ```

2. Monitor metrics:
   - Latency impact
   - Error rates
   - User feedback

### Phase 3: Enable for All Traffic

**Steps:**

1. **Enable feature flag**:
   ```bash
   export PROMPT_UPLIFT_ENABLED=true
   ```

2. **Restart services**:
   ```bash
   docker compose -f docker-compose.graphmind.yml restart graphmind-rag
   ```

3. **Monitor** for 1 hour:
   - Check logs: `docker logs -f graphmind-rag | grep "prompt_uplift"`
   - Monitor metrics: `/metrics` endpoint
   - Check error rates
   - Monitor latency

4. **Validate**:
   - Test with sample queries
   - Verify metadata in responses
   - Check cache hit rate

---

## 🔧 Feature Flag Configuration

### Environment Variables

```bash
# Enable/disable prompt uplift
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

### Code Location

Feature flag is checked in:
- `app/config.py` - `FEATURES` dictionary
- `app/main.py` - `/ask` endpoint

---

## 📊 Monitoring After Deployment

### Key Metrics to Watch

1. **Latency**:
   ```bash
   # Check Prometheus metrics
   curl http://localhost:8000/metrics | grep prompt_uplift_latency
   ```

2. **Confidence Scores**:
   ```bash
   curl http://localhost:8000/metrics | grep prompt_uplift_confidence
   ```

3. **Cache Hit Rate**:
   ```bash
   curl http://localhost:8000/metrics | grep uplift_cache
   ```

4. **Fallback Rate**:
   ```bash
   curl http://localhost:8000/metrics | grep fallback
   ```

### Logs to Monitor

```bash
# Uplift activity
docker logs -f graphmind-rag | grep "prompt_uplift"

# Errors
docker logs -f graphmind-rag | grep -i "error.*uplift"

# Performance
docker logs -f graphmind-rag | grep "latency_ms"
```

---

## 🔄 Rollback Plan

### If Issues Occur

1. **Disable feature flag**:
   ```bash
   export PROMPT_UPLIFT_ENABLED=false
   docker compose -f docker-compose.graphmind.yml restart graphmind-rag
   ```

2. **Verify rollback**:
   - System returns to baseline behavior
   - No errors in logs
   - Existing functionality works

3. **Investigate**:
   - Check logs for errors
   - Review metrics
   - Analyze uplift transformations

---

## ✅ Pre-Deployment Checklist

- [ ] Feature flag configured (`PROMPT_UPLIFT_ENABLED`)
- [ ] All tests passing (40+ tests)
- [ ] Code reviewed
- [ ] Documentation complete
- [ ] Monitoring configured
- [ ] Rollback plan tested
- [ ] Environment variables set
- [ ] Services can restart cleanly

---

## 🎯 Post-Deployment Validation

### Immediate Checks (First 10 minutes)

- [ ] System starts without errors
- [ ] Feature flag is respected
- [ ] Logs show uplift activity (if enabled)
- [ ] No increase in error rate
- [ ] Response times acceptable

### Extended Validation (First hour)

- [ ] Cache hit rate >50%
- [ ] Latency within budget (<600ms)
- [ ] Confidence scores reasonable (>0.7 average)
- [ ] Fallback rate <10%
- [ ] No fact injection violations

### Long-term Monitoring (First week)

- [ ] nDCG improvement measured
- [ ] User feedback positive
- [ ] No performance degradation
- [ ] Metrics stable

---

## 📝 Deployment Commands

### Full Deployment

```bash
# 1. Set environment variables
export PROMPT_UPLIFT_ENABLED=true
export PROMPT_EXPANSION_COUNT=3
export PROMPT_CONFIDENCE_THRESHOLD=0.75

# 2. Restart services
docker compose -f docker-compose.graphmind.yml restart graphmind-rag

# 3. Verify
docker logs -f graphmind-rag | grep "prompt_uplift"

# 4. Test
curl -X POST http://localhost:8000/ask \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"query": "trading strategies", "mode": "qa"}'
```

### Rollback

```bash
# Disable feature
export PROMPT_UPLIFT_ENABLED=false
docker compose -f docker-compose.graphmind.yml restart graphmind-rag
```

---

## 🎉 Deployment Complete

After successful deployment:

1. ✅ Feature is live
2. ✅ Monitoring active
3. ✅ Documentation updated
4. ✅ Team notified

**Next Steps**: Monitor for 1 week, then proceed with next roadmap item (Self-Check Verification)

---

**Last Updated**: October 30, 2025  
**Version**: 3.0.0
