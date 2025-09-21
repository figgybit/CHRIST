#!/usr/bin/env python3
"""
Demo RAG system with Ollama - Non-interactive version.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from consciousness.database import init_database
from retrieval.vector_store import VectorStore
from intelligence.llm import OllamaLLM, RAGSystem


def demo_rag():
    """Demo the RAG system."""

    print("=" * 70)
    print(" C.H.R.I.S.T. Consciousness RAG Demo with Local Ollama")
    print("=" * 70)
    print()

    # Initialize
    print("Initializing system...")
    db = init_database()
    vector_store = VectorStore()

    # Check data
    stats = vector_store.get_stats()
    if stats['total_documents'] == 0:
        print("❌ No documents found. Run 'python demo_clean.py' first!")
        return

    print(f"✅ Found {stats['total_documents']} consciousness documents")

    # Initialize Ollama
    try:
        llm = OllamaLLM()
        print(f"✅ Using Ollama model: {llm.model_name}\n")
    except Exception as e:
        print(f"❌ Ollama error: {e}")
        print("Make sure Ollama is running: 'ollama serve'")
        return

    # Create RAG
    rag = RAGSystem(llm=llm, vector_store=vector_store)

    # Demo queries
    queries = [
        "What insights about consciousness emerged during meditation?",
        "What did grandmother say about libraries?",
        "How does the C.H.R.I.S.T. system work technically?",
        "What is the relationship between dreams and data?"
    ]

    for question in queries:
        print("=" * 70)
        print(f"❓ Question: {question}")
        print("-" * 70)

        result = rag.query(question, k=3, temperature=0.7, max_tokens=150)

        print(f"\n💡 Answer:\n{result['answer']}")

        if result['sources']:
            print("\n📄 Sources:")
            for i, source in enumerate(result['sources'], 1):
                name = source['source'].split('/')[-1]
                score = source['score']
                print(f"   {i}. {name} (relevance: {score:.2f})")

        print()

    print("=" * 70)
    print("✨ RAG demo complete! The system can answer questions using")
    print("   retrieved consciousness data and local AI generation.")
    print("=" * 70)


if __name__ == "__main__":
    demo_rag()