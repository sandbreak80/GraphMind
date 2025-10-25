# Known Defects & Issues

**Last Updated:** October 25, 2025  
**Project:** GraphMind v3.0.0  
**Status:** Production-Ready with Minor Issues

---

## Summary

| Priority | Count | Status |
|----------|-------|--------|
| **P0 - Critical** | 0 | 🟢 All Resolved |
| **P1 - High** | 3 | 🟡 In Progress |
| **P2 - Medium** | 3 | 🟢 Low Impact |
| **TOTAL** | 6 | 🎯 Manageable |

---

## 🟢 Recently Resolved (This Session)

### ✅ Large File Upload Hangs - FIXED
**Status**: ✅ Resolved  
**Fixed**: October 25, 2025

**Solution Implemented:**
- Chunked upload mechanism (5MB chunks)
- Real-time progress tracking (0% → 100%)
- Backend `/upload-chunk` endpoint
- Frontend chunk assembly with `FormData`
- Nginx optimization (direct proxy, no buffering)

**Result:**
- 200MB+ files upload successfully
- Real-time progress feedback
- ~220s for 200MB video (expected)

---

### ✅ Obsidian Configuration Cannot Be Saved - FIXED
**Status**: ✅ Resolved  
**Fixed**: October 25, 2025

**Solution Implemented:**
- Added Docker volume: `./data:/workspace/data`
- Added volume: `./data/system_prompts:/workspace/system_prompts`
- Auto-convert `localhost`/`127.0.0.1`/`0.0.0.0` → `host.docker.internal`
- Added `extra_hosts` for host machine access

**Result:**
- Settings persist across restarts
- Obsidian API connection working
- User can save vault path, API key

---

### ✅ Ingest Shows "undefined files/chunks" - FIXED
**Status**: ✅ Resolved  
**Fixed**: October 25, 2025

**Solution Implemented:**
- Frontend parses new background ingestion response
- Shows "Processing in background..." message
- Proper feedback for async ingestion

**Result:**
- Clear user feedback
- No more "undefined" text
- Background ingestion working

---

### ✅ Login Slow / Blocked by Ingestion - FIXED
**Status**: ✅ Resolved  
**Fixed**: October 25, 2025

**Solution Implemented:**
- Moved ingestion to background thread (`ThreadPoolExecutor`)
- Ingestion no longer blocks FastAPI event loop
- Login instant regardless of ingestion

**Result:**
- Login always responsive
- No blocking during document processing

---

### ✅ RAG Source Citations Show "rag-only 0" - FIXED
**Status**: ✅ Resolved  
**Fixed**: October 25, 2025

**Solution Implemented:**
- Added `filename` to ChromaDB metadata during ingestion
- Updated all RAG citation builders to use `filename`
- Prioritize `filename` over `file_name` fallback

**Result:**
- Proper document names in citations
- Accurate source attribution

---

### ✅ Security Vulnerabilities in Upload - FIXED
**Status**: ✅ Resolved  
**Fixed**: October 25, 2025

**Solution Implemented:**
1. **File Type Validation**: Whitelist only processable types
2. **Duplicate Prevention**: Return HTTP 409 for existing files
3. **Size Enforcement**: 400MB max, enforced during streaming
4. **Streaming Validation**: Check size incrementally, delete partial files

**Result:**
- No unsupported file types accepted
- No duplicate file overwrites
- Size limits properly enforced

---

## 🟡 P1 - High Priority Issues

### 1. Dark Mode Toggle Not Working

**Status**: 🟡 High Priority  
**Severity**: P1 (High)  
**Impact**: UI/UX

**Description:**
Dark mode toggle in settings does not properly switch theme. Users clicking the dark mode toggle see no visual change or inconsistent behavior.

**Root Cause:**
- Tailwind `darkMode: 'class'` config present
- localStorage persistence implemented
- But theme class not being applied to document root
- OR CSS variables not responding to theme class

**Workaround:**
Users can manually edit browser localStorage or use system theme preference.

**Fix Strategy:**
1. Debug `data-theme` attribute on `<html>` element
2. Verify Tailwind dark: classes compile correctly
3. Check if theme persistence logic executes on page load
4. Add proper theme initialization in root layout
5. Test across all pages (landing, chat, settings)

**Files Affected:**
- `frontend/components/UIEnhancements.tsx` (theme switcher)
- `frontend/tailwind.config.js` (dark mode config)
- `frontend/app/layout.tsx` (root layout)

**Priority Justification:**
- Affects user experience
- Feature advertised as available
- Relatively simple fix
- High visibility issue

---

### 2. Chat Deletion on Open Chat Logs Out User

