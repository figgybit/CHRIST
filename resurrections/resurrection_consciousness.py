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