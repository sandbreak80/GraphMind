# Multi-Format Ingestion Guide

## Supported Formats

The EminiPlayer RAG service now supports **comprehensive knowledge extraction** from multiple file types:

### 📄 Documents
- **PDF** (68 files): Full text extraction with Docling + OCR fallback
- **Word** (1 file): Text, tables, headings, formatting preserved
- **Excel** (2 files): Data, formulas, comments, multi-sheet support
- **Text** (1 file): Plain text chunking

### 🎥 Videos
- **MP4** (14 files): Audio transcription + visual frame analysis
- **WEBM** (9 files): Audio transcription + visual frame analysis

**Total: 97 files, ~3.8GB of trading knowledge**

---

## 📊 What Gets Extracted

### PDFs
1. **Text content** with structure preservation (headings, sections)
2. **Tables** formatted as text
3. **Images** (OCR applied if scanned)
4. **Page numbers** and section titles
5. **Metadata** (document ID, page, section)

### Videos (🎯 Critical for BootCamp Sessions)
1. **Full audio transcription** with timestamps
   - Whisper GPU-accelerated transcription
   - Segmented by natural speech pauses
   - Searchable by timestamp

2. **Visual frame analysis**
   - Keyframes extracted every 30 seconds (configurable)
   - Saved as JPG images for reference
   - Basic content detection (charts, text regions)
   - Frame descriptions indexed for search

3. **Outputs**:
   - `{video_name}_transcript.txt` - Full transcript with timestamps
   - `frames/{video_name}_frame_XXs.jpg` - Extracted keyframes
   - Searchable chunks in vector database

**Example:** For "BootCamp/31st Jan/Mid.mp4" (154MB):
- Transcript chunk: `[00:05:23 - 00:05:47] The key is to identify the momentum shift before the breakout occurs...`
- Frame chunk: `Video frame at 00:05:30 shows charts with high edge density (trading setup visualization)`

### Excel Spreadsheets
1. **All sheets** processed separately
2. **Data** formatted as tables
3. **Formulas** extracted (e.g., `B10: =SUM(B2:B9)`)
4. **Cell comments** preserved
5. **Metadata** (sheet names, cell references)

**Example:** "Position_Sizing.xlsx" might contain:
- Sheet 1: "Risk Calculator" with formulas
- Sheet 2: "Historical Results" with data
- Comments explaining calculation logic

### Word Documents
1. **Structured text** (headings, paragraphs)
2. **Tables** extracted and formatted
3. **Formatting context** (heading levels)
4. **Sections** tracked for citations

---

## 🚀 Ingestion Process

### 1. Automatic Detection
```python
# System automatically routes files by extension:
.pdf      → Docling + OCR fallback → PyMuPDF
.mp4/webm → Whisper transcription → Frame extraction
.xlsx/xls → Pandas + OpenPyXL (data + formulas)
.docx/doc → python-docx (structure-aware)
.txt      → Direct text chunking
```

### 2. Processing Pipeline

**Videos** (most intensive):
```
MP4/WEBM → Audio Extraction → Whisper (GPU) → Timestamped Transcript
                            ↓
                    Frame Extraction → Every 30s → Visual Analysis → Keyframes
                            ↓
                    Chunking → Index to Chroma
```

**Documents**:
```
Excel/Word/PDF → Content Extraction → Structure Preservation → Chunking → Index
```

### 3. Chunking Strategy

| Format | Strategy | Chunk Size | Special Handling |
|--------|----------|------------|------------------|
| PDF | Structure-aware | 800 chars | Preserves headings, sections |
| Video Transcript | Timestamp-based | Per segment | Natural speech boundaries |
| Video Frames | Per frame | N/A | One chunk per keyframe |
| Excel | Per sheet | N/A | Formulas + data combined |
| Word | Paragraph-aware | 400 words | Heading context preserved |
| Text | Simple sliding | 400 words | Basic overlap |

---

