# Known Defects

## Critical Defects

### 1. Large File Upload Hangs with Endless Spinner

**Status**: 🔴 Critical  
**Severity**: High  
**Priority**: P0

**Description**:
Uploading files larger than 200MB results in an endless spinning wheel with no progress indication or completion. The upload never completes from the user's perspective.

**Root Cause**:
1. Frontend routes upload through Next.js API route (`/api/documents/upload`)
2. Next.js reads entire file into memory before forwarding to backend
3. For 200MB+ files, this takes 5+ minutes with zero feedback
4. No real-time progress tracking (UI just shows 50% static progress)
5. Nginx direct proxy (`location /api/documents/upload`) is not being used due to route precedence

**Impact**:
- Users cannot upload video files or large PDFs
- No way to track upload progress
- Appears broken/hung to users
- Wasted bandwidth on failed uploads

**Workaround**:
None currently available.

**Fix Strategy**:
1. Implement chunked upload with progress tracking (recommended)
2. OR: Add WebSocket-based upload with real-time progress
3. OR: Use direct S3/Object Storage upload with presigned URLs
4. Update UI to show actual upload progress (bytes uploaded / total bytes)

**Files Affected**:
- `frontend/app/documents/page.tsx` (upload UI)
- `frontend/app/api/documents/upload/route.ts` (proxy route)
- `nginx/nginx.conf` (direct backend proxy not working)
- `app/main.py` (backend upload endpoint)

**Test Case**:
```bash
# Upload 200MB video file
# Expected: Progress bar shows real progress, completes in ~60s
# Actual: Spinner shows indefinitely, no feedback
```

---

### 2. Obsidian Configuration Cannot Be Saved

**Status**: 🔴 Critical  
**Severity**: High  
**Priority**: P0

**Description**:
Users cannot save Obsidian MCP configuration settings. When attempting to save vault path, connection settings, or other Obsidian-related configurations, the save operation fails silently or returns an error.

**Root Cause**:
[TO BE INVESTIGATED]

**Impact**:
- Obsidian mode is non-functional
- Cannot connect to Obsidian vaults
- Users cannot configure MCP settings
- Core feature broken

**Workaround**:
Manual configuration via environment variables (not user-friendly).

**Fix Strategy**:
1. Debug settings API endpoint
2. Check file permissions for settings storage
3. Verify frontend-backend API contract
4. Add proper error handling and feedback

**Files Affected**:
- `frontend/app/settings/page.tsx` (settings UI)
- `frontend/app/api/settings/route.ts` (settings API)
- `app/main.py` (backend settings endpoints)
- `app/obsidian_mcp_client.py` (Obsidian configuration)

**Test Case**:
```bash
# Navigate to Settings page
# Update Obsidian vault path
# Click "Save"
# Expected: Success message, settings persisted
# Actual: Error or silent failure
```

---

### 3. Ingest Shows "Successfully ingested undefined files (undefined chunks)"

**Status**: 🟡 Medium  
**Severity**: Medium  
**Priority**: P1

**Description**:
When running document ingestion, the success message displays "Successfully ingested undefined files (undefined chunks)" instead of showing actual numbers. This indicates a response parsing issue or missing data from the backend.

**Root Cause**:
Backend ingestion now runs in background thread (non-blocking) and returns immediately with status "started". Frontend expects `processed_files` and `total_chunks` in response, but gets `undefined`.

**Backend Response (Current)**:
```json
{
  "status": "started",
  "message": "Ingestion started in background for 49 files..."
}
```

**Frontend Expects**:
```json
{
  "status": "success",
  "processed_files": 49,
  "total_chunks": 1234,
  "failed_files": 0
}
```

**Impact**:
- Users don't know if ingestion succeeded
- No feedback on number of files/chunks processed
- Confusing UX

**Workaround**:
Check backend logs for actual ingestion results.

**Fix Strategy**:
1. Add `/api/documents/ingest-status` polling to track background ingestion
2. Update UI to show "Processing in background..." message
3. Poll ingestion status every 5 seconds until complete
4. Show final results when complete
5. OR: Keep synchronous ingestion for better UX (add progress streaming)