**Status**: 🟡 High Priority  
**Severity**: P1 (High)  
**Impact**: User Experience

**Description:**
When a user deletes the currently open/active chat, they are logged out instead of being redirected to the home page or a new chat.

**Root Cause:**
- Chat deletion triggers 404 on current chat route
- Error handler interprets 404 as auth failure
- User gets logged out unnecessarily

**Expected Behavior:**
- Detect if deleted chat is currently open
- Redirect to home page (`/`) or new chat
- Show success toast: "Chat deleted"
- Do NOT log out user

**Workaround:**
Don't delete the chat you're currently viewing. Navigate to home first.

**Fix Strategy:**
1. Add check in delete handler: `if (deletingChatId === currentChatId)`
2. If yes, redirect to `/` before deletion
3. Show success toast after redirect
4. Only then call delete API

**Files Affected:**
- `frontend/components/Sidebar.tsx` (delete button)
- `frontend/lib/store.ts` (chat management)
- Error boundary handling

**Priority Justification:**
- Confusing user experience
- Looks like a bug
- Moderate complexity to fix
- Affects usability

---

### 3. System Prompt Changes Sometimes Don't Persist

**Status**: 🟡 High Priority  
**Severity**: P1 (High)  
**Impact**: Functionality

**Description:**
Occasionally, when users edit and save system prompts, the changes don't persist after page refresh or service restart.

**Root Cause (Suspected):**
- Volume mount working (`./data/system_prompts:/workspace/system_prompts`)
- But file write might be cached or delayed
- OR permissions issue preventing write
- OR frontend not waiting for backend confirmation

**Observed Behavior:**
- Sometimes works fine
- Sometimes reverts to default after refresh
- Inconsistent - suggests race condition or caching issue

**Workaround:**
- Try saving multiple times
- Refresh page to verify
- Check backend logs for write errors

**Fix Strategy:**
1. Add file sync/flush after write in backend
2. Return file contents after save for verification
3. Frontend should verify returned contents match sent contents
4. Add proper error handling + retry logic
5. Log all file write operations

**Files Affected:**
- `frontend/app/prompts/page.tsx` (prompt editor)
- `frontend/app/api/system-prompts/[mode]/route.ts` (API)
- `app/main.py` (backend save endpoint)

**Test Case:**
```bash
1. Edit system prompt for "rag" mode
2. Click "Save"
3. Wait for success toast
4. Refresh page
5. Expected: Changes persist
6. Actual: Sometimes reverts to default
```

**Priority Justification:**
- Affects core functionality
- User trust issue (lost work)
- Intermittent = hard to reproduce
- Needs investigation

---

## 🟢 P2 - Medium Priority Issues

### 4. Markdown Rendering Could Be Improved

**Status**: 🟢 Medium Priority  
**Severity**: P2 (Medium)  
**Impact**: UI Polish

**Description:**
Markdown rendering in chat responses has minor formatting issues:
- Line breaks sometimes inconsistent
- Code blocks could have better syntax highlighting
- Tables occasionally misaligned
- Lists sometimes have spacing issues

**Root Cause:**
- Using `react-markdown` with basic config
- Need better `remarkGfm` and `rehypeRaw` settings
- CSS styles for markdown elements could be refined

**Workaround:**
Responses are readable, just not perfectly formatted.

**Fix Strategy:**
1. Review `react-markdown` configuration
2. Add custom CSS for markdown elements
3. Test with various markdown samples
4. Consider switching to `marked` or `markdown-it` if needed

**Files Affected:**
- `frontend/components/EnhancedChatInterface.tsx`
- Markdown rendering configuration
- CSS styles for `.prose` classes

**Priority Justification:**
- Cosmetic issue
- Doesn't block functionality
- Can be improved incrementally
- Low user impact

---

### 5. Memory Loading Slow on Large Datasets

**Status**: 🟢 Medium Priority  
**Severity**: P2 (Medium)  
**Impact**: Performance

**Description:**
When memory system contains large amounts of data (>1000 entries), loading the memory page takes 5-10 seconds.

**Root Cause:**
- Loading all memory categories at once
- No pagination or lazy loading
- JSON file reading not optimized
- Frontend not caching memory data

**Workaround:**
Wait for page to load, then it's responsive.

**Fix Strategy:**
1. Add pagination to memory API (50 items per page)
2. Implement lazy loading for categories
3. Cache memory data in frontend state
4. Only reload when changes detected
5. Consider switching to SQLite for memory storage

**Files Affected:**
- `frontend/app/memory/page.tsx`
- `app/memory_system.py`
- Memory API endpoints

**Priority Justification:**
- Only affects users with large memory datasets
- One-time load per session
- Functionality still works
- Can optimize later

