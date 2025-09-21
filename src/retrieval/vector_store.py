"""
Vector database integration for RAG (Retrieval-Augmented Generation).
"""

import os
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import numpy as np

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False
    print("ChromaDB not installed. Install with: pip install chromadb")

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False
    print("Sentence transformers not installed. Install with: pip install sentence-transformers")


class VectorStore:
    """
    Vector store for semantic search and retrieval.
    Supports ChromaDB with fallback to simple numpy-based search.
    """

    def __init__(
        self,
        collection_name: str = "consciousness",
        persist_directory: str = "./data/chroma",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize vector store.

        Args:
            collection_name: Name of the collection
            persist_directory: Directory to persist ChromaDB
            embedding_model: Name of the embedding model
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_model_name = embedding_model

        # Initialize embedding model
        if EMBEDDINGS_AVAILABLE:
            self.embedding_model = SentenceTransformer(embedding_model)
            self.embedding_dimension = self.embedding_model.get_sentence_embedding_dimension()
        else:
            self.embedding_model = None
            self.embedding_dimension = 384  # Default dimension

        # Initialize ChromaDB if available
        if CHROMADB_AVAILABLE:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )

            # Get or create collection
            try:
                self.collection = self.client.get_collection(collection_name)
            except:
                self.collection = self.client.create_collection(
                    name=collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
        else:
            self.client = None
            self.collection = None
            # Fallback to in-memory storage
            self.memory_store = {
                'ids': [],
                'embeddings': [],
                'documents': [],
                'metadatas': []
            }

    def add_documents(
        self,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """
        Add documents to the vector store.

        Args:
            documents: List of documents to add
            metadatas: Optional metadata for each document
            ids: Optional IDs for documents

        Returns:
            List of document IDs
        """
        if not documents:
            return []

        # Generate IDs if not provided
        if ids is None:
            import uuid
            ids = [str(uuid.uuid4()) for _ in documents]

        # Generate embeddings
        embeddings = self._embed_texts(documents)

        # Prepare metadata
        if metadatas is None:
            metadatas = [{}] * len(documents)

        # Add timestamp to metadata
        for metadata in metadatas:
            if 'timestamp' not in metadata:
                metadata['timestamp'] = datetime.now().isoformat()

        # Store in vector database
        if self.collection is not None:
            self.collection.add(
                embeddings=embeddings.tolist() if isinstance(embeddings, np.ndarray) else embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        else:
            # Fallback to memory store
            self.memory_store['ids'].extend(ids)
            self.memory_store['embeddings'].extend(embeddings.tolist())
            self.memory_store['documents'].extend(documents)
            self.memory_store['metadatas'].extend(metadatas)

        return ids

    def search(
        self,
        query: str,
        k: int = 5,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Query string
            k: Number of results to return
            filter: Optional metadata filter

        Returns:
            List of search results with documents, metadata, and scores
        """
        # Generate query embedding
        query_embedding = self._embed_texts([query])[0]

        if self.collection is not None:
            # Use ChromaDB search
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=k,
                where=filter
            )

            # Format results
            formatted_results = []
            for i in range(len(results['ids'][0])):
                formatted_results.append({
                    'id': results['ids'][0][i],
                    'document': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i],
                    'score': 1 - results['distances'][0][i]  # Convert distance to similarity
                })

            return formatted_results
        else:
            # Fallback to numpy search
            return self._numpy_search(query_embedding, k, filter)

    def _numpy_search(
        self,
        query_embedding: np.ndarray,
        k: int,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Fallback numpy-based similarity search.
        """
        if not self.memory_store['embeddings']:
            return []

        # Convert to numpy array
        embeddings = np.array(self.memory_store['embeddings'])

        # Calculate cosine similarity
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        embeddings_norm = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        similarities = np.dot(embeddings_norm, query_norm)

        # Apply filter if provided
        if filter:
            valid_indices = []
            for i, metadata in enumerate(self.memory_store['metadatas']):
                if all(metadata.get(key) == value for key, value in filter.items()):
                    valid_indices.append(i)

            if not valid_indices:
                return []

            similarities = similarities[valid_indices]
            filtered_indices = np.array(valid_indices)
        else:
            filtered_indices = np.arange(len(similarities))

        # Get top k results
        top_k_indices = np.argsort(similarities)[-k:][::-1]

        # Format results
        results = []
        for idx in top_k_indices:
            original_idx = filtered_indices[idx]
            results.append({
                'id': self.memory_store['ids'][original_idx],
                'document': self.memory_store['documents'][original_idx],
                'metadata': self.memory_store['metadatas'][original_idx],
                'score': float(similarities[idx])
            })

        return results

    def _embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for texts.
        """
        if self.embedding_model is not None:
            return self.embedding_model.encode(texts, convert_to_numpy=True)
        else:
            # Fallback to random embeddings (for testing only)
            import hashlib
            embeddings = []
            for text in texts:
                # Generate deterministic "embedding" from text hash
                hash_obj = hashlib.sha256(text.encode())
                hash_bytes = hash_obj.digest()
                # Convert to float array
                embedding = np.frombuffer(hash_bytes, dtype=np.uint8)[:self.embedding_dimension]
                embedding = embedding.astype(np.float32) / 255.0
                # Pad if necessary
                if len(embedding) < self.embedding_dimension:
                    embedding = np.pad(embedding, (0, self.embedding_dimension - len(embedding)))
                embeddings.append(embedding)
            return np.array(embeddings)

    def delete(self, ids: List[str]):
        """
        Delete documents by IDs.
        """
        if self.collection is not None:
            self.collection.delete(ids=ids)
        else:
            # Remove from memory store
            for id_to_remove in ids:
                if id_to_remove in self.memory_store['ids']:
                    idx = self.memory_store['ids'].index(id_to_remove)
                    self.memory_store['ids'].pop(idx)
                    self.memory_store['embeddings'].pop(idx)
                    self.memory_store['documents'].pop(idx)
                    self.memory_store['metadatas'].pop(idx)

    def get_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        """
        if self.collection is not None:
            count = self.collection.count()
        else:
            count = len(self.memory_store['ids'])

        return {
            'total_documents': count,
            'storage_type': 'chromadb' if self.collection else 'memory',
            'embedding_model': self.embedding_model_name,
            'embedding_dimension': self.embedding_dimension
        }

    def clear(self):
        """
        Clear all documents from the store.
        """
        if self.collection is not None:
            # Delete and recreate collection
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
        else:
            # Clear memory store
            self.memory_store = {
                'ids': [],
                'embeddings': [],
                'documents': [],
                'metadatas': []
            }


class HybridRetriever:
    """
    Hybrid retriever combining vector search with keyword search.
    """

    def __init__(self, vector_store: VectorStore):
        """
        Initialize hybrid retriever.

        Args:
            vector_store: Vector store instance
        """
        self.vector_store = vector_store

    def retrieve(
        self,
        query: str,
        k: int = 5,
        semantic_weight: float = 0.7,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve documents using hybrid search.

        Args:
            query: Query string
            k: Number of results
            semantic_weight: Weight for semantic search (vs keyword)
            filter: Optional metadata filter

        Returns:
            List of retrieved documents
        """
        # Semantic search
        semantic_results = self.vector_store.search(query, k=k*2, filter=filter)

        # Keyword search (simple implementation)
        keyword_results = self._keyword_search(query, k=k*2, filter=filter)

        # Merge and rerank
        merged_results = self._merge_results(
            semantic_results,
            keyword_results,
            semantic_weight
        )

        return merged_results[:k]

    def _keyword_search(
        self,
        query: str,
        k: int,
        filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Simple keyword search.
        """
        # This is a placeholder - in production, use Elasticsearch or similar
        results = []
        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Search in memory store or get all documents
        if hasattr(self.vector_store, 'memory_store'):
            documents = self.vector_store.memory_store['documents']
            metadatas = self.vector_store.memory_store['metadatas']
            ids = self.vector_store.memory_store['ids']

            for i, doc in enumerate(documents):
                # Apply filter
                if filter and not all(metadatas[i].get(k) == v for k, v in filter.items()):
                    continue

                # Calculate keyword score
                doc_lower = doc.lower()
                doc_words = set(doc_lower.split())
                common_words = query_words.intersection(doc_words)
                score = len(common_words) / len(query_words) if query_words else 0

                if score > 0:
                    results.append({
                        'id': ids[i],
                        'document': doc,
                        'metadata': metadatas[i],
                        'score': score
                    })

        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:k]

    def _merge_results(
        self,
        semantic_results: List[Dict[str, Any]],
        keyword_results: List[Dict[str, Any]],
        semantic_weight: float
    ) -> List[Dict[str, Any]]:
        """
        Merge and rerank results from different search methods.
        """
        # Create a unified score for each document
        doc_scores = {}

        # Add semantic search results
        for result in semantic_results:
            doc_id = result['id']
            doc_scores[doc_id] = {
                'document': result['document'],
                'metadata': result['metadata'],
                'semantic_score': result['score'],
                'keyword_score': 0,
                'final_score': result['score'] * semantic_weight
            }

        # Add keyword search results
        keyword_weight = 1 - semantic_weight
        for result in keyword_results:
            doc_id = result['id']
            if doc_id in doc_scores:
                doc_scores[doc_id]['keyword_score'] = result['score']
                doc_scores[doc_id]['final_score'] = (
                    doc_scores[doc_id]['semantic_score'] * semantic_weight +
                    result['score'] * keyword_weight
                )
            else:
                doc_scores[doc_id] = {
                    'document': result['document'],
                    'metadata': result['metadata'],
                    'semantic_score': 0,
                    'keyword_score': result['score'],
                    'final_score': result['score'] * keyword_weight
                }

        # Convert to list and sort
        final_results = [
            {
                'id': doc_id,
                'document': data['document'],
                'metadata': data['metadata'],
                'score': data['final_score'],
                'semantic_score': data['semantic_score'],
                'keyword_score': data['keyword_score']
            }
            for doc_id, data in doc_scores.items()
        ]

        final_results.sort(key=lambda x: x['score'], reverse=True)
        return final_results