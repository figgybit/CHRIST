#!/bin/bash

# C.H.R.I.S.T. System - Setup Script
# Makes it easy to get started with the consciousness capture system

echo "========================================================"
echo "    C.H.R.I.S.T. System - Setup & Installation"
echo "========================================================"
echo

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check Python
echo "📋 Checking requirements..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found${NC}"
    echo "Please install Python 3.8+ first"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python 3 found"

# Step 2: Create virtual environment
if [ ! -d "venv" ]; then
    echo
    echo "🔧 Creating virtual environment..."
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment exists"
fi

# Step 3: Activate and install requirements
echo
echo "📦 Installing Python packages..."
source venv/bin/activate

# Install core requirements
pip install --upgrade pip > /dev/null 2>&1
pip install -q \
    fastapi \
    uvicorn \
    sqlalchemy \
    pydantic \
    python-multipart \
    jinja2 \
    aiofiles \
    chromadb \
    numpy \
    scikit-learn \
    requests

echo -e "${GREEN}✓${NC} Core packages installed"

# Step 4: Install sentence-transformers (optional but recommended)
echo
echo "🧠 Installing AI components..."
echo -e "${YELLOW}This will download ~2GB for sentence-transformers and PyTorch${NC}"
read -p "Install sentence-transformers for semantic search? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing sentence-transformers (this may take a few minutes)..."
    pip install -q sentence-transformers
    echo -e "${GREEN}✓${NC} Sentence-transformers installed"
else
    echo "Skipping sentence-transformers (will use fallback embeddings)"
fi

# Step 5: Check for Ollama
echo
echo "🤖 Checking for Ollama (local LLM)..."
if command -v ollama &> /dev/null; then
    echo -e "${GREEN}✓${NC} Ollama is installed"

    # Check if Ollama is running
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} Ollama server is running"

        # List available models
        echo "Available models:"
        ollama list
    else
        echo -e "${YELLOW}⚠${NC} Ollama is installed but not running"
        echo "Start it with: ollama serve"

        read -p "Start Ollama server now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Starting Ollama server in background..."
            nohup ollama serve > /dev/null 2>&1 &
            sleep 2
            echo -e "${GREEN}✓${NC} Ollama server started"
        fi
    fi

    # Check for models
    if ! ollama list | grep -q "gemma\|llama\|mistral"; then
        echo
        echo "No suitable models found. Recommended models:"
        echo "  - llama2 (3.8GB) - Best for consciousness/philosophy"
        echo "  - mistral (4.1GB) - Fast and capable"
        echo "  - gemma:2b (1.4GB) - Lightweight option"

        read -p "Install a model? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "Choose a model:"
            echo "1) gemma:2b (1.4GB - lightweight)"
            echo "2) llama2 (3.8GB - recommended)"
            echo "3) mistral (4.1GB - fast)"
            read -p "Selection (1-3): " model_choice

            case $model_choice in
                1) ollama pull gemma:2b ;;
                2) ollama pull llama2 ;;
                3) ollama pull mistral ;;
                *) echo "Invalid selection" ;;
            esac
        fi
    fi
else
    echo -e "${YELLOW}⚠${NC} Ollama not installed"
    echo "Install Ollama for local LLM support:"
    echo "  Linux/Mac: curl -fsSL https://ollama.com/install.sh | sh"
    echo "  Or visit: https://ollama.com/download"
fi

# Step 6: Create demo data
echo
echo "📚 Setting up demo data..."
if [ ! -d "rich_demo_data" ]; then
    python create_rich_demo.py > /dev/null 2>&1
    echo -e "${GREEN}✓${NC} Rich demo content created"
else
    echo -e "${GREEN}✓${NC} Demo content exists"
fi

# Step 7: Initialize database
echo
echo "💾 Initializing database..."
python -c "from src.consciousness.database import init_database; init_database()" 2>/dev/null
echo -e "${GREEN}✓${NC} Database initialized"

# Step 8: Show next steps
echo
echo "========================================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "========================================================"
echo
echo "🚀 Quick Start Commands:"
echo
echo "1. Load demo data & test search:"
echo "   ${YELLOW}python demo_clean.py${NC}"
echo
echo "2. Interactive query mode:"
echo "   ${YELLOW}python cli.py query${NC}"
echo
echo "3. Chat with your consciousness:"
echo "   ${YELLOW}python cli.py chat${NC}"
echo
echo "4. Web interface:"
echo "   ${YELLOW}python web_app.py${NC}"
echo "   Then open: http://localhost:8000"
echo
echo "5. API server:"
echo "   ${YELLOW}python api_server.py${NC}"
echo "   API docs: http://localhost:8001/docs"
echo
echo "========================================================"
echo "📖 For more info, see README.md and DEMO.md"
echo "========================================================"