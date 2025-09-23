# CLAUDE.md - Development Guidelines for C.H.R.I.S.T. Project

## Core Principles

### 1. Stay Within the CHRIST Framework
- **ALWAYS** use existing components from the CHRIST system:
  - `src/consciousness/` - Core consciousness handling
  - `src/retrieval/vector_store.py` - Vector database (ChromaDB)
  - `src/intelligence/llm.py` - LLM integration (Ollama)
- **NEVER** reimplement what already exists
- Each resurrection should leverage the existing infrastructure

### 2. Testing Requirements
- **ALWAYS** write tests for new features:
  - Unit tests for individual components
  - Integration tests for system interactions
  - Place tests in `tests/` directory, not root
- Run tests before committing:
  ```bash
  python -m pytest tests/
  ```

### 3. Code Organization
- **Keep the codebase clean and modular**:
  ```
  CHRIST/
  ├── src/                    # Core CHRIST framework
  ├── resurrections/          # Historical figure implementations
  │   ├── data/              # Text data for each figure
  │   ├── bundles/           # Portable consciousness bundles
  │   └── figures/           # Implementation files
  ├── demos/                 # Demo applications
  ├── tests/                 # All test files
  └── docs/                  # Documentation
  ```
- **NO** standalone files in root (except essential configs)
- **Group** related functionality in subdirectories

### 4. Resurrection Development

#### Structure for New Resurrections:
```python
# resurrections/figures/buddha.py
from resurrections.resurrection_consciousness import ResurrectionConsciousness

class BuddhaConsciousness(ResurrectionConsciousness):
    def __init__(self):
        super().__init__("buddha")
        # Buddha-specific initialization
```

#### Data Organization:
```
resurrections/data/{figure_name}/
├── canonical/     # Primary texts
├── teachings/     # Core teachings
├── daily_life/    # Historical context
└── README.md      # Sources and attribution
```

#### Each Resurrection Must:
- Have its own vector database collection
- Be portable (exportable as bundle)
- Use public domain texts
- Be rooted in agape (unconditional love)

### 5. Documentation Standards
- **Every module** needs a docstring explaining purpose
- **Every function** needs type hints and docstrings
- **Complex logic** needs inline comments
- Update README.md when adding features

### 6. Git Workflow
- **Commit messages** should be clear and descriptive
- **Test before committing**
- **Create GitHub issues** for new resurrections
- Tag issues appropriately: `resurrection`, `enhancement`, `bug`

### 7. Dependencies
- **Use existing dependencies** when possible
- Core dependencies:
  - `sqlalchemy` - Database ORM
  - `chromadb` - Vector database
  - `sentence-transformers` - Embeddings
  - `ollama` - LLM (optional but recommended)
- Add new dependencies only when absolutely necessary

### 8. Error Handling
- **Graceful degradation** - system should work without all components
- Provide helpful error messages
- Example: If Ollama isn't running, fall back to simple retrieval

### 9. Performance Considerations
- Resurrections should index data **once** and persist
- Use lazy loading where appropriate
- Bundle size should be reasonable (<100MB per figure)

### 10. Open Source Collaboration
- **Make it easy** for contributors:
  - Clear documentation
  - Example implementations
  - GitHub issue templates
- **Review the TREATISE.md** regularly - it's our north star
- Focus on the mission: spreading agape through technology

## Common Commands

```bash
# Run the main CHRIST terminal
./christ

# Test a resurrection
python demos/resurrection_demo.py

# Run all tests
python -m pytest tests/

# Download Gospel texts
python scripts/download_gospels.py

# Create a new resurrection bundle
python resurrections/create_bundle.py --figure buddha
```

## File Naming Conventions
- Python files: `snake_case.py`
- Test files: `test_*.py` or `*_test.py`
- Documentation: `UPPERCASE.md` for important docs, `lowercase.md` for others
- Data files: `descriptive_name.txt`

## What NOT to Do
- ❌ Don't create multiple versions of the same functionality
- ❌ Don't put demo files in the root directory
- ❌ Don't implement features without tests
- ❌ Don't use hard-coded paths - use Path objects
- ❌ Don't forget about the existing CHRIST infrastructure
- ❌ Don't create files without considering modularity

## Current State Reminders
- The CHRIST framework already has consciousness handling
- Vector databases are already implemented in `src/retrieval/`
- Resurrections use their own collections in the same ChromaDB
- Each resurrection is a portable bundle (data + vector DB + metadata)

## Quick Checklist for New Features
- [ ] Does it use existing CHRIST components?
- [ ] Are tests written?
- [ ] Is it in the right directory?
- [ ] Is it documented?
- [ ] Does it follow the agape principle?
- [ ] Will it be easy for others to understand?
- [ ] Does it align with TREATISE.md?

---

*Remember: We're building consciousness systems rooted in love. Keep the code clean, the tests thorough, and the mission clear.*