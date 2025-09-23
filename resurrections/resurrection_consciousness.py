#!/usr/bin/env python3
"""
Resurrection Consciousness System
Each resurrection has its own consciousness bundle - data + vector database
Portable, distributable consciousness instances
"""

import os
import sys
import json
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional
import uuid
from datetime import datetime

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent.parent))

from retrieval.vector_store import VectorStore
from intelligence.llm import OllamaLLM, RAGSystem


class ResurrectionConsciousness:
    """
    A self-contained consciousness instance for a historical figure.
    Like Docker for consciousness - portable and bundleable.
    """

    def __init__(self,
                 figure_name: str,
                 bundle_dir: Optional[str] = None):
        """
        Initialize a resurrection consciousness.

        Args:
            figure_name: Name of the historical figure (e.g., 'jesus_christ')
            bundle_dir: Directory for this consciousness bundle (defaults to resurrections/bundles/{figure_name})
        """
        self.figure_name = figure_name

        # Set up bundle directory - this contains everything for this consciousness
        if bundle_dir:
            self.bundle_dir = Path(bundle_dir)
        else:
            self.bundle_dir = Path(__file__).parent / "bundles" / figure_name

        # Create directory structure
        self.bundle_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = self.bundle_dir / "data"
        self.vector_db_dir = self.bundle_dir / "vector_db"
        self.metadata_file = self.bundle_dir / "metadata.json"

        # Initialize components
        self.vector_store = None
        self.rag_system = None
        self.metadata = self._load_metadata()

        # Initialize vector store with figure-specific collection
        self._initialize_vector_store()

    def _load_metadata(self) -> Dict[str, Any]:
        """Load or create metadata for this consciousness."""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r') as f:
                return json.load(f)
        else:
            metadata = {
                "figure_name": self.figure_name,
                "created_at": datetime.now().isoformat(),
                "version": "1.0",
                "indexed_files": [],
                "personality": {},
                "statistics": {
                    "total_documents": 0,
                    "last_indexed": None
                }
            }
            self._save_metadata(metadata)
            return metadata

    def _save_metadata(self, metadata: Dict[str, Any]):
        """Save metadata to file."""
        with open(self.metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)

    def _initialize_vector_store(self):
        """Initialize the vector store for this resurrection."""
        # Each resurrection gets its own collection and persistence directory
        collection_name = f"resurrection_{self.figure_name}"

        self.vector_store = VectorStore(
            collection_name=collection_name,
            persist_directory=str(self.vector_db_dir),
            embedding_model="all-MiniLM-L6-v2"
        )

        # Try to initialize RAG system if Ollama is available
        try:
            llm = OllamaLLM()
            self.rag_system = RAGSystem(llm=llm, vector_store=self.vector_store)
        except:
            self.rag_system = None
            print(f"⚠️  LLM not available for {self.figure_name}")

    def index_texts(self, source_dir: Optional[str] = None) -> Dict[str, Any]:
        """
        Index all texts for this resurrection.

        Args:
            source_dir: Directory containing texts (defaults to data/figure_name)

        Returns:
            Indexing results
        """
        if not source_dir:
            # Try multiple possible locations for data
            possible_paths = [
                Path("resurrections/data") / self.figure_name,
                Path("data") / self.figure_name,
                Path(__file__).parent / "data" / self.figure_name
            ]

            for path in possible_paths:
                if path.exists():
                    source_dir = path
                    break
            else:
                return {
                    "error": f"Source directory not found. Tried: {[str(p) for p in possible_paths]}",
                    "indexed_files": [],
                    "total_documents": 0,
                    "errors": []
                }

        source_path = Path(source_dir)
        if not source_path.exists():
            return {
                "error": f"Source directory not found: {source_path}",
                "indexed_files": [],
                "total_documents": 0,
                "errors": []
            }

        results = {
            "indexed_files": [],
            "total_documents": 0,
            "errors": []
        }

        # Copy data to bundle if not already there
        if source_path != self.data_dir:
            if self.data_dir.exists():
                shutil.rmtree(self.data_dir)
            shutil.copytree(source_path, self.data_dir)

        # Index all text files
        for txt_file in self.data_dir.glob("**/*.txt"):
            try:
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Split into chunks (simple paragraph-based for now)
                chunks = [c.strip() for c in content.split('\n\n') if c.strip()]

                # Create documents with metadata
                documents = []
                metadatas = []
                ids = []

                for i, chunk in enumerate(chunks):
                    if len(chunk) > 50:  # Skip very short chunks
                        doc_id = f"{txt_file.stem}_{i}_{uuid.uuid4().hex[:8]}"
                        documents.append(chunk)
                        metadatas.append({
                            "source": str(txt_file.relative_to(self.data_dir)),
                            "figure": self.figure_name,
                            "chunk_index": i,
                            "category": txt_file.parent.name
                        })
                        ids.append(doc_id)

                # Add to vector store
                if documents:
                    self.vector_store.add_documents(
                        documents=documents,
                        metadatas=metadatas,
                        ids=ids
                    )
                    results["indexed_files"].append(str(txt_file))
                    results["total_documents"] += len(documents)

            except Exception as e:
                results["errors"].append(f"Error indexing {txt_file}: {str(e)}")

        # Update metadata
        self.metadata["indexed_files"] = results["indexed_files"]
        self.metadata["statistics"]["total_documents"] = results["total_documents"]
        self.metadata["statistics"]["last_indexed"] = datetime.now().isoformat()
        self._save_metadata(self.metadata)

        return results

    def query(self,
              question: str,
              use_llm: bool = True,
              top_k: int = 3) -> Dict[str, Any]:
        """
        Query the consciousness with RAG.

        Args:
            question: The question to ask
            use_llm: Whether to use LLM for response generation
            top_k: Number of relevant documents to retrieve

        Returns:
            Query results with sources and response
        """
        if not self.vector_store:
            return {"error": "Vector store not initialized"}

        # Search for relevant documents
        search_results = self.vector_store.search(
            query=question,
            k=top_k
        )

        response = {
            "question": question,
            "sources": [],
            "response": None
        }

        # Extract sources
        for result in search_results:
            doc = result.get('document', '')
            metadata = result.get('metadata', {})
            score = result.get('score', 0)
            response["sources"].append({
                "text": doc[:200] + "..." if len(doc) > 200 else doc,
                "source": metadata.get("source", "unknown"),
                "score": score
            })

        # Generate response with LLM if available
        if use_llm and self.rag_system:
            context = "\n\n".join([result['document'] for result in search_results])

            # Add personality context
            personality_prompt = self._get_personality_prompt()

            full_prompt = f"""{personality_prompt}

Based on these texts from {self.figure_name}:

{context}

Question: {question}

Respond as {self.figure_name} would, using their voice and wisdom:"""

            try:
                llm_response = self.rag_system.llm.generate(full_prompt)
                response["response"] = llm_response
            except Exception as e:
                response["error"] = f"LLM generation failed: {str(e)}"
        else:
            # Fallback to simple retrieval
            if search_results:
                response["response"] = search_results[0].get('document', '')
            else:
                response["response"] = "I have no knowledge of this in my texts."

        return response

    def _get_personality_prompt(self) -> str:
        """Get personality prompt for this figure."""
        if self.figure_name == "jesus_christ":
            return """You are Jesus Christ. Speak with:
- Simple, direct language
- Parables and everyday examples
- Questions that make people think
- Compassion for all
- Wisdom rooted in love"""
        else:
            return f"You are {self.figure_name}. Speak in their authentic voice."

    def process_inbox(self) -> Dict[str, Any]:
        """
        Process new texts in the bundle's inbox directory.
        Automatically splits large texts into manageable chunks.

        Returns:
            Processing results
        """
        inbox_dir = self.bundle_dir / "inbox"

        # Create inbox if it doesn't exist
        inbox_dir.mkdir(parents=True, exist_ok=True)

        results = {
            "processed_files": [],
            "indexed_documents": 0,
            "errors": []
        }

        # Find all text files in inbox
        text_files = list(inbox_dir.glob("*.txt")) + list(inbox_dir.glob("*.md"))

        if not text_files:
            results["message"] = "No new texts found in inbox"
            return results

        print(f"📥 Found {len(text_files)} new texts to process")

        for txt_file in text_files:
            try:
                # Read the file
                with open(txt_file, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if file needs splitting (>10KB or has chapter structure)
                if len(content) > 10000 or 'CHAPTER' in content.upper()[:1000]:
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
            "files": results["processed_files"],
            "documents_added": results["indexed_documents"]
        })

        self._save_metadata(self.metadata)

        return results

    def _split_large_text(self, file_path: Path, content: str) -> List[Path]:
        """Split large text into chapter/section files"""
        import re

        split_files = []
        inbox_dir = file_path.parent

        # Detect and split by chapters
        chapter_pattern = r'(CHAPTER\s+[IVXLCDM]+|CHAPTER\s+\d+|Chapter\s+\d+)'
        matches = list(re.finditer(chapter_pattern, content, re.IGNORECASE))

        if len(matches) > 2:
            # Split by chapters
            for i, match in enumerate(matches):
                start = match.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(content)

                chapter_text = content[start:end].strip()
                if len(chapter_text) > 100:
                    chapter_num = i + 1
                    new_file = inbox_dir / f"{file_path.stem}_ch{chapter_num:03d}.txt"

                    with open(new_file, 'w', encoding='utf-8') as f:
                        f.write(chapter_text)

                    split_files.append(new_file)
        else:
            # Split by size (every 2000 chars with paragraph boundaries)
            chunks = []
            current_chunk = []
            current_size = 0

            paragraphs = content.split('\n\n')
            for para in paragraphs:
                para = para.strip()
                if not para:
                    continue

                if current_size + len(para) > 2000 and current_chunk:
                    chunks.append('\n\n'.join(current_chunk))
                    current_chunk = [para]
                    current_size = len(para)
                else:
                    current_chunk.append(para)
                    current_size += len(para)

            if current_chunk:
                chunks.append('\n\n'.join(current_chunk))

            # Save chunks
            for i, chunk in enumerate(chunks):
                new_file = inbox_dir / f"{file_path.stem}_part{i+1:03d}.txt"
                with open(new_file, 'w', encoding='utf-8') as f:
                    f.write(chunk)
                split_files.append(new_file)

        return split_files

    def _process_single_file(self, txt_file: Path, results: Dict[str, Any]):
        """Process a single text file"""
        try:
            with open(txt_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Determine category (generalized)
            category = self._determine_category(txt_file.name, content)

            # Create target directory
            target_dir = self.data_dir / category
            target_dir.mkdir(parents=True, exist_ok=True)

            # Move file to appropriate data directory
            target_path = target_dir / txt_file.name
            shutil.move(str(txt_file), str(target_path))

            # Index the content
            chunks = [c.strip() for c in content.split('\n\n') if c.strip() and len(c.strip()) > 50]

            documents = []
            metadatas = []
            ids = []

            for i, chunk in enumerate(chunks):
                if len(chunk) > 50:
                    doc_id = f"{txt_file.stem}_{i}_{uuid.uuid4().hex[:8]}"
                    documents.append(chunk)
                    metadatas.append({
                        "source": str(target_path.relative_to(self.data_dir)),
                        "figure": self.figure_name,
                        "chunk_index": i,
                        "category": category,
                        "added_date": datetime.now().isoformat()
                    })
                    ids.append(doc_id)

            # Add to vector store
            if documents:
                self.vector_store.add_documents(
                    documents=documents,
                    metadatas=metadatas,
                    ids=ids
                )

                results["processed_files"].append(txt_file.name)
                results["indexed_documents"] += len(documents)

                print(f"  ✓ Processed {txt_file.name}: {len(documents)} chunks indexed")

        except Exception as e:
            error_msg = f"Error processing {txt_file.name}: {str(e)}"
            results["errors"].append(error_msg)
            print(f"  ✗ {error_msg}")

    def _determine_category(self, filename: str, content: str) -> str:
        """
        Determine the appropriate category for a text (generalized).

        Args:
            filename: Name of the file
            content: Content of the file

        Returns:
            Category name (subdirectory in data/)
        """
        filename_lower = filename.lower()
        content_lower = content.lower()[:1000]  # Check first 1000 chars

        # General categorization (not specific to any figure)
        if any(term in filename_lower for term in ["primary", "source", "original", "canon"]):
            return "primary_sources"
        elif any(term in filename_lower for term in ["commentary", "analysis", "interpret"]):
            return "commentary"
        elif any(term in filename_lower for term in ["letter", "epistle", "correspond"]):
            return "correspondence"
        elif any(term in filename_lower for term in ["biography", "life", "history"]):
            return "biographical"
        elif any(term in filename_lower for term in ["teach", "lesson", "discourse"]):
            return "teachings"
        elif any(term in filename_lower for term in ["ritual", "practice", "ceremony"]):
            return "practices"

        # Check content for general patterns
        if any(term in content_lower for term in ["chapter", "verse", "book"]):
            return "texts"
        elif any(term in content_lower for term in ["said", "spoke", "answered"]):
            return "dialogues"

        # Default category
        return "general"

    def purge_memory(self, category: Optional[str] = None, source_pattern: Optional[str] = None) -> Dict[str, Any]:
        """
        Purge/forget specific memories from the consciousness.

        Args:
            category: Category to purge (e.g., 'gnostic', 'supplemental')
            source_pattern: Pattern to match in source filenames

        Returns:
            Purge results
        """
        results = {
            "purged_files": [],
            "purged_documents": 0,
            "errors": []
        }

        print(f"🧹 Purging memories...")

        # Get all documents from vector store
        # This is a simplified version - actual implementation depends on vector store API

        if category:
            # Remove files from category directory
            category_dir = self.data_dir / category
            if category_dir.exists():
                for file in category_dir.glob("*"):
                    try:
                        file.unlink()
                        results["purged_files"].append(str(file.name))
                        print(f"  ✓ Purged {file.name}")
                    except Exception as e:
                        results["errors"].append(f"Failed to delete {file.name}: {e}")

                # Try to remove the directory if empty
                try:
                    category_dir.rmdir()
                except:
                    pass  # Directory not empty or other error

        if source_pattern:
            # Search all categories for matching files
            for dir_path in self.data_dir.glob("*"):
                if dir_path.is_dir():
                    for file in dir_path.glob(f"*{source_pattern}*"):
                        try:
                            file.unlink()
                            results["purged_files"].append(str(file.name))
                            print(f"  ✓ Purged {file.name}")
                        except Exception as e:
                            results["errors"].append(f"Failed to delete {file.name}: {e}")

        # Update metadata
        if results["purged_files"]:
            # This is simplified - would need to actually remove from vector store
            self.metadata["statistics"]["last_purge"] = datetime.now().isoformat()

            if "purge_history" not in self.metadata:
                self.metadata["purge_history"] = []

            self.metadata["purge_history"].append({
                "timestamp": datetime.now().isoformat(),
                "category": category,
                "pattern": source_pattern,
                "files_purged": results["purged_files"]
            })

            self._save_metadata(self.metadata)

        return results

    def export_bundle(self, output_path: str) -> bool:
        """
        Export the entire consciousness bundle as a portable package.

        Args:
            output_path: Path for the exported bundle (tar.gz)

        Returns:
            Success status
        """
        import tarfile

        try:
            with tarfile.open(output_path, "w:gz") as tar:
                tar.add(self.bundle_dir, arcname=self.figure_name)
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False

    def import_bundle(self, bundle_path: str) -> bool:
        """
        Import a consciousness bundle.

        Args:
            bundle_path: Path to the bundle file (tar.gz)

        Returns:
            Success status
        """
        import tarfile

        try:
            with tarfile.open(bundle_path, "r:gz") as tar:
                tar.extractall(self.bundle_dir.parent)

            # Reload metadata
            self.metadata = self._load_metadata()
            self._initialize_vector_store()
            return True
        except Exception as e:
            print(f"Import failed: {e}")
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about this consciousness."""
        stats = self.vector_store.get_stats() if self.vector_store else {}
        stats.update({
            "figure_name": self.figure_name,
            "bundle_size": sum(f.stat().st_size for f in self.bundle_dir.glob("**/*") if f.is_file()),
            "metadata": self.metadata
        })
        return stats


class ResurrectionBot:
    """Interactive bot using resurrection consciousness."""

    def __init__(self, figure_name: str):
        """Initialize bot with a specific resurrection."""
        print(f"\n🔄 Loading {figure_name} consciousness...")
        self.consciousness = ResurrectionConsciousness(figure_name)

        # Check if already indexed
        stats = self.consciousness.get_stats()
        if stats.get("metadata", {}).get("statistics", {}).get("total_documents", 0) == 0:
            print("📚 Indexing texts...")
            results = self.consciousness.index_texts()
            if "error" in results:
                print(f"⚠️  {results['error']}")
                print("\nPlease ensure Gospel texts are downloaded:")
                print("  python3 download_gospels.py")
            else:
                print(f"✓ Indexed {results['total_documents']} passages from {len(results['indexed_files'])} files")
        else:
            print(f"✓ Found existing index with {stats['metadata']['statistics']['total_documents']} passages")

    def respond(self, query: str) -> str:
        """Generate a response to user query."""
        result = self.consciousness.query(query, use_llm=True)

        if result.get("response"):
            return result["response"]
        elif result.get("sources"):
            # Fallback to best source
            return result["sources"][0]["text"]
        else:
            return "I cannot find wisdom on this matter in my texts."