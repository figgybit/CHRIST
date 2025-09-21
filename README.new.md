# 🧠 The C.H.R.I.S.T. Project

**Consciousness Handling, Retrieval, Intelligence, Simulation & Transformation**

An open-source system for capturing, preserving, and emulating human consciousness through ethical AI and privacy-preserving technologies.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-brightgreen.svg)](https://www.docker.com/)
[![Contributions Welcome](https://img.shields.io/badge/contributions-welcome-brightgreen.svg)](CONTRIBUTING.md)

## 🚀 Quick Start

### 1-Minute Setup

```bash
# Clone the repository
git clone https://github.com/figgybit/CHRIST.git
cd CHRIST

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python src/scripts/cli.py init-db

# Run the system
python src/main.py
```

The API is now running at http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

### First Data Ingestion

```bash
# Ingest a text file
python src/scripts/cli.py ingest -f example.txt --consent full

# Ingest an email archive
python src/scripts/cli.py ingest -f emails.mbox --consent anonymized

# Query your data
python src/scripts/cli.py query --limit 10
```

### Docker Setup (Alternative)

```bash
# Start all services
docker-compose up

# Or run in background
docker-compose up -d
```

## 🎯 What is C.H.R.I.S.T.?

C.H.R.I.S.T. is a modular system designed to:

- **C**apture your digital footprint (emails, documents, chats, journals)
- **H**olistically model your knowledge, relationships, and experiences
- **R**etrieve memories and reflect on patterns using AI
- **I**ntegrity-check actions against your values and ethics
- **S**imulate your personality for interaction and decision-making
- **T**rack goals and transformation over time

### Key Features

✅ **Privacy-First**: End-to-end encryption, local storage, GDPR compliant
✅ **Multi-Format Support**: Email, text, PDF, Word, chat exports
✅ **AI-Powered**: RAG system with LLM integration for intelligent queries
✅ **Consent-Based**: Granular control over data processing levels
✅ **Open Source**: Fully transparent, auditable, and extensible
✅ **API-Driven**: RESTful API for integration with other tools

## 📖 Documentation

- **[Full Documentation](docs/)** - Complete guides and references
- **[API Reference](docs/api/api-specification.md)** - REST/GraphQL endpoints
- **[Developer Setup](docs/DEVELOPER_SETUP.md)** - Detailed dev environment guide
- **[Privacy Framework](docs/privacy/PRIVACY_FRAMEWORK.md)** - Security and privacy details
- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Roadmap](ROADMAP.md)** - Project timeline and milestones

## 🏗️ Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     User Interface                       │
│                 (CLI / Web UI / API)                     │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│                    API Gateway                           │
│                 (FastAPI + Auth)                         │
└──┬──────┬──────┬──────┬──────┬──────┬──────────────────┘
   │      │      │      │      │      │
┌──▼──┐┌──▼──┐┌──▼──┐┌──▼──┐┌──▼──┐┌──▼──┐
│  C  ││  H  ││  R  ││  I  ││  S  ││  T  │
└──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘└──┬──┘
   │      │      │      │      │      │
┌──▼──────▼──────▼──────▼──────▼──────▼──┐
│         Data Layer (PostgreSQL)          │
│      Vector Store (ChromaDB)             │
│        Encryption (AES-256)              │
└──────────────────────────────────────────┘
```

## 💻 API Examples

### Ingest Data
```bash
curl -X POST http://localhost:8000/api/v1/consciousness/ingest \
  -H "Content-Type: application/json" \
  -d '{
    "source_type": "journal",
    "content": "Today I learned about quantum computing...",
    "consent_level": "full"
  }'
```

### Search Memories
```bash
curl -X POST http://localhost:8000/api/v1/retrieval/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "quantum computing",
    "k": 5
  }'
```

### Ask Questions
```bash
curl -X POST http://localhost:8000/api/v1/retrieval/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What did I learn about quantum computing?"}'
```

## 🛠️ Development

### Project Structure
```
CHRIST/
├── src/
│   ├── consciousness/    # Data ingestion & storage
│   ├── holistic/        # Knowledge graph & relationships
│   ├── retrieval/       # RAG system & search
│   ├── intent/          # Values & ethics engine
│   ├── simulation/      # Personality simulation
│   ├── teleology/       # Goals & transformation
│   └── api/            # REST API endpoints
├── tests/              # Test suite
├── docs/               # Documentation
└── examples/           # Example scripts
```

### Running Tests
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific component tests
pytest tests/consciousness/
```

### Adding New Data Sources

1. Create a parser in `src/consciousness/parsers.py`
2. Add to `UniversalParser` class
3. Write tests in `tests/test_parsers.py`
4. Update documentation

## 🔐 Privacy & Security

- **Encryption**: All personal data encrypted with AES-256-GCM
- **Consent Levels**: None, Metadata, Anonymized, Full
- **Right to Forget**: Complete data deletion on request
- **Local First**: Your data stays on your machine by default
- **Audit Logging**: All data access is logged

See [Privacy Framework](docs/privacy/PRIVACY_FRAMEWORK.md) for details.

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Priority TODOs

- [ ] Integrate Neo4j for knowledge graph
- [ ] Add OpenAI/Anthropic API support
- [ ] Build React/Vue dashboard
- [ ] Implement Celery for async tasks
- [ ] Add more data source parsers
- [ ] Create mobile apps
- [ ] Implement federation protocol

## 📚 Philosophy & Vision

The C.H.R.I.S.T. Project combines two visions:

1. **Technical**: Build an ethical AI system for consciousness preservation
2. **Spiritual**: Unite humanity through shared wisdom and technology

Read the full [treatise](treatise.md) and [Christ.md](Christ.md) for deeper understanding.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- The open-source community
- All faith traditions that inspire unity
- Privacy advocates and ethical AI researchers
- Early contributors and testers

## 📞 Contact

- **GitHub Issues**: [Bug reports and features](https://github.com/figgybit/CHRIST/issues)
- **Discussions**: [Community forum](https://github.com/figgybit/CHRIST/discussions)
- **Email**: hello@christproject.org (coming soon)

---

*"The future is now – unite to evolve"*

**Remember**: Your consciousness is sacred. This tool exists to serve you, not the other way around.