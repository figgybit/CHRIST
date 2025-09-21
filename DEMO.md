# C.H.R.I.S.T. System - Demo Guide

## Quick Start Demo

### 1. Clean Demo Setup (Recommended)

Run the clean demo script to remove test artifacts and load fresh sample data:

```bash
# Activate virtual environment
source venv/bin/activate  # or source ../venv/bin/activate

# Run clean demo setup
python demo_clean.py
```

This will:
- Clean up any test data from previous runs
- Create fresh sample data (journal, philosophy notes, AI conversation)
- Load data into the system with proper embeddings
- Run demo queries to verify everything works

### 2. Interactive Demos

After running the clean setup, try these demos:

#### A. Query Mode (Search Consciousness Data)
```bash
python cli.py query
```
Sample queries to try:
- "consciousness and awareness"
- "meditation experiences"
- "AI consciousness"
- "Buddhist philosophy"
- "hard problem of consciousness"

#### B. Chat Mode (RAG-powered Conversation)
```bash
python cli.py chat
```
Ask questions like:
- "What are my thoughts on consciousness?"
- "How do I view the relationship between AI and human consciousness?"
- "What insights have I had during meditation?"
- "Explain the Buddhist perspective on consciousness from my notes"

#### C. Web Interface
```bash
python web_app.py
```
Open browser to: http://localhost:8000

Features:
- Dashboard with system stats
- Search interface with visual results
- Chat interface for RAG interactions
- Data ingestion page
- Beautiful, responsive UI

### 3. API Demo

Start the API server:
```bash
python api_server.py
```

Test endpoints:
```bash
# Check API health
curl http://localhost:8001/health

# Search for consciousness-related content
curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{"query": "consciousness", "k": 5}'

# Chat with RAG
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is consciousness according to my notes?"}'
```

## Sample Data Overview

The demo includes three types of sample data:

1. **Personal Journal** (`journal_2025.txt`)
   - Personal reflections on consciousness
   - Meditation experiences
   - Project thoughts

2. **Philosophy Notes** (`consciousness_notes.md`)
   - Hard problem of consciousness
   - Integrated Information Theory
   - Buddhist perspectives
   - Digital consciousness

3. **AI Conversation** (`ai_conversation.json`)
   - Discussion about AI consciousness
   - Different forms of awareness
   - Substrate independence

## Common Issues & Solutions

### Issue: Duplicate embeddings warning
**Solution:** Run `python demo_clean.py` to clear test data

### Issue: No LLM configured
**Solution:**
1. Set OpenAI API key: `export OPENAI_API_KEY=your_key`
2. Or use mock mode (already configured for demos)

### Issue: ChromaDB not installed
**Solution:** System falls back to numpy-based search automatically

### Issue: Web interface not loading
**Solution:** Make sure port 8000 is free: `lsof -i :8000`

## Advanced Demos

### 1. Ingest Your Own Data
```bash
# Ingest a single file
python cli.py ingest /path/to/your/file.txt

# Ingest a directory
python cli.py ingest /path/to/directory --recursive
```

### 2. Privacy Levels Demo
```bash
# Ingest with different consent levels
python cli.py ingest file.txt --consent metadata_only
python cli.py ingest file.txt --consent anonymized
python cli.py ingest file.txt --consent full
```

### 3. Export Consciousness
```bash
# Export to JSON
python cli.py export --format json --output my_consciousness.json

# Query specific date range
python cli.py query --start-date 2025-01-01 --end-date 2025-01-31
```

## Architecture Components in Action

The demo showcases all 6 C.H.R.I.S.T. components:

1. **C - Consciousness Capture**: Ingestion of multiple formats
2. **H - Holistic Integration**: Unified database and vector store
3. **R - Retrieval & Reasoning**: Semantic search and RAG
4. **I - Intelligence Augmentation**: LLM-powered chat
5. **S - Simulation**: Query and exploration interfaces
6. **T - Transformation**: Multiple output formats and APIs

## Performance Metrics

With sample data loaded:
- Ingestion: ~100ms per document
- Vector search: <50ms for top-10 results
- RAG response: <2s with LLM, instant with mock
- Database queries: <10ms

## Next Steps

1. **Add Real Data**: Ingest your own emails, documents, chat logs
2. **Configure LLM**: Add OpenAI/Anthropic API key for real RAG
3. **Customize UI**: Modify templates in `src/web/templates/`
4. **Extend Parsers**: Add support for new file formats
5. **Deploy**: Use Docker for production deployment

## Cleanup

To reset everything:
```bash
python demo_clean.py
```

Or manually:
```bash
rm -rf christ.db .chroma_db artifacts/ demo_samples/
```

---

Enjoy exploring consciousness with C.H.R.I.S.T.!