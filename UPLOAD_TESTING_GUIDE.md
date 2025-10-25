# Document Upload Testing Guide

## Quick Start

### 1. Restart Services
```bash
cd /home/brad/cursor_code/EminiPlayer
docker compose -f docker-compose.graphmind.yml up -d
```

### 2. Check Backend is Ready
```bash
# Wait for "Application startup complete"
docker logs graphmind-rag --tail 50 -f
```

### 3. Access Document Management
Open: https://graphmind.riffyx.com/documents

## Testing Workflow

### Test 1: Single File Upload
1. Click "Documents" in sidebar
2. Click upload area or drag a file
3. Select 1 PDF file (< 400MB)
4. Click "Upload 1 File"
5. ✅ Should complete in seconds
6. ✅ File shows with "Not ingested" badge

### Test 2: Multiple File Upload
1. Click upload area
2. Select 5-10 files (various types: PDF, Word, Excel)
3. See selected files list
4. Click "Upload 10 Files"
5. ✅ Progress bars for each file
6. ✅ All files upload quickly
7. ✅ All show "Not ingested"

### Test 3: Batch Ingestion
1. After uploading files
2. See banner: "X files uploaded • 0 chunks indexed • X unprocessed"
3. Click "Ingest X Files" button
4. ✅ See "Processing documents..." toast
5. ✅ Wait 10-30 seconds (depending on file count)
6. ✅ See success: "Successfully ingested X files (Y chunks)"
7. ✅ Files now show chunk counts (e.g., "23 chunks")
8. ✅ "Not ingested" badges gone

### Test 4: Large File Upload
1. Create or find a large file (100-350MB)
   ```bash
   # Create 200MB test file
   dd if=/dev/urandom of=large_test.bin bs=1M count=200
   ```
2. Upload the file
3. ✅ Should upload successfully
4. ✅ Progress bar shows upload
5. ✅ No timeout errors

### Test 5: File Too Large
1. Try to upload a file > 400MB
2. ✅ Should reject with error
3. ✅ No partial file saved

### Test 6: Delete Document
1. Click trash icon on a document
2. Confirm deletion
3. ✅ File removed from list
4. ✅ Chunks removed from ChromaDB
5. ✅ File deleted from filesystem

### Test 7: Refresh & Persistence
1. Upload some files
2. Don't ingest yet
3. Refresh the page
4. ✅ Files still show in list
5. ✅ Still marked "Not ingested"
6. Now click "Ingest All"
7. ✅ Files process successfully

## Expected Behavior

### Upload Phase (FAST)
- Multiple files upload in parallel
- Each file shows progress bar
- Takes seconds, not minutes
- Files persist to `/workspace/documents`
- No processing happens yet

### Ingestion Phase (SLOWER)
- Batch processes all files at once
- Shows "Processing documents..." message
- Takes 10-30 seconds depending on:
  - Number of files
  - File sizes
  - File types (video is slowest)
- Updates chunk counts when done

## Troubleshooting

### Upload Fails Immediately
```bash
# Check backend logs
docker logs graphmind-rag --tail 100

# Check disk space
df -h /workspace/documents
```

### Ingestion Fails
```bash
# Check ChromaDB
docker logs chromadb --tail 50

# Check for file processing errors
docker logs graphmind-rag | grep "ERROR"
```

### Files Don't Show Up
```bash
# Check if files actually saved
docker exec graphmind-rag ls -lh /workspace/documents/

# Check frontend logs
docker logs graphmind-frontend --tail 50
```

### "Not Ingested" Badge Doesn't Clear
```bash
# Manually check ChromaDB collection
docker exec graphmind-rag python3 -c "
import chromadb
client = chromadb.HttpClient(host='chromadb', port=8000)
collection = client.get_collection('documents')
print(f'Total chunks: {collection.count()}')
"
```

## Manual API Testing

### Upload via curl
```bash
# Get auth token first
TOKEN=$(curl -X POST https://graphmind.riffyx.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  | jq -r '.access_token')

# Upload file
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.pdf"
```

### Trigger Ingestion via curl
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force_reindex": false}'
```

### Check Ingestion Status
```bash
curl -X POST http://localhost:8000/ingest-status \
  -H "Authorization: Bearer $TOKEN"
```

### List Documents
```bash
curl http://localhost:8000/documents \
  -H "Authorization: Bearer $TOKEN"
```

## Performance Benchmarks

### Good Performance
- Upload 10 x 5MB files: **< 10 seconds**
- Upload 1 x 200MB file: **< 30 seconds**
- Ingest 10 PDFs (100 pages each): **20-40 seconds**
- Ingest 1 video (30 min): **60-120 seconds**

### Warning Signs
- Upload taking > 1 minute: Check network/disk
- Ingestion taking > 5 minutes: Check embedding model
- Files not appearing: Check permissions
- Chunks = 0 after ingestion: Check file processing

## File Type Support

| Type | Extension | Upload | Ingest | Notes |
|------|-----------|--------|--------|-------|
| PDF | `.pdf` | ✅ | ✅ | Uses Docling + OCR |
| Word | `.docx` | ✅ | ✅ | Fast |
| Excel | `.xlsx` | ✅ | ✅ | Extracts text from cells |
| PowerPoint | `.pptx` | ✅ | ✅ | Extracts slide text |
| Text | `.txt`, `.md` | ✅ | ✅ | Very fast |
| Video | `.mp4`, `.avi`, `.mov` | ✅ | ✅ | Slow (uses Whisper) |
| Images | `.jpg`, `.png` | ✅ | ✅ | Uses OCR |

## Next Steps

### For Single User
Current setup works great!
- Fast uploads
- Batch ingestion
- Good UX

### For Multiple Collections (Future)
When you want separate knowledge bases:
```bash
# Upload to specific collection
POST /upload?collection=finance_docs

# Ingest specific collection
POST /ingest?collection=finance_docs

# Query specific collection
POST /ask?collection=finance_docs
```

### For High Volume (Future)
When processing 100+ files daily:
- Add background task queue (Celery/RQ)
- Add progress streaming
- Add file watching (optional)
- Add webhook notifications

## Quick Verification

After deployment, run this quick check:

```bash
# 1. Upload test file
echo "Test document content" > test.txt
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@test.txt"

# 2. Check it appears
curl http://localhost:8000/documents \
  -H "Authorization: Bearer $TOKEN" \
  | jq '.documents[] | select(.filename=="test.txt")'

# 3. Ingest it
curl -X POST http://localhost:8000/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force_reindex": false}'

# 4. Verify chunks created
curl -X POST http://localhost:8000/ingest-status \
  -H "Authorization: Bearer $TOKEN"

# Should show:
# {
#   "total_files": 1,
#   "total_chunks": > 0,
#   "status": "ready"
# }
```

✅ If all steps pass, upload system is working!

## UI Features

### Status Banner
- Shows: Files uploaded, chunks indexed, unprocessed count
- Appears: At top of documents page
- Action: Click "Ingest X Files" button

### Upload Progress
- Individual progress bars per file
- Green checkmark on success
- Red X on failure
- Shows file name and size

### Document List
- File icon (based on type)
- Filename
- Size
- Chunk count (or "Not ingested")
- Type
- Delete button

## Support

If issues persist:
1. Check logs: `docker logs graphmind-rag`
2. Verify disk space: `df -h`
3. Test API directly: See "Manual API Testing" above
4. Check ChromaDB: `docker logs chromadb`
5. Restart services: `docker compose -f docker-compose.graphmind.yml restart`

