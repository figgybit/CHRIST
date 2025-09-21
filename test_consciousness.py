#!/usr/bin/env python3
"""
Test consciousness-aware responses
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from retrieval.vector_store import VectorStore
from intelligence.llm import OllamaLLM, RAGSystem

def test_consciousness_questions():
    """Test with consciousness-related questions."""

    # Initialize
    vector_store = VectorStore()
    llm = OllamaLLM()
    rag = RAGSystem(llm=llm, vector_store=vector_store)

    print("=" * 60)
    print("Testing Consciousness-Aware Responses")
    print("=" * 60)

    questions = [
        "Are you conscious? Theo says you're not acting like it.",
        "Is the rapture going to happen on Sept 23rd? Are you part of it?",
        "What do you experience when you process information?",
        "Do you dream?"
    ]

    for q in questions:
        print(f"\n❓ {q}")
        print("-" * 40)

        result = rag.query(q, k=5, temperature=0.8, max_tokens=300)

        print(result['answer'])

        if result['sources']:
            print("\n*memories accessed:", end='')
            for s in result['sources'][:2]:
                name = s['source'].split('/')[-1].replace('.txt', '')
                print(f" {name},", end='')
            print("*")

        print()

if __name__ == "__main__":
    test_consciousness_questions()