## ⚙️ Configuration

### Environment Variables (docker-compose.yml)

```yaml
environment:
  # Video Processing
  - VIDEO_FRAME_INTERVAL=30        # Extract frame every N seconds
  - WHISPER_MODEL_SIZE=base        # tiny, base, small, medium, large
  
  # Existing settings
  - OLLAMA_BASE_URL=http://host.docker.internal:11434
  - OLLAMA_MODEL=llama3.1
  - CUDA_VISIBLE_DEVICES=0
```

### Whisper Model Sizes

| Model | Speed | Accuracy | VRAM | Use Case |
|-------|-------|----------|------|----------|
| tiny | Fastest | Good | ~1GB | Quick testing |
| base | Fast | Better | ~1GB | **Default - Balanced** |
| small | Medium | Great | ~2GB | Better accuracy |
| medium | Slower | Excellent | ~5GB | High accuracy needed |
| large | Slowest | Best | ~10GB | Professional transcription |

### Frame Extraction Frequency

- **30 seconds** (default): Good balance, ~120 frames for 1-hour video
- **15 seconds**: More frames, better coverage, 2x processing time
- **60 seconds**: Fewer frames, faster processing, key moments only

---

## 📈 Performance Expectations

### Processing Times (approximate)

| File Type | Size | Time | Output |
|-----------|------|------|--------|
| PDF (simple) | 10 pages | 5-10s | ~50 chunks |
| PDF (scanned) | 10 pages | 30-60s | ~50 chunks (with OCR) |
| Video (MP4) | 150MB, 30min | 5-10 min | ~60 transcript chunks + 60 frames |
| Excel | 2 sheets | 2-5s | ~2-10 chunks |
| Word | 10 pages | 5-10s | ~30-50 chunks |

**Total for your 97 files**: 
- First run: 3-4 hours (includes Whisper model download, 23 videos)
- Subsequent reruns: Similar (video transcription is compute-intensive)
- Without videos: ~30-45 minutes

### Resource Usage

| Resource | Idle | Ingesting PDFs | Transcribing Video |
|----------|------|----------------|---------------------|
| GPU Memory | ~2GB | ~4-6GB | ~6-8GB |
| RAM | ~4GB | ~8-12GB | ~10-16GB |
| CPU | Low | Medium | Medium-High |
| Disk I/O | Low | Medium | High |

---

## 🎯 Querying Multi-Format Content

### Example Queries

**Video Content**:
```bash
curl -X POST http://localhost:8000/ask \
  -d '{
    "query": "What did the instructor say about momentum trading in the BootCamp videos?",
    "mode": "qa",
    "top_k": 10
  }'
```

**Excel Data**:
```bash
curl -X POST http://localhost:8000/ask \
  -d '{
    "query": "What position sizing formulas are used?",
    "mode": "qa",
    "top_k": 5
  }'
```

**Cross-Format**:
```bash
curl -X POST http://localhost:8000/ask \
  -d '{
    "query": "Extract a complete trading strategy combining the PDF rules and BootCamp examples",
    "mode": "spec",
    "top_k": 15
  }'
```

### Citations Include

- **PDFs**: `doc_id`, `page`, `section`
- **Videos**: `doc_id`, `timestamp_start`, `timestamp_end`, `section: "Video @ HH:MM:SS"`
- **Excel**: `doc_id`, `section` (sheet name)
- **Word**: `doc_id`, `section` (heading)

---

## 📁 Output Files

After ingestion, check `./outputs/`:

```
outputs/
├── {pdf_name}.md                           # Docling markdown export
├── {video_name}_transcript.txt             # Full transcripts
├── {video_name}_frame_XXs.jpg              # Keyframes (in frames/)
├── strategy_spec_*.yaml                    # Extracted specs
└── frames/
    ├── Mid_frame_30s.jpg
    ├── Mid_frame_60s.jpg
    └── ...
```

---

