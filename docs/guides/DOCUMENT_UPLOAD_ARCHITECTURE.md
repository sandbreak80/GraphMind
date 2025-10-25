# Document Upload & Ingestion Architecture

## Overview

GraphMind uses a **separated upload/ingest workflow** for optimal user experience and performance. This architecture follows best practices for handling large files and batch processing.

## Architecture Pattern

### 1. Upload Phase (Fast)
```
User selects files → Upload to /workspace/documents → Show in UI as "Not ingested"
```
- **Fast**: Files are saved directly to filesystem
- **No processing**: Documents are not yet processed
- **Multiple files**: Can upload many files quickly
- **Large files**: Supports files up to 400MB

### 2. Ingestion Phase (Batch Processing)
```
User clicks "Ingest All" → Process all documents → Extract text → Chunk → Embed → Index
```
- **Batch operation**: All files processed together
- **Efficient**: Runs once for multiple files
- **Progress tracking**: User sees real-time status
- **Persistent**: Files remain even if ingestion fails

## Benefits

### ✅ Fast Upload UX
- Users can upload multiple files in seconds
- No waiting for processing
- Immediate feedback

### ✅ User Control
- Users decide when to process documents
- Can review uploads before ingesting
- Can delete unwanted files before processing

### ✅ Batch Efficiency
- Process multiple files together
- Better resource utilization
- Single embedding model load

### ✅ Reliable
- Files persist on disk
- Can retry ingestion if it fails
- No data loss on errors

## Technical Implementation

### Backend Endpoints

#### `POST /upload`
**Purpose:** Upload a single file to `/workspace/documents`

**Features:**
- Streaming upload for memory efficiency
- 400MB file size limit
- Duplicate filename handling
- Progress tracking

**Request:**
```bash
curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@document.pdf"
```

**Response:**
```json
{
  "success": true,
  "message": "Document uploaded successfully: document.pdf",
  "filename": "document.pdf",
  "size": 12345678,
  "path": "/workspace/documents/document.pdf"
}
```

#### `POST /ingest`
**Purpose:** Batch ingest all documents from `/workspace/documents`

**Features:**
- Processes all file types (PDF, Video, Word, Excel, etc.)
- Chunks documents
- Generates embeddings
- Indexes into ChromaDB
- Returns detailed statistics

**Request:**
```bash
curl -X POST http://localhost:8000/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force_reindex": false}'
```

**Response:**
```json
{
  "status": "success",
  "processed_files": 5,
  "total_chunks": 234,
  "failed_files": [],
  "message": "Ingestion complete. Processed 5 files, added 234 chunks. Failed: 0"
}
```

#### `POST /ingest-status`
**Purpose:** Get current ingestion status

**Response:**
```json
{
  "total_files": 10,
  "total_chunks": 450,
  "status": "ready"
}
```

#### `GET /documents`
**Purpose:** List all uploaded documents with ingestion status

**Response:**
```json
{
  "documents": [
    {
      "filename": "document.pdf",
      "doc_id": "document.pdf",
      "chunks": 23,
      "size": 12345678,
      "type": "pdf",
      "uploaded_at": "2025-01-01T12:00:00",
      "ingested": true
    },
    {
      "filename": "video.mp4",
      "doc_id": "video.mp4",
      "chunks": 0,
      "size": 98765432,
      "type": "video",
      "uploaded_at": "2025-01-01T12:05:00",
      "ingested": false
    }
  ]
}
```

#### `DELETE /documents/{doc_id}`
**Purpose:** Delete a document from both filesystem and ChromaDB

**Features:**
- Removes physical file from `/workspace/documents`
- Deletes all chunks from ChromaDB
- Returns deletion statistics

### Frontend Flow

```typescript
// 1. User selects files
const handleFileSelect = (event) => {
  setSelectedFiles(event.target.files)
}

// 2. Upload all files (fast)
const uploadDocuments = async () => {
  for (const file of selectedFiles) {
    const formData = new FormData()
    formData.append('file', file)
    await fetch('/api/documents/upload', {
      method: 'POST',
      body: formData
    })
  }
  loadDocuments() // Refresh list
}

// 3. Later: User clicks "Ingest All"
const ingestAllDocuments = async () => {
  await fetch('/api/documents/ingest', {
    method: 'POST',
    body: JSON.stringify({ force_reindex: false })
  })
  loadDocuments() // Refresh list with chunk counts
}
```

## UI/UX Features

### Upload Section
- Drag & drop support
- Multiple file selection
- Directory upload support (browser permitting)
- File size validation (400MB max)
- Progress bars for each file
- Success/failure indicators

### Ingestion Status Banner
- Shows total files and chunks
- Highlights unprocessed files
- "Ingest All" button when files need processing
- Real-time status updates

