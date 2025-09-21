# C.H.R.I.S.T. Data Ingestion Guide

## Quick Start - Ingest Your Data

### Step 1: Prepare Your Data
Organize your data in a folder structure. The system will recursively scan all subdirectories.

### Step 2: Run Ingestion

```bash
# Activate environment
source venv/bin/activate  # or source ../venv/bin/activate

# Dry run - see what will be processed
python ingest_my_data.py /path/to/your/data --dry-run

# Full ingestion
python ingest_my_data.py /path/to/your/data

# Faster ingestion without encryption
python ingest_my_data.py /path/to/your/data --no-encryption
```

## Currently Supported File Types

### ✅ Fully Supported
- **Text**: `.txt`, `.md`, `.markdown`, `.rst`, `.log`
- **Code**: `.py`, `.js`, `.java`, `.cpp`, `.html`, `.css`
- **Data**: `.json`, `.xml`, `.yaml`, `.yml`
- **Email**: `.eml`, `.mbox`
- **Chat exports**: WhatsApp `.txt`, Discord `.json`

### 🚧 Coming Soon
- **Documents**: `.pdf`, `.doc`, `.docx` (need to install: `pip install PyPDF2 python-docx`)
- **Images**: `.jpg`, `.png` (need: `pip install pillow pytesseract` for OCR)
- **Audio**: `.mp3`, `.wav` (need: `pip install whisper` for transcription)
- **Video**: `.mp4`, `.avi` (frame extraction + OCR)

## Handling Different Data Types

### Personal Documents
```bash
python ingest_my_data.py ~/Documents --consent full
```

### Email Archives
Export your emails as `.mbox` or `.eml` files:
- Gmail: Takeout → Download as MBOX
- Outlook: Export → Save as EML
```bash
python ingest_my_data.py ~/EmailArchive
```

### Chat History
- WhatsApp: Export chat (without media) → `.txt` file
- Discord: Use DiscordChatExporter → `.json` file
- Telegram: Export as JSON
```bash
python ingest_my_data.py ~/ChatExports
```

### Code Repositories
```bash
python ingest_my_data.py ~/Projects --no-encryption
```

### Mixed Media Collection
```bash
# First pass - text only
python ingest_my_data.py ~/PersonalArchive

# Later - when image support is ready
python ingest_my_data.py ~/PersonalArchive --process-images
```

## Privacy Levels

Choose your comfort level:

```bash
# Full capture (default)
python ingest_my_data.py /data --consent full

# Only metadata, no content
python ingest_my_data.py /data --consent metadata_only

# Anonymized content
python ingest_my_data.py /data --consent anonymized

# No capture (test run)
python ingest_my_data.py /data --consent none
```

## Performance Tips

### For Large Archives (>10GB)

1. **Start with a subset**:
```bash
python ingest_my_data.py ~/Archive/2024 --batch-size 100
```

2. **Disable encryption for speed**:
```bash
python ingest_my_data.py ~/Archive --no-encryption
```

3. **Process in batches**:
```bash
# Year by year
for year in 2020 2021 2022 2023 2024; do
    python ingest_my_data.py ~/Archive/$year
done
```

## Adding PDF Support

To enable PDF processing:

```bash
pip install PyPDF2 pdfplumber

# Then in parsers.py, add:
import PyPDF2
import pdfplumber
```

## Adding Image Support (OCR)

To extract text from images:

```bash
# Install Tesseract OCR
sudo apt-get install tesseract-ocr  # Linux
brew install tesseract              # Mac

# Install Python packages
pip install pytesseract pillow

# Then the system can extract text from images
```

## Adding Audio Transcription

To transcribe audio files:

```bash
pip install openai-whisper

# Or for faster, local transcription:
pip install faster-whisper
```

## Monitoring Progress

The ingestion script shows progress every 10 files (configurable):

```
[156/1847] Processing: Documents/notes/consciousness.txt
  ✅ Ingested as a4f3e8b2...

📈 Progress: 160/1847 files processed
   ✅ Success: 145
   ⏭️ Skipped: 10
   ❌ Errors: 5
```

## After Ingestion

Once your data is ingested:

### 1. Search Your Consciousness
```bash
python cli.py query
> "memories from childhood"
> "thoughts about AI"
> "project ideas from 2023"
```

### 2. Chat with Your Data
```bash
python cli.py chat
> "What did I think about consciousness in my journal entries?"
> "Summarize my email conversations about the project"
```

### 3. Visualize Your Mind
```bash
python web_app.py
# Open http://localhost:8000
```

### 4. Query with RAG
```bash
python demo_rag.py
# AI-powered answers from your consciousness data
```

## Best Practices

1. **Start Small**: Test with a small folder first
2. **Organize**: Group similar content in folders
3. **Clean**: Remove duplicates and junk files
4. **Privacy**: Use appropriate consent levels
5. **Backup**: Keep original files - ingestion is non-destructive

## Troubleshooting

### "Too many files" error
- Process in smaller batches
- Increase system limits: `ulimit -n 4096`

### "Memory error"
- Use `--batch-size 1` for very large files
- Disable encryption: `--no-encryption`

### "Permission denied"
- Check file permissions
- Run as user who owns the files

### Slow ingestion
- Disable encryption for speed
- Skip images/videos initially
- Use SSD storage for database

## Future Capabilities

Coming soon:
- 🖼️ Image memory extraction (photos → memories)
- 🎵 Audio transcription (voice notes → text)
- 🎥 Video processing (videos → key frames + transcripts)
- 📧 Email threading and conversation reconstruction
- 💬 Chat sentiment and relationship analysis
- 🧠 Dream journal analysis
- 📊 Temporal pattern detection
- 🔗 Knowledge graph generation

## Data Safety

- Original files are NEVER modified
- All data is stored encrypted (unless disabled)
- Database can be backed up/exported
- You maintain full control

---

Ready to capture your consciousness? Start with:
```bash
python ingest_my_data.py ~/YourDataFolder --dry-run
```