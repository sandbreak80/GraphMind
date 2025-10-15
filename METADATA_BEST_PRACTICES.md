# Metadata Best Practices - Comprehensive Guide

## 🎯 Answer: "Do we need to add metadata to documents before ingestion?"

### ✅ **NO manual prep needed!** The system auto-extracts metadata.

However, understanding what metadata helps will let you optimize your folder structure and file naming.

---

## 🔄 What the System Auto-Extracts

### 1. **From File System** (Automatic)
```python
✅ File name: "momentum_strategy.pdf"
✅ File path: "ProTrader/strategies/momentum_strategy.pdf"
✅ Folder structure: "ProTrader/strategies"
✅ File extension: ".pdf"
✅ Creation date: From file system
✅ Modified date: From file system
✅ Ingestion timestamp: "2025-10-14T22:15:30Z"
```

### 2. **From Content** (AI-Powered)
```python
✅ Keywords: ["momentum", "breakout", "volume", "entry", "confirmation"]
   - Extracted using frequency analysis
   - Removes stop words
   - Top 5 most relevant terms

✅ Content type: "text" / "table" / "spreadsheet" / "video_transcript" / "video_frame"
   - Auto-detected based on source

✅ Extraction method: "docling" / "ocr" / "whisper" / "pandas"
   - Tracks how content was extracted
   - Useful for quality assessment
```

### 3. **From Video Processing**
```python
✅ Timestamps: start/end for each segment
✅ OCR text: Visible tickers, indicators, prices
✅ Trading terms: Auto-detected (ES, NQ, VWAP, RSI, etc.)
✅ Frame path: Link to extracted keyframe image
✅ Speech segments: Natural pause boundaries
```

### 4. **From Document Structure**
```python
✅ Page numbers: From PDF/Word structure
✅ Section titles: From headings
✅ Table detection: Separate chunks for tables
✅ Heading hierarchy: Breadcrumb trail
```

---

## 📝 Optional: Improve Your Folder Structure

### Current Structure (Good!)
```
/path/to/your/documents/
├── BootCamp/
│   ├── 31st Jan/
│   │   ├── Mid.mp4
│   │   └── Prep.mp4
│   └── Notes.docx
└── ProTrader/
    ├── 1.Your Market FW/
    │   └── Part 1/
    │       ├── Contextual_Market_Reading_Abilities_Part1_KeyTakeaways.pdf
    │       └── ...
    └── 2.TradingFW/
        └── Part2/
            └── Position_Sizing.xlsx
```

**What works well:**
- ✅ Folders by topic (BootCamp, ProTrader)
- ✅ Date-based subfolders for videos
- ✅ Descriptive filenames

### Optional Enhancements (Not Required!)

**Add topic tags to filenames** (if you want):
```
Before: Contextual_Market_Reading_Abilities_Part1_KeyTakeaways.pdf
After:  [MarketAnalysis] Contextual_Market_Reading_Abilities_Part1_KeyTakeaways.pdf

Before: Mid.mp4
After:  [Momentum-Trading] 2024-01-31_Mid.mp4
```

**Benefits**:
- Easier to filter by topic
- Better keyword extraction
- Clearer citations

**BUT**: Your current structure is fine! The system extracts keywords from content anyway.

---

## 🎨 Best Practices for Future Documents

### 1. **Descriptive Filenames** ✅ (You already do this!)
```
Good: "Momentum_Breakout_Strategy_Guide.pdf"
Bad:  "Document1.pdf", "Final_v3.pdf"
```

### 2. **Consistent Folder Structure** ✅ (You already have!)
```
Strategies/
├── Momentum/
├── Reversal/
└── Range/

BootCamp/
├── {Date}/
    ├── Prep.mp4
    ├── Mid.mp4
    └── After.mp4
```

### 3. **Use Descriptive Section Headings** ✅
```markdown
Good:
# Momentum Breakout Strategy
## Entry Rules
## Exit Rules
## Risk Management

Bad:
# Strategy
## Rules
## Other
```

### 4. **Keep Related Files Together**
```
Momentum_Strategy/
├── Momentum_Strategy_Guide.pdf
├── Momentum_Strategy_Drills.pdf
├── Momentum_Strategy_AnswerKey.pdf
└── Momentum_BootCamp_Examples.mp4
```

---

## 🚀 Advanced: Pre-Processing Scripts (Optional)

### If You Want to Add Custom Metadata

**Option 1: Filename Tags**
```bash
# Add tags to filenames
rename 's/^/[Strategy] /' ProTrader/strategies/*.pdf
rename 's/^/[Drill] /' ProTrader/drills/*.pdf
```

**Option 2: Create .metadata.json Files**
```json
// momentum_strategy.metadata.json
{
  "title": "Momentum Breakout Strategy",
  "category": "trading_strategy",
  "difficulty": "intermediate",
  "prerequisites": ["market_structure", "volume_analysis"],
  "related_files": ["momentum_drills.pdf", "momentum_answer_key.pdf"],
  "keywords": ["momentum", "breakout", "volume", "trend"],
  "summary": "Comprehensive guide to momentum breakout trading with volume confirmation"
}
```

