#!/usr/bin/env python3
"""
Test RAG (Retrieval-Augmented Generation) with Ollama.
Demonstrates consciousness data retrieval and AI-enhanced responses.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from consciousness.database import init_database
from retrieval.vector_store import VectorStore
from intelligence.llm import OllamaLLM, RAGSystem


def test_rag_system():
    """Test the complete RAG pipeline with Ollama."""

    print("=" * 60)
    print("C.H.R.I.S.T. RAG System Test with Ollama")
    print("=" * 60)
    print()

    # Initialize components
    print("🔧 Initializing components...")

    # Database
    db = init_database()
    print("  ✓ Database ready")

    # Vector store
    vector_store = VectorStore()
    print("  ✓ Vector store ready")

    # Check if we have data
    stats = vector_store.get_stats()
    doc_count = stats['total_documents']

    if doc_count == 0:
        print("\n⚠️ No documents in vector store!")
        print("Run 'python demo_clean.py' first to load demo data")
        return

    print(f"  ✓ Found {doc_count} documents in vector store")

    # Initialize Ollama
    try:
        llm = OllamaLLM()
        print(f"  ✓ Ollama connected (model: {llm.model_name})")
    except Exception as e:
        print(f"\n❌ Failed to connect to Ollama: {e}")
        print("Make sure Ollama is running: 'ollama serve'")
        return

    # Create RAG system
    rag = RAGSystem(llm=llm, vector_store=vector_store)
    print("  ✓ RAG system initialized")

    print("\n" + "=" * 60)
    print("Testing RAG Queries")
    print("=" * 60)

    # Test queries
    test_queries = [
        "What insights about consciousness were discovered during meditation?",
        "What did grandmother say about libraries and consciousness?",
        "Explain the relationship between quantum mechanics and consciousness",
        "What are the ethical implications of digital consciousness?",
        "How does the C.H.R.I.S.T. project capture and preserve consciousness?"
    ]

    for i, question in enumerate(test_queries, 1):
        print(f"\n🤔 Question {i}: {question}")
        print("-" * 40)

        # Get RAG response
        result = rag.query(
            question=question,
            k=3,  # Use top 3 relevant documents
            temperature=0.7,
            max_tokens=200
        )

        # Show answer
        print(f"🤖 Answer: {result['answer']}")

        # Show sources
        if result['sources']:
            print("\n📚 Sources used:")
            for j, source in enumerate(result['sources'], 1):
                source_name = source['source'].split('/')[-1]
                score = source['score']
                print(f"  {j}. {source_name} (relevance: {score:.2f})")

        print("=" * 60)

        # Ask if user wants to continue
        if i < len(test_queries):
            response = input("\nPress Enter for next question (or 'q' to quit): ")
            if response.lower() == 'q':
                break

    # Interactive mode
    print("\n" + "=" * 60)
    print("Interactive RAG Chat")
    print("=" * 60)
    print("You can now ask your own questions about the consciousness data.")
    print("Type 'exit' to quit.\n")

    while True:
        question = input("Your question: ").strip()

        if question.lower() in ['exit', 'quit', 'q']:
            print("👋 Goodbye!")
            break

        if not question:
            continue

        print("\n🔍 Searching consciousness data...")
        result = rag.query(
            question=question,
            k=5,
            temperature=0.8,
            max_tokens=300
        )

        print(f"\n🤖 Response:\n{result['answer']}")

        if result['sources']:
            print("\n📚 Based on:")
            for source in result['sources'][:3]:
                source_name = source['source'].split('/')[-1]
                print(f"  - {source_name}")

        print("\n" + "-" * 60)


if __name__ == "__main__":
    test_rag_system()