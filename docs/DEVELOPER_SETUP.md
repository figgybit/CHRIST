# Developer Setup Guide

Welcome to the C.H.R.I.S.T. Project! This guide will help you set up your development environment and start contributing.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Setup](#detailed-setup)
4. [Development Workflow](#development-workflow)
5. [Testing](#testing)
6. [Troubleshooting](#troubleshooting)
7. [IDE Setup](#ide-setup)

## Prerequisites

### Required Software
- **Python** 3.9 or higher
- **Git** 2.25 or higher
- **Docker** (optional, but recommended)
- **Node.js** 18+ (for frontend development)

### Recommended Hardware
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 10GB free space for development
- **CPU**: Modern multi-core processor

## Quick Start

For experienced developers who want to get running quickly:

```bash
# Clone the repository
git clone git@github.com:figgybit/CHRIST.git
cd CHRIST

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your settings

# Initialize database
python scripts/init_db.py

# Run tests
pytest

# Start development server
python src/main.py
```

## Detailed Setup

### 1. Fork and Clone

First, fork the repository on GitHub, then:

```bash
# Clone your fork
git clone git@github.com:YOUR_USERNAME/CHRIST.git
cd CHRIST

# Add upstream remote
git remote add upstream git@github.com:figgybit/CHRIST.git

# Verify remotes
git remote -v
```

### 2. Python Environment

#### Using venv (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Linux/macOS:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

#### Using conda

```bash
# Create conda environment
conda create -n christ python=3.9
conda activate christ
```

### 3. Install Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Development dependencies
pip install -r requirements-dev.txt

# Optional ML dependencies
pip install -r requirements-ml.txt
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
# Copy example environment file
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Application
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///./christ.db
# For PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/christ

# Encryption
ENCRYPTION_KEY=generate-a-secure-key
KDF_ITERATIONS=100000

# APIs (optional)
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Storage
STORAGE_PATH=./data/storage
TEMP_PATH=./data/temp

# Logging
LOG_LEVEL=DEBUG
LOG_FILE=./logs/christ.log
```

### 5. Database Setup

#### SQLite (Default for development)

```bash
# Initialize database
python scripts/init_db.py

# Run migrations
python scripts/migrate.py
```

#### PostgreSQL (Recommended for production)

```bash
# Install PostgreSQL
# Ubuntu/Debian:
sudo apt-get install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Create database
createdb christ_dev

# Update DATABASE_URL in .env
# Run migrations
python scripts/migrate.py
```

### 6. Docker Setup (Optional)

Using Docker simplifies dependency management:

```bash
# Build Docker image
docker-compose build

# Start services
docker-compose up

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Development Workflow

### 1. Create Feature Branch

```bash
# Update main branch
git checkout main
git pull upstream main

# Create feature branch
git checkout -b feature/your-feature-name
```

### 2. Code Style

We use Black for Python formatting and ESLint for JavaScript:

```bash
# Format Python code
black src/ tests/

# Check Python style
flake8 src/ tests/

# Type checking
mypy src/

# Format JavaScript (if working on frontend)
npm run format
```

### 3. Pre-commit Hooks

Install pre-commit hooks to ensure code quality:

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

### 4. Running Components

#### Start Individual Components

```bash
# Consciousness Capture service
python src/consciousness/server.py

# Holistic Model service
python src/holistic/server.py

# Retrieval service
python src/retrieval/server.py

# API Gateway
python src/api/gateway.py
```

#### Start All Services

```bash
# Using the orchestrator
python src/main.py

# Or using Docker
docker-compose up
```

### 5. Development Server

```bash
# Start with auto-reload
python src/main.py --reload

# Specify port
python src/main.py --port 8080

# Enable debug mode
python src/main.py --debug
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test file
pytest tests/consciousness/test_ingestion.py

# Run specific test
pytest tests/consciousness/test_ingestion.py::test_email_parsing

# Run with verbose output
pytest -v

# Run only marked tests
pytest -m "unit"  # or "integration", "slow"
```

### Test Structure

```
tests/
├── unit/              # Fast, isolated tests
│   ├── consciousness/
│   ├── holistic/
│   └── ...
├── integration/       # Component interaction tests
├── e2e/              # End-to-end tests
└── fixtures/         # Test data
```

### Writing Tests

```python
# Example test file: tests/unit/consciousness/test_parser.py
import pytest
from src.consciousness.parsers import EmailParser

def test_email_parsing():
    """Test email parsing functionality."""
    parser = EmailParser()
    result = parser.parse("test_email.eml")

    assert result is not None
    assert result.subject == "Test Email"
    assert len(result.attachments) == 0

@pytest.fixture
def sample_email():
    """Fixture providing sample email data."""
    return {
        "subject": "Test",
        "from": "test@example.com",
        "body": "Test content"
    }

def test_with_fixture(sample_email):
    """Test using fixture."""
    assert sample_email["subject"] == "Test"
```

## Troubleshooting

### Common Issues

#### ImportError: No module named 'src'

```bash
# Add project root to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${PWD}"
# Or install in development mode
pip install -e .
```

#### Database Connection Error

```bash
# Check database is running
psql -U postgres -c "SELECT 1"

# Reset database
python scripts/reset_db.py
```

#### Port Already in Use

```bash
# Find process using port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill process
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows
```

#### Virtual Environment Not Activating

```bash
# Recreate virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## IDE Setup

### Visual Studio Code

1. Install Python extension
2. Create `.vscode/settings.json`:

```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  }
}
```

3. Create `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: CHRIST",
      "type": "python",
      "request": "launch",
      "module": "src.main",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```

### PyCharm

1. Open project as Python project
2. Configure interpreter:
   - File → Settings → Project → Python Interpreter
   - Select virtual environment
3. Mark directories:
   - Right-click `src` → Mark Directory as → Sources Root
   - Right-click `tests` → Mark Directory as → Test Sources Root
4. Configure tests:
   - Settings → Tools → Python Integrated Tools
   - Default test runner: pytest

### Vim/Neovim

Add to your config:

```vim
" Python settings
autocmd FileType python set colorcolumn=88
autocmd FileType python set expandtab
autocmd FileType python set shiftwidth=4
autocmd FileType python set softtabstop=4

" ALE settings for Python
let g:ale_python_flake8_options = '--max-line-length=88'
let g:ale_python_black_options = '--line-length=88'
let g:ale_fixers = {'python': ['black', 'isort']}
let g:ale_fix_on_save = 1
```

## Development Tools

### Database Management

```bash
# Access SQLite database
sqlite3 christ.db

# Access PostgreSQL
psql -d christ_dev

# Database migrations
python scripts/migrate.py create "Add user table"
python scripts/migrate.py upgrade
python scripts/migrate.py downgrade
```

### API Testing

```bash
# Using HTTPie
http GET localhost:8000/api/v1/health

# Using curl
curl http://localhost:8000/api/v1/health

# Interactive API docs
open http://localhost:8000/docs  # Swagger UI
open http://localhost:8000/redoc  # ReDoc
```

### Performance Profiling

```bash
# Profile specific function
python -m cProfile -o profile.stats src/main.py

# Visualize profile
pip install snakeviz
snakeviz profile.stats
```

### Memory Profiling

```bash
# Install memory profiler
pip install memory_profiler

# Run with memory profiling
python -m memory_profiler src/main.py
```

## Debugging

### Using pdb

```python
# Add breakpoint in code
import pdb; pdb.set_trace()

# Or in Python 3.7+
breakpoint()
```

### Using IPython

```python
# Interactive shell at breakpoint
from IPython import embed; embed()
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate log levels
logger.debug("Detailed debug info")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
logger.critical("Critical issue")
```

## Continuous Integration

Our CI pipeline runs automatically on pull requests:

1. **Linting**: Code style checks
2. **Type Checking**: mypy validation
3. **Unit Tests**: Fast tests
4. **Integration Tests**: Component tests
5. **Coverage**: Minimum 80% required
6. **Security Scan**: Vulnerability check

To run CI checks locally:

```bash
# Run all CI checks
./scripts/ci.sh

# Or individually
black --check src/ tests/
flake8 src/ tests/
mypy src/
pytest --cov=src
safety check
```

## Getting Help

### Resources
- [Documentation](https://christs.ai/docs)
- [API Reference](./docs/api/)
- [Architecture Guide](./docs/ARCHITECTURE.md)
- [Contributing Guide](./CONTRIBUTING.md)

### Communication
- **Discord**: [Join Server](#) (Coming Soon)
- **GitHub Discussions**: For questions and ideas
- **Issue Tracker**: For bugs and features
- **Weekly Sync**: Thursdays 2PM UTC

### Mentorship
New contributors can request a mentor by:
1. Joining Discord
2. Introducing yourself in #introductions
3. Asking in #mentorship

---

**Happy Coding! 🚀**

*Remember: We're building the future of consciousness preservation. Your contribution matters!*