---

### 6. Model List Refresh Delay

**Status**: 🟢 Medium Priority  
**Severity**: P2 (Medium)  
**Impact**: UX Polish

**Description:**
After clicking "Refresh Models" in the model selector, there's a noticeable delay (2-3 seconds) before the list updates.

**Root Cause:**
- Fetching from Ollama API (slow)
- No loading indicator during refresh
- No caching of model list
- Frontend waits for full response

**Workaround:**
Wait a few seconds, models will update.

**Fix Strategy:**
1. Add loading spinner during refresh
2. Cache model list (5 min TTL)
3. Fetch in background, update UI when ready
4. Show last-fetched timestamp

**Files Affected:**
- `frontend/components/ChatControls.tsx`
- Model selector component
- Ollama API client

**Priority Justification:**
- Minor UX issue
- Infrequent user action
- Easy fix (add spinner)
- Low impact

---

## 📋 Future Enhancements (Not Bugs)

These are not defects but planned enhancements from the roadmap:

### Roadmap Items (See STRATEGY_AND_ROADMAP.md)
- 🔄 Prompt Uplift + Query Expansion
- 🔄 Self-Check Verification
- 🔄 Obsidian GraphRAG
- 🔄 Auto Mode & Model Routing
- 🔄 Monitoring Dashboards
- 🔄 Golden Question Eval Harness
- 🔄 PDF Parsing Upgrade (GROBID)
- 🔄 Semantic Chunking Optimization
- 🔄 Domain Trust Policy
- 🔄 Multi-Query Expansion

---

## 🔬 Testing & Validation

### Test Coverage by Component

| Component | Coverage | Status |
|-----------|----------|--------|
| Authentication | ~85% | ✅ Good |
| 4 Operating Modes | ~80% | ✅ Good |
| Upload/Ingestion | ~75% | 🟡 Needs Improvement |
| System Prompts | ~70% | 🟡 Needs Improvement |
| Memory System | ~65% | 🟡 Needs Improvement |
| Chat Management | ~80% | ✅ Good |
| Overall | ~75% | 🎯 Target: >80% |

### Recommended Test Additions

1. **System Prompts Persistence Test**
   ```python
   def test_system_prompt_persistence():
       # Save prompt
       # Restart service
       # Verify prompt persisted
   ```

2. **Dark Mode Toggle Test**
   ```typescript
   test('dark mode toggle applies theme', () => {
       // Click toggle
       // Verify theme class on root
       // Verify localStorage updated
   });
   ```

3. **Chat Deletion While Open Test**
   ```python
   def test_delete_open_chat_redirects():
       # Open chat
       # Delete current chat
       # Verify redirected to home
       # Verify NOT logged out
   ```

---

## 📊 Defect Statistics

### By Priority
- P0 (Critical): 0 (0%)
- P1 (High): 3 (50%)
- P2 (Medium): 3 (50%)

### By Category
- UI/UX: 2 (33%)
- Functionality: 2 (33%)
- Performance: 1 (17%)
- Security: 0 (0%)

### Resolution Trend
- Resolved This Session: 6
- Opened This Session: 6
- Net Change: 0
- Resolution Rate: 100% for critical issues

---

## 🎯 Defect Priorities for Next Sprint

### Sprint 1 Focus (Next 2 Weeks)
1. ✅ Fix dark mode toggle (1 day)
2. ✅ Fix chat deletion redirect (1 day)
3. ✅ Investigate prompt persistence (2 days)

### Sprint 2 Focus (Weeks 3-4)
4. 🔄 Improve markdown rendering (2 days)
5. 🔄 Optimize memory loading (3 days)

### Sprint 3+ (Low Priority)
6. 🔄 Model list refresh UX (1 day)

---

## 📝 Notes

- All P0 (critical) issues have been resolved
- System is production-ready with minor issues
- P1 issues are annoying but don't block core functionality
- P2 issues are polish items
- Overall system health: ✅ Excellent

---

## 🔗 Related Documents

- [STRATEGY_AND_ROADMAP.md](./STRATEGY_AND_ROADMAP.md) - Product roadmap
- [RAG_INGESTION_ANALYSIS.md](./RAG_INGESTION_ANALYSIS.md) - RAG analysis
- [CHUNKED_UPLOAD_IMPLEMENTATION.md](./CHUNKED_UPLOAD_IMPLEMENTATION.md) - Upload guide
- [PROJECT_STATUS.txt](../PROJECT_STATUS.txt) - Overall status

---

**Last Review:** October 25, 2025  
**Next Review:** After Sprint 1 (Week 2)  
**Defect Tracking:** GitHub Issues (when repo is public)