**Files Affected**:
- `frontend/app/documents/page.tsx` (lines 213-217)
- `frontend/app/api/documents/ingest/route.ts` (ingestion API)
- `app/main.py` (lines 318-325 - ingestion endpoint)

**Code Location**:
```typescript
// frontend/app/documents/page.tsx:215
toast.success(
  `✓ Successfully ingested ${data.processed_files} files (${data.total_chunks} chunks)`,
  // ^ data.processed_files is undefined because backend returns "started" not "success"
)
```

**Test Case**:
```bash
# Upload 2-3 documents
# Click "Ingest Documents"
# Expected: "Successfully ingested 3 files (47 chunks)"
# Actual: "Successfully ingested undefined files (undefined chunks)"
```

---

## Architecture Issues

### Ingestion Blocking Login (FIXED ✅)

**Status**: ✅ Fixed  
**Fixed In**: Commit `935ab84d`

**Description**:
Ingestion was running synchronously and blocking the entire FastAPI event loop, causing all other requests (including login) to hang for 5-10 minutes.

**Fix**:
Moved ingestion to background thread using `ThreadPoolExecutor`. Ingestion now returns immediately and processes in background.

---

### Docker DNS Caching (DOCUMENTED ✅)

**Status**: 🟡 Mitigated  
**Mitigation**: Restart frontend container when backend restarts

**Description**:
Node.js caches DNS resolutions, so when backend container restarts and gets new IP, frontend continues using old cached IP.

**Fix Strategy**:
Implement Nginx internal proxy for all inter-service communication (documented in `docs/architecture/SERVICE_RESOLUTION_BEST_PRACTICES.md`).

---

## Minor Issues

### Chat Deletion Logs Out User

**Status**: 🟡 Low Priority  
**Severity**: Low  
**Priority**: P3

**Description**:
If user deletes the currently open chat, they get logged out instead of being redirected to home page.

**Fix**: Add proper error handling for 404 on active chat deletion.

---

### System Prompt Management Shows Default Instead of Current

**Status**: 🟡 Low Priority  
**Severity**: Low  
**Priority**: P3

**Description**:
System prompt management UI shows default prompts instead of current user-customized prompts. Edit prompt resets to default instead of editing existing prompt.

**Fix**: Update frontend to fetch current prompts, not defaults.

---

## Deployment

### Commands to Rebuild

```bash
# Rebuild and restart all services
cd /home/brad/cursor_code/EminiPlayer
docker compose -f docker-compose.graphmind.yml build
docker compose -f docker-compose.graphmind.yml up -d

# Restart specific service
docker compose -f docker-compose.graphmind.yml restart graphmind-rag
docker compose -f docker-compose.graphmind.yml restart graphmind-frontend

# View logs
docker logs graphmind-rag --tail 100 -f
docker logs graphmind-frontend --tail 100 -f
```

---

## Test Coverage

### Required Test Cases

1. **Large File Upload**
   - Upload 200MB video file
   - Verify progress tracking works
   - Verify upload completes successfully
   - Verify file appears in documents list

2. **Obsidian Configuration**
   - Navigate to Settings
   - Update Obsidian vault path
   - Click Save
   - Verify settings persist after page reload

3. **Document Ingestion**
   - Upload 3 documents
   - Click "Ingest Documents"
   - Verify success message shows actual numbers
   - Verify documents show chunk counts

4. **Background Ingestion**
   - Start ingestion
   - Attempt to login in another tab
   - Verify login works immediately (not blocked)

---

## Priority Order

1. **P0**: Large file upload (blocks core feature)
2. **P0**: Obsidian configuration save (blocks core feature)
3. **P1**: Ingestion undefined message (UX issue, workaround available)
4. **P2**: Docker DNS caching (documented, mitigation available)
5. **P3**: Minor UI issues (low impact)

---

**Last Updated**: 2025-10-25  
**Total Critical Defects**: 2  
**Total Medium Defects**: 1  
**Total Low Priority**: 2