### Document List
- Shows all uploaded files
- "Not ingested" indicator for unprocessed files
- Chunk count for processed files
- File size and type
- Delete button

## Large File Support

### Configuration

#### Next.js (`frontend/next.config.js`)
```javascript
experimental: {
  largePageDataBytes: 400 * 1024 * 1024, // 400MB
}
```

#### Nginx (`nginx/nginx.conf`)
```nginx
client_max_body_size 400M;
client_body_buffer_size 128k;
client_body_timeout 300s;
proxy_connect_timeout 300s;
proxy_send_timeout 300s;
proxy_read_timeout 300s;
```

#### Backend (`app/main.py`)
```python
MAX_SIZE = 400 * 1024 * 1024  # 400MB

# Streaming upload
total_size = 0
with open(file_path, 'wb') as f:
    while chunk := await file.read(8192):  # 8KB chunks
        total_size += len(chunk)
        if total_size > MAX_SIZE:
            raise HTTPException(status_code=413, detail="File too large")
        f.write(chunk)
```

## Future Enhancements

### Multiple RAG Collections
**Plan:** Support multiple knowledge bases with collection management

```python
# Future API
POST /collections/create
  {"name": "finance_docs", "description": "Financial documents"}

POST /upload?collection=finance_docs
  Upload to specific collection

POST /ingest?collection=finance_docs
  Ingest into specific collection

GET /ask?collection=finance_docs
  Query specific collection
```

### File Watching (Optional)
**Not implemented yet** - Current manual workflow is more reliable

Could add automatic ingestion with watchdog:
```python
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class IngestOnUpload(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            # Auto-ingest new files
            ingest_file(event.src_path)
```

⚠️ **Trade-offs:**
- Pro: Automatic processing
- Con: Hard to show progress to user
- Con: Multiple rapid uploads trigger multiple ingestions
- Con: Race conditions possible

### Background Task Queue (Recommended for Scale)
**For future high-volume deployments:**

```python
# Using Celery or RQ
@celery.task
def ingest_document(file_path):
    # Process in background
    # Update progress in Redis
    # Send notifications when done

# API
POST /upload → Upload file → Queue ingestion task → Return immediately
GET /ingest/status/{task_id} → Check progress
```

## Best Practices

### For Users
1. **Upload first, review later**: Upload all files quickly
2. **Review before ingesting**: Check uploaded files are correct
3. **Ingest in batches**: Process multiple files at once
4. **Monitor progress**: Watch ingestion status
5. **Verify results**: Check chunk counts after ingestion

### For Developers
1. **Stream large files**: Use chunked reading
2. **Validate early**: Check file size before processing
3. **Handle duplicates**: Auto-rename or prompt user
4. **Clean up on errors**: Delete partial uploads
5. **Provide feedback**: Real-time progress indicators
6. **Separate concerns**: Upload ≠ Ingestion
7. **Make it idempotent**: Can re-run ingestion safely

## Error Handling

### Upload Errors
- **File too large (>400MB)**: HTTP 413 Payload Too Large
- **Disk full**: HTTP 507 Insufficient Storage
- **Invalid file type**: HTTP 415 Unsupported Media Type
- **Network timeout**: Retry with exponential backoff

### Ingestion Errors
- **Missing dependencies**: Log and skip file
- **Corrupt file**: Log and continue with next file
- **Embedding failure**: Retry with smaller chunks
- **ChromaDB error**: Rollback transaction

## Monitoring

### Metrics to Track
- Upload success rate
- Average upload time per MB
- Ingestion success rate
- Average processing time per file
- Storage utilization
- ChromaDB collection size

### Logs to Monitor
```
INFO: Uploaded document: large_video.mp4 (385.2 MB)
INFO: Starting batch ingestion (force_reindex=False)
INFO: Processing file: document.pdf with PDFProcessor
INFO: Added 23 chunks from document.pdf
INFO: Ingestion complete: 5 files, 234 chunks
```

## Testing

### Upload Test
```bash
# Test large file upload (generates 200MB file)
dd if=/dev/urandom of=large_file.bin bs=1M count=200

curl -X POST http://localhost:8000/upload \
  -H "Authorization: Bearer $TOKEN" \
  -F "file=@large_file.bin" \
  -o /dev/null -w "Time: %{time_total}s\n"
```

### Batch Ingestion Test
```bash
# Upload multiple files
for file in docs/*.pdf; do
  curl -X POST http://localhost:8000/upload \
    -H "Authorization: Bearer $TOKEN" \
    -F "file=@$file"
done

# Ingest all at once
curl -X POST http://localhost:8000/ingest \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"force_reindex": false}'
```

## Summary

✅ **Upload/Ingest Separation = Better UX**
- Fast uploads
- User control
- Batch efficiency
- Reliable processing

This architecture provides the best balance of speed, reliability, and user experience while laying the groundwork for future enhancements like multiple collections and background processing.

