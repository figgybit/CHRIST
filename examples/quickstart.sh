#!/bin/bash
# C.H.R.I.S.T. Project - Quick Start Script

echo "======================================================"
echo "   C.H.R.I.S.T. Project - Quick Start Setup"
echo "======================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Step 1: Check Python
echo -e "\n${YELLOW}[1/6]${NC} Checking Python installation..."
if command_exists python3; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    echo -e "${GREEN}✓${NC} Found $PYTHON_VERSION"
else
    echo -e "${RED}✗${NC} Python 3 not found. Please install Python 3.9+"
    exit 1
fi

# Step 2: Create virtual environment
echo -e "\n${YELLOW}[2/6]${NC} Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Step 3: Install dependencies
echo -e "\n${YELLOW}[3/6]${NC} Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Step 4: Initialize database
echo -e "\n${YELLOW}[4/6]${NC} Initializing database..."
python src/scripts/cli.py init-db
echo -e "${GREEN}✓${NC} Database initialized"

# Step 5: Load sample data
echo -e "\n${YELLOW}[5/6]${NC} Loading sample data..."
python examples/scripts/demo_ingest.py
echo -e "${GREEN}✓${NC} Sample data loaded"

# Step 6: Start the server
echo -e "\n${YELLOW}[6/6]${NC} Starting the C.H.R.I.S.T. server..."
echo ""
echo "======================================================"
echo "   Setup Complete! Server starting..."
echo "======================================================"
echo ""
echo "The system will be available at:"
echo "  • Web Interface: http://localhost:8000"
echo "  • API Documentation: http://localhost:8000/docs"
echo "  • Alternative API Docs: http://localhost:8000/redoc"
echo ""
echo "Quick actions:"
echo "  • Upload data: http://localhost:8000/ingest"
echo "  • Search memories: http://localhost:8000/search"
echo "  • Chat: http://localhost:8000/chat"
echo ""
echo "Press Ctrl+C to stop the server"
echo "======================================================"
echo ""

# Start the server
python src/main.py --reload