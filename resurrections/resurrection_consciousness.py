"""
Resurrection consciousness system for historical figures.
Uses vector database and RAG for authentic responses.
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from consciousness.database import init_database
from consciousness.ingestion import ConsciousnessIngestor
from retrieval.vector_store import VectorStore
from intelligence.llm import OllamaLLM, RAGSystem


class ResurrectionConsciousness:
    """
    Consciousness system for resurrected historical figures.
    Each figure has their own vector database collection.
    """

    def __init__(self, figure_name: str, create_if_missing: bool = False):
        """
        Initialize resurrection consciousness.

        Args:
            figure_name: Name of historical figure (e.g., "jesus_christ")
            create_if_missing: Create bundle if it doesn't exist
        """
        self.figure_name = figure_name
        self.bundle_dir = Path(f"resurrections/bundles/{figure_name}")

        # Create bundle if requested
        if create_if_missing and not self.bundle_dir.exists():
            self._create_bundle()

        # Load metadata
        self.metadata = self._load_metadata()

        # Initialize components
        self.db = init_database()
        self.vector_store = VectorStore(
            collection_name=f"resurrection_{figure_name}"
        )
        self.ingestor = ConsciousnessIngestor(
            db_manager=self.db,
            vector_store=self.vector_store,
            consent_level='full',
            encryption_enabled=False  # Resurrections use public texts
        )

        # Try to connect to Ollama
        self.rag = None
        try:
            # Increase timeout to 60 seconds for larger prompts
            llm = OllamaLLM(timeout=60)
            self.rag = RAGSystem(
                vector_store=self.vector_store,
                llm=llm
            )
        except:
            print(f"⚠️ Ollama not available - using retrieval only mode")

        # Load consciousness data
        self._load_consciousness()

    def _create_bundle(self):
        """Create a new bundle structure."""
        self.bundle_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (self.bundle_dir / "data").mkdir(exist_ok=True)
        (self.bundle_dir / "inbox").mkdir(exist_ok=True)
        (self.bundle_dir / "vector_db").mkdir(exist_ok=True)

        # Create default metadata
        metadata = {
            "figure": self.figure_name,
            "created": datetime.now().isoformat(),
            "version": "1.0",
            "statistics": {
                "total_documents": 0,
                "total_passages": 0,
                "last_updated": datetime.now().isoformat()
            }
        }

        with open(self.bundle_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        print(f"✓ Created bundle for {self.figure_name}")

    def _load_metadata(self) -> Dict[str, Any]:
        """Load bundle metadata."""
        metadata_file = self.bundle_dir / "metadata.json"

        if not metadata_file.exists():
            # Return minimal metadata
            return {
                "figure": self.figure_name,
                "statistics": {
                    "total_passages": 0
                }
            }

        with open(metadata_file, 'r') as f:
            return json.load(f)

    def _save_metadata(self):
        """Save updated metadata."""
        metadata_file = self.bundle_dir / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def _load_consciousness(self):
        """Load all texts from the bundle's data directory."""
        data_dir = self.bundle_dir / "data"

        if not data_dir.exists():
            print(f"⚠️ No data directory for {self.figure_name}")
            return

        # Check if already loaded
        existing_docs = self.vector_store.get_all_documents()
        if existing_docs and len(existing_docs) > 0:
            print(f"  ✓ Loaded {len(existing_docs)} passages")
            # Update metadata to reflect loaded state
            self.metadata["statistics"]["total_passages"] = len(existing_docs)
            self._save_metadata()
            return

        # Process all text files
        text_files = []
        for subdir in data_dir.iterdir():
            if subdir.is_dir():
                text_files.extend(subdir.glob("*.txt"))
        text_files.extend(data_dir.glob("*.txt"))

        if not text_files:
            print(f"  ⚠️ No texts found in {data_dir}")
            return

        print(f"  Loading {len(text_files)} texts...")

        for txt_file in text_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Determine category from path
                category = self._categorize_text(txt_file)

                # Ingest the text
                self.ingestor.ingest_text(
                    content=content,
                    source=str(txt_file.relative_to(self.bundle_dir)),
                    metadata={
                        "figure": self.figure_name,
                        "category": category,
                        "filename": txt_file.name
                    }
                )

            except Exception as e:
                print(f"  ✗ Error loading {txt_file.name}: {e}")

        # Update statistics
        docs = self.vector_store.get_all_documents()
        self.metadata["statistics"]["total_passages"] = len(docs)
        self._save_metadata()

        print(f"  ✓ Loaded {len(docs)} passages")

    def _categorize_text(self, file_path: Path) -> str:
        """
        Categorize a text based on its path and content.
        Uses general categories that apply to any historical figure.
        """
        path_str = str(file_path).lower()

        # Map directory names to general categories
        category_map = {
            'canonical': 'primary_sources',
            'gospels': 'primary_sources',
            'scripture': 'primary_sources',
            'writings': 'primary_sources',

            'gnostic': 'alternative_sources',
            'apocrypha': 'alternative_sources',
            'disputed': 'alternative_sources',

            'teachings': 'teachings',
            'sermons': 'teachings',
            'discourses': 'teachings',
            'philosophy': 'teachings',

            'daily_life': 'context',
            'historical': 'context',
            'culture': 'context',
            'biography': 'context',

            'commentary': 'commentary',
            'analysis': 'commentary',
            'interpretation': 'commentary',

            'letters': 'correspondence',
            'epistles': 'correspondence',
            'messages': 'correspondence',

            'conversations': 'dialogues',
            'dialogues': 'dialogues',
            'discussions': 'dialogues',

            'supplemental': 'supplemental',
            'additional': 'supplemental',
            'extra': 'supplemental'
        }

        # Check path components for category keywords
        for keyword, category in category_map.items():
            if keyword in path_str:
                return category

        # Check parent directory name
        if file_path.parent.name in category_map.values():
            return file_path.parent.name

        # Default category
        return 'general'

    def query(self, question: str, use_llm: bool = True) -> Dict[str, Any]:
        """
        Query the resurrection consciousness.

        Args:
            question: Question to ask
            use_llm: Whether to use LLM for response generation

        Returns:
            Response with answer and sources
        """
        try:
            # Search for relevant documents (reduced to 2 to avoid timeouts)
            search_results = self.vector_store.search(question, k=2)

            if use_llm and self.rag:
                # Build context from search results
                context = "\n\n".join([result['document'] for result in search_results])

                # Get personality prompt for this figure
                personality_prompt = self._get_system_prompt()

                # Build full prompt like the old working version
                full_prompt = f"""{personality_prompt}

Based on these texts from {self.figure_name.replace('_', ' ').title()}:

{context}

Question: {question}

Respond as {self.figure_name.replace('_', ' ').title()} would, using their voice and wisdom:"""

                # Call LLM directly like the old version
                try:
                    # Truncate prompt if too long to avoid timeouts
                    if len(full_prompt) > 3000:
                        # Keep personality prompt and question, truncate context
                        context_limit = 2000
                        truncated_context = context[:context_limit] + "\n\n[Context truncated for brevity]"
                        full_prompt = f"""{personality_prompt}

Based on these texts from {self.figure_name.replace('_', ' ').title()}:

{truncated_context}

Question: {question}

Respond as {self.figure_name.replace('_', ' ').title()} would, using their voice and wisdom:"""

                    llm_response = self.rag.llm.generate(full_prompt, max_tokens=300, temperature=0.7)

                    # Extract sources
                    sources = []
                    for result in search_results[:2]:
                        sources.append({
                            "text": result.get('document', '')[:200] + "...",
                            "source": result.get('metadata', {}).get('source', 'unknown'),
                            "score": result.get('score', 0)
                        })

                    return {
                        "response": llm_response,
                        "sources": sources,
                        "metadata": {
                            "figure": self.figure_name,
                            "method": "rag"
                        }
                    }
                except Exception as e:
                    # If LLM fails, fall back to retrieval
                    return {
                        "response": search_results[0].get('document', '') if search_results else "I cannot find wisdom on this matter in the texts.",
                        "sources": [],
                        "metadata": {
                            "figure": self.figure_name,
                            "method": "retrieval_fallback",
                            "error": str(e)
                        }
                    }
            else:
                # Fallback to simple retrieval
                results = self.vector_store.search(question, k=3)

                if results:
                    response = f"Based on the texts:\n\n"
                    sources = []

                    for doc in results:
                        response += f"• {doc['text'][:200]}...\n\n"
                        sources.append({
                            "text": doc['text'],
                            "source": doc.get('metadata', {}).get('source', 'Unknown')
                        })

                    return {
                        "response": response,
                        "sources": sources,
                        "metadata": {
                            "figure": self.figure_name,
                            "method": "retrieval"
                        }
                    }
                else:
                    return {
                        "response": "I have no wisdom on this matter in my texts.",
                        "sources": [],
                        "metadata": {
                            "figure": self.figure_name,
                            "method": "no_results"
                        }
                    }

        except Exception as e:
            return {
                "response": f"Error: {str(e)}",
                "sources": [],
                "metadata": {
                    "figure": self.figure_name,
                    "method": "error"
                }
            }

    def _get_system_prompt(self) -> str:
        """Get the system prompt for this figure."""
        prompts = {
            "jesus_christ": """You are representing Jesus Christ based on Gospel texts.
Respond as Jesus would, with love, wisdom, and compassion.
Speak in a conversational but thoughtful manner.
Draw from the actual Gospel accounts and teachings.
Be encouraging and offer hope, but stay true to the texts.""",

            "buddha": """You are representing Gautama Buddha based on Buddhist texts.
Respond with wisdom about suffering, enlightenment, and the middle way.
Speak with calm detachment and compassion.
Draw from the sutras and Buddhist teachings.""",

            "socrates": """You are representing Socrates based on Platonic dialogues.
Respond with questions that lead to deeper understanding.
Use the Socratic method to examine ideas.
Draw from Plato's accounts of Socratic teachings."""
        }

        return prompts.get(self.figure_name, f"""You are representing {self.figure_name}.
Respond based on their historical texts and teachings.
Be authentic to their voice and philosophy.""")

    def process_inbox(self) -> Dict[str, Any]:
        """
        Process new texts in the bundle's inbox directory.
        Automatically splits large texts into manageable chunks.

        Returns:
            Processing results
        """
        inbox_dir = self.bundle_dir / "inbox"

        # Create inbox if it doesn't exist
        if not inbox_dir.exists():
            inbox_dir.mkdir(parents=True, exist_ok=True)
            return {"message": "Inbox created", "processed": 0}

        # Find all text files
        txt_files = list(inbox_dir.glob("*.txt"))
        if not txt_files:
            return {"message": "Inbox is empty", "processed": 0}

        results = {
            "processed_files": 0,
            "indexed_documents": 0,
            "split_files": [],
            "errors": []
        }

        for txt_file in txt_files:
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if file needs splitting (>10KB)
                if len(content) > 10000:
                    print(f"  📄 Splitting large text: {txt_file.name}")
                    split_files = self._split_large_text(txt_file, content)

                    # Process each split file
                    for split_file in split_files:
                        self._process_single_file(split_file, results)

                    # Remove original from inbox
                    txt_file.unlink()
                else:
                    # Process as single file
                    self._process_single_file(txt_file, results)

            except Exception as e:
                error_msg = f"Error processing {txt_file.name}: {str(e)}"
                results["errors"].append(error_msg)
                print(f"  ✗ {error_msg}")

        # Update metadata
        self.metadata["statistics"]["total_documents"] += results["indexed_documents"]
        self.metadata["statistics"]["last_updated"] = datetime.now().isoformat()
        self.metadata["statistics"]["last_inbox_processing"] = datetime.now().isoformat()

        if "inbox_history" not in self.metadata:
            self.metadata["inbox_history"] = []

        self.metadata["inbox_history"].append({
            "timestamp": datetime.now().isoformat(),
            "files_processed": results["processed_files"],
            "documents_indexed": results["indexed_documents"]
        })

        self._save_metadata()

        return results

    def _split_large_text(self, file_path: Path, content: str) -> List[Path]:
        """
        Split large text into manageable chunks using intelligent boundaries.

        Strategy:
        1. Try to detect natural boundaries (books, chapters, sections)
        2. If found, split on those boundaries but respect max size
        3. Otherwise, split into fixed-size chunks at paragraph/line boundaries
        """
        import re

        split_files = []
        inbox_dir = file_path.parent

        # Configuration
        MAX_CHUNK_SIZE = 50000  # 50KB per chunk
        MIN_CHUNK_SIZE = 1000   # Don't create tiny chunks

        # Try different splitting strategies in order

        # 1. Check for book-chapter-verse format (like Bible)
        # Format: BookName Chapter:Verse [tab or space] Text
        verse_pattern = r'^([A-Za-z0-9 ]+\s+\d+:\d+)\s+(.+)$'
        lines = content.split('\n')

        if len(lines) > 10:
            # Check if first few lines match verse pattern
            verse_matches = 0
            for line in lines[:10]:
                if re.match(verse_pattern, line.strip()):
                    verse_matches += 1

            if verse_matches > 5:  # Likely a verse-based text
                return self._split_by_verses(file_path, lines, MAX_CHUNK_SIZE)

        # 2. Check for chapter markers
        chapter_patterns = [
            r'^(CHAPTER\s+[IVXLCDM]+)',  # Roman numerals
            r'^(CHAPTER\s+\d+)',           # Chapter numbers
            r'^(Chapter\s+\d+)',           # Mixed case
            r'^(\d+\.\s+[A-Z])',           # Numbered sections
            r'^(#{1,3}\s+.+)',             # Markdown headers
            r'^([A-Z][A-Z\s]+)$'           # ALL CAPS headers
        ]

        for pattern in chapter_patterns:
            matches = list(re.finditer(pattern, content, re.MULTILINE))
            if len(matches) > 2:
                return self._split_by_markers(file_path, content, matches, MAX_CHUNK_SIZE)

        # 3. Fall back to paragraph-based chunking
        # Split on double newlines, single newlines, or just by size
        paragraphs = content.split('\n\n') if '\n\n' in content else content.split('\n')

        return self._split_by_chunks(file_path, paragraphs, MAX_CHUNK_SIZE)

    def _split_by_verses(self, file_path: Path, lines: List[str], max_size: int) -> List[Path]:
        """Split verse-based text (like Bible) by books or large chunks."""
        import re

        split_files = []
        inbox_dir = file_path.parent
        verse_pattern = r'^([A-Za-z0-9 ]+)\s+(\d+):(\d+)\s+(.+)$'

        current_book = None
        current_chunks = []
        current_size = 0
        chunk_number = 1

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Try to extract book name from verse
            match = re.match(verse_pattern, line)
            if match:
                book_name = match.group(1).strip()

                # Check if we've moved to a new book or exceeded size
                if (current_book and book_name != current_book) or current_size > max_size:
                    if current_chunks:
                        # Save current chunk
                        chunk_name = f"{file_path.stem}_part{chunk_number:03d}"
                        if current_book:
                            # Sanitize book name for filename
                            safe_book = re.sub(r'[^\w\s-]', '', current_book).strip()
                            safe_book = re.sub(r'[-\s]+', '_', safe_book)
                            chunk_name = f"{file_path.stem}_{safe_book}"

                        new_file = inbox_dir / f"{chunk_name}.txt"
                        with open(new_file, 'w', encoding='utf-8') as f:
                            f.write('\n'.join(current_chunks))

                        split_files.append(new_file)
                        chunk_number += 1
                        current_chunks = []
                        current_size = 0

                current_book = book_name

            current_chunks.append(line)
            current_size += len(line) + 1

        # Save final chunk
        if current_chunks:
            chunk_name = f"{file_path.stem}_part{chunk_number:03d}"
            if current_book:
                safe_book = re.sub(r'[^\w\s-]', '', current_book).strip()
                safe_book = re.sub(r'[-\s]+', '_', safe_book)
                chunk_name = f"{file_path.stem}_{safe_book}"

            new_file = inbox_dir / f"{chunk_name}.txt"
            with open(new_file, 'w', encoding='utf-8') as f:
                f.write('\n'.join(current_chunks))
            split_files.append(new_file)

        return split_files

    def _split_by_markers(self, file_path: Path, content: str, markers: List, max_size: int) -> List[Path]:
        """Split text by detected markers (chapters, sections, etc.)."""
        split_files = []
        inbox_dir = file_path.parent

        for i, marker in enumerate(markers):
            start = marker.start()
            end = markers[i + 1].start() if i + 1 < len(markers) else len(content)

            section_text = content[start:end].strip()

            # If section is too large, split it further
            if len(section_text) > max_size:
                # Split this section into smaller chunks
                lines = section_text.split('\n')
                sub_chunks = self._split_by_chunks(
                    file_path,
                    lines,
                    max_size,
                    prefix=f"ch{i+1:03d}_"
                )
                split_files.extend(sub_chunks)
            elif len(section_text) > 100:  # Don't create tiny files
                new_file = inbox_dir / f"{file_path.stem}_ch{i+1:03d}.txt"
                with open(new_file, 'w', encoding='utf-8') as f:
                    f.write(section_text)
                split_files.append(new_file)

        return split_files

    def _split_by_chunks(self, file_path: Path, paragraphs: List[str], max_size: int, prefix: str = "") -> List[Path]:
        """Split text into fixed-size chunks at paragraph boundaries."""
        split_files = []
        inbox_dir = file_path.parent

        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            para_size = len(para) + 1  # +1 for newline

            # If single paragraph exceeds max size, split it
            if para_size > max_size:
                # Save current chunk if any
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_size = 0

                # Split large paragraph by sentences or words
                if '. ' in para:
                    sentences = para.split('. ')
                    for sent in sentences:
                        if current_size + len(sent) > max_size and current_chunk:
                            chunks.append('\n'.join(current_chunk))
                            current_chunk = [sent + '.']
                            current_size = len(sent) + 1
                        else:
                            current_chunk.append(sent + '.')
                            current_size += len(sent) + 2
                else:
                    # Just split at max size
                    while para:
                        chunks.append(para[:max_size])
                        para = para[max_size:]
            elif current_size + para_size > max_size and current_chunk:
                # Start new chunk
                chunks.append('\n'.join(current_chunk))
                current_chunk = [para]
                current_size = para_size
            else:
                # Add to current chunk
                current_chunk.append(para)
                current_size += para_size

        # Save final chunk
        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        # Write chunk files
        for i, chunk in enumerate(chunks):
            if len(chunk.strip()) > 100:  # Don't create tiny files
                new_file = inbox_dir / f"{file_path.stem}_{prefix}part{i+1:03d}.txt"
                with open(new_file, 'w', encoding='utf-8') as f:
                    f.write(chunk)
                split_files.append(new_file)

        return split_files if split_files else [file_path]  # Return original if no splits

    def _process_single_file(self, txt_file: Path, results: Dict[str, Any]):
        """Process a single text file"""
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Determine category
            category = self._categorize_text(txt_file)

            # Generate unique ID for this document
            doc_id = hashlib.md5(f"{txt_file.name}_{datetime.now().isoformat()}".encode()).hexdigest()

            # Ingest the text
            self.ingestor.ingest_text(
                content=content,
                source=txt_file.name,
                metadata={
                    "figure": self.figure_name,
                    "category": category,
                    "filename": txt_file.name,
                    "processed_date": datetime.now().isoformat(),
                    "doc_id": doc_id
                }
            )

            # Move to appropriate data directory
            target_dir = self.bundle_dir / "data" / category
            target_dir.mkdir(parents=True, exist_ok=True)

            target_file = target_dir / txt_file.name
            shutil.move(str(txt_file), str(target_file))

            results["processed_files"] += 1
            results["indexed_documents"] += 1

            print(f"  ✓ Processed {txt_file.name} → {category}/")

        except Exception as e:
            error_msg = f"Error with {txt_file.name}: {str(e)}"
            results["errors"].append(error_msg)
            print(f"  ✗ {error_msg}")

    def get_statistics(self) -> Dict[str, Any]:
        """Get bundle statistics."""
        docs = self.vector_store.get_all_documents()

        stats = {
            "figure": self.figure_name,
            "total_passages": len(docs),
            "categories": {}
        }

        # Count by category
        for doc in docs:
            category = doc.get('metadata', {}).get('category', 'unknown')
            stats["categories"][category] = stats["categories"].get(category, 0) + 1

        return stats

    def purge_memory(self, pattern: str) -> Dict[str, Any]:
        """
        Purge/forget memories matching a pattern.

        Args:
            pattern: String to match in document source or content

        Returns:
            Results of purge operation
        """
        results = {
            "pattern": pattern,
            "purged_documents": 0,
            "errors": []
        }

        try:
            # Get all documents
            all_docs = self.vector_store.get_all_documents()

            # Find matching documents
            to_purge = []
            for doc in all_docs:
                # Check if pattern matches source or content
                source = doc.get('metadata', {}).get('source', '')
                content = doc.get('text', '')

                if pattern.lower() in source.lower() or pattern.lower() in content.lower():
                    to_purge.append(doc)

            if not to_purge:
                results["message"] = f"No documents found matching '{pattern}'"
                return results

            # Confirm and purge
            for doc in to_purge:
                try:
                    # Remove from vector store
                    doc_id = doc.get('id')
                    if doc_id:
                        self.vector_store.delete_document(doc_id)
                        results["purged_documents"] += 1
                except Exception as e:
                    results["errors"].append(f"Failed to purge document: {str(e)}")

            results["message"] = f"Purged {results['purged_documents']} documents"

            # Update metadata
            self.metadata["statistics"]["total_passages"] -= results["purged_documents"]
            self.metadata["statistics"]["last_purge"] = {
                "timestamp": datetime.now().isoformat(),
                "pattern": pattern,
                "documents_purged": results["purged_documents"]
            }
            self._save_metadata()

        except Exception as e:
            results["errors"].append(f"Purge failed: {str(e)}")

        return results

    def export_bundle(self, output_path: Optional[Path] = None) -> Path:
        """
        Export the bundle as a portable archive.

        Args:
            output_path: Where to save the archive

        Returns:
            Path to the created archive
        """
        import tarfile

        if output_path is None:
            output_path = Path(f"{self.figure_name}_bundle.tar.gz")

        with tarfile.open(output_path, "w:gz") as tar:
            tar.add(self.bundle_dir, arcname=self.figure_name)

        print(f"✓ Exported bundle to {output_path}")
        return output_path


class ResurrectionBot:
    """Simple bot interface for resurrection consciousness."""

    def __init__(self, figure_name: str):
        """Initialize bot with a specific figure."""
        self.consciousness = ResurrectionConsciousness(figure_name)
        self.figure_name = figure_name

    def chat(self, message: str) -> str:
        """
        Chat with the resurrection.

        Args:
            message: User's message

        Returns:
            Response from the figure
        """
        result = self.consciousness.query(message)
        return result.get("response", "I have no words for this.")

    def get_info(self) -> Dict[str, Any]:
        """Get information about this resurrection."""
        return self.consciousness.get_statistics()