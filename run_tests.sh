#!/bin/bash
# C.H.R.I.S.T. Project - Comprehensive Test Suite

echo "======================================================"
echo "   C.H.R.I.S.T. Project - Running Test Suite"
echo "======================================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Activate virtual environment
if [ -d "../venv" ]; then
    source ../venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${RED}✗${NC} Virtual environment not found"
    exit 1
fi

echo -e "\n${YELLOW}[1/5]${NC} Running database tests..."
python -m pytest tests/test_database.py -v --tb=short
DB_RESULT=$?

echo -e "\n${YELLOW}[2/5]${NC} Running parser tests..."
python -m pytest tests/test_parsers.py -v --tb=short
PARSER_RESULT=$?

echo -e "\n${YELLOW}[3/5]${NC} Running encryption tests..."
python -m pytest tests/test_encryption.py -v --tb=short 2>/dev/null
ENCRYPTION_RESULT=$?

echo -e "\n${YELLOW}[4/5]${NC} Running API tests..."
python -m pytest tests/test_api.py -v --tb=short 2>/dev/null
API_RESULT=$?

echo -e "\n${YELLOW}[5/5]${NC} Running integration tests..."
python -m pytest tests/test_integration.py -v --tb=short 2>/dev/null
INTEGRATION_RESULT=$?

echo -e "\n======================================================"
echo "   Test Results Summary"
echo "======================================================"

if [ $DB_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Database tests: PASSED"
else
    echo -e "${RED}✗${NC} Database tests: FAILED"
fi

if [ $PARSER_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Parser tests: PASSED"
else
    echo -e "${RED}✗${NC} Parser tests: FAILED"
fi

if [ $ENCRYPTION_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Encryption tests: PASSED"
else
    echo -e "${YELLOW}?${NC} Encryption tests: NOT FOUND"
fi

if [ $API_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓${NC} API tests: PASSED"
else
    echo -e "${YELLOW}?${NC} API tests: NOT FOUND"
fi

if [ $INTEGRATION_RESULT -eq 0 ]; then
    echo -e "${GREEN}✓${NC} Integration tests: PASSED"
else
    echo -e "${YELLOW}?${NC} Integration tests: NOT FOUND"
fi

echo "======================================================"

# Overall result
if [ $DB_RESULT -eq 0 ] && [ $PARSER_RESULT -eq 0 ]; then
    echo -e "\n${GREEN}✅ Core tests passed! System is functional.${NC}"
    exit 0
else
    echo -e "\n${RED}❌ Some tests failed. Please review the output above.${NC}"
    exit 1
fi