Then modify ingest to read these:
```python
metadata_file = pdf_path.with_suffix('.metadata.json')
if metadata_file.exists():
    custom_metadata = json.loads(metadata_file.read_text())
    chunk.update(custom_metadata)
```

**But again: NOT NECESSARY!** The system extracts keywords automatically.

---

## 📊 Metadata Schema Currently Stored

### Complete Metadata Structure

```python
{
    // ALWAYS PRESENT
    "doc_id": str,                    # Document identifier
    "chunk_id": str,                  # Unique chunk identifier
    "page": int,                      # Page number (0 for videos/Excel)
    "section": str,                   # Section title or heading
    "content_type": str,              # text, table, spreadsheet, video_transcript, video_frame
    "extraction_method": str,         # docling, ocr, pymupdf, whisper, pandas
    "keywords": str,                  # "momentum, breakout, volume, entry"
    "ingested_at": str,               # ISO timestamp
    
    // FOR VIDEOS ONLY
    "media_type": str,                # video_transcript or video_frame
    "timestamp_start": float,         # Seconds from start
    "timestamp_end": float,           # Seconds from start
    "frame_path": str,                # Path to extracted frame image (if video_frame)
    
    // FOR EXCEL ONLY
    "has_formulas": bool,             # Contains Excel formulas
    "has_comments": bool,             # Contains cell comments
}
```

### Queryable Fields

All these fields can be used for filtering:
```python
# Filter by content type
where={"content_type": "table"}

# Filter by extraction quality
where={"extraction_method": "docling"}  # High quality

# Filter by keywords
where={"keywords": {"$contains": "momentum"}}

# Filter by media type
where={"media_type": "video_transcript"}

# Filter by timestamp range
where={
    "timestamp_start": {"$gte": 900},    # After 15 minutes
    "timestamp_end": {"$lte": 1800}      # Before 30 minutes
}
```

---

## 🎯 Recommendations Summary

### ✅ What You Already Have (Perfect!)
1. **Auto keyword extraction** - No manual tagging needed
2. **Content type classification** - Auto-detected
3. **Structure preservation** - Headings, sections, pages
4. **Video OCR** - Extracts visible chart text
5. **Table extraction** - Separate chunks for tables
6. **Timestamps** - Full tracking of when/what

### 🎁 Optional Future Enhancements
1. **Document type inference** - Auto-categorize by folder
2. **AI summaries** - One sentence per chunk
3. **Related doc linking** - Connect drills to answer keys
4. **Custom metadata files** - If you need specific tags

### 🚫 What You DON'T Need to Do
- ❌ Manually tag files with keywords
- ❌ Rename files (current names are good)
- ❌ Reorganize folders (structure is fine)
- ❌ Create metadata files
- ❌ Pre-process documents

---

## 💡 If You Want Even Better Results (5-Minute Add)

Add this to `app/ingest.py` to infer document types from your folder structure:

```python
def _infer_doc_type_from_path(self, file_path: Path) -> str:
    """Infer document type from path."""
    path_str = str(file_path).lower()
    name_str = file_path.name.lower()
    
    # From folder structure
    if "bootcamp" in path_str:
        if file_path.suffix in ['.mp4', '.webm']:
            return "bootcamp_video"
        return "bootcamp_notes"
    
    if "protrader" in path_str:
        if "market fw" in path_str:
            return "market_framework"
        if "tradingfw" in path_str:
            return "trading_framework"
    
    # From filename patterns
    if "drill" in name_str:
        return "practice_drill"
    if "answerkey" in name_str or "answer_key" in name_str:
        return "answer_key"
    if "keytakeaways" in name_str or "key_takeaways" in name_str:
        return "key_takeaways"
    if "cheat" in name_str or "sheet" in name_str:
        return "cheat_sheet"
    if file_path.suffix in ['.xlsx', '.xls']:
        return "calculator"
    
    return "guide"
```

Then add to metadata:
```python
metadata["doc_type"] = self._infer_doc_type_from_path(file_path)
```

**Benefit**: Filter queries by document type (drills vs guides vs videos)

Want me to add this now? It's a 2-minute change!

---

## 🎉 Current Status

**Your ingestion is running with:**
- ✅ 94 files being processed
- ✅ Enhanced metadata (keywords, content types, timestamps)
- ✅ Table extraction from PDFs
- ✅ OCR on video frames
- ✅ 90-95% recall configuration

**Current progress**: Processing PDFs done, now on first video (Mid.mp4)

**Time remaining**: ~3-4 hours for 23 videos

**Monitor with**:
```bash
docker compose logs -f | grep -E "✓|Transcribing|Extracted"
```