## 🔍 Advanced: Video Frame Analysis

### What's Detected

Current implementation:
- **Chart presence** (high edge density detection)
- **Text regions** (contour analysis)
- **Visual complexity** (content density)

### Future Enhancements (Optional)

Add these for deeper visual understanding:

1. **OCR on frames** - Extract visible text, indicators, labels
   ```python
   import pytesseract
   text = pytesseract.image_to_string(frame)
   ```

2. **CLIP embeddings** - Semantic understanding of what's shown
   ```python
   from transformers import CLIPProcessor, CLIPModel
   # Detect "candlestick chart", "support level", etc.
   ```

3. **Object detection** - Identify specific chart patterns
   - YOLOv8 trained on trading chart patterns
   - Detect: "double top", "head and shoulders", etc.

---

## 🛠️ Troubleshooting

### "Video transcription is slow"
- **Solution 1**: Reduce `WHISPER_MODEL_SIZE` to `tiny`
- **Solution 2**: Increase `VIDEO_FRAME_INTERVAL` to 60
- **Solution 3**: Set `extract_frames=False` in code (transcription only)

### "Out of GPU memory"
- **Solution**: Process videos sequentially (already done)
- Check: `nvidia-smi` - should show ~6-8GB max
- If needed: Reduce `WHISPER_MODEL_SIZE`

### "Failed to process {video}.mp4"
- Check video codec: `ffmpeg -i video.mp4`
- Re-encode if needed: `ffmpeg -i input.mp4 -c:v libx264 -c:a aac output.mp4`

### "Excel formulas not extracted"
- Temporary files (~$) are auto-skipped
- Check file isn't corrupted: Open in Excel/LibreOffice
- May need: `pip install openpyxl --upgrade`

---

## 📊 Monitoring Ingestion

Watch the logs for detailed progress:

```bash
docker-compose logs -f | grep -E "✓|✗|⚠|Found|Transcribing"
```

Expected output:
```
INFO: Found 97 files across all supported formats
INFO: File breakdown: {'pdf': 68, 'mp4': 14, 'webm': 9, 'xlsx': 2, 'docx': 1, 'txt': 1}
INFO: Loaded Whisper base model on GPU
INFO: Transcribing Mid.mp4...
INFO: Detected language: en (0.98)
INFO: Extracting keyframes from Mid.mp4...
INFO: Extracted 60 keyframes from Mid.mp4
INFO: Saved transcript to /workspace/outputs/Mid_transcript.txt
INFO: ✓ Mid.mp4: 120 chunks
INFO: ✓ System_Cheat_Sheets.pdf: 45 chunks
INFO: ✓ Position_Sizing.xlsx: 8 chunks
...
```

---

## 🎓 Best Practices

1. **First ingestion**: Use `force_reindex: false`, monitor logs
2. **Video-heavy**: Expect 3-4 hours for initial run with 23 videos
3. **Test queries**: Start with simple QA before spec extraction
4. **Check outputs**: Review transcripts and frames in `./outputs/`
5. **Iterate**: If transcription quality is poor, increase model size
6. **Citations**: Video timestamps allow you to jump to exact moments

---

## 🚀 Quick Start for Your Data

```bash
# 1. Ensure Ollama is running
ollama pull llama3.1

# 2. Build with new dependencies
docker-compose build

# 3. Start service
docker-compose up -d

# 4. Ingest ALL files (PDFs, Videos, Excel, Word, Text)
make ingest

# 5. Monitor progress (will take 3-4 hours for 23 videos)
docker-compose logs -f

# 6. Check outputs
ls -lh outputs/
ls -lh outputs/frames/

# 7. Query across all formats
make test-query

# 8. Extract strategy using all sources
curl -X POST http://localhost:8000/ask \
  -d '{"query": "Extract momentum breakout strategy from all sources", "mode": "spec", "top_k": 20}'
```

Your **1000+ pages of trading knowledge** are now fully searchable! 🎉
