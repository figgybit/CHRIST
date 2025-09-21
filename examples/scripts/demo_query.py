#!/usr/bin/env python3
"""
Demo script showing how to query the C.H.R.I.S.T. system.
"""

import sys
import asyncio
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from retrieval.vector_store import VectorStore, HybridRetriever
from retrieval.llm_integration import LLMProvider, RAGSystem
from consciousness.database import get_db_manager


async def demo_queries():
    """Demonstrate various query capabilities."""

    print("=" * 60)
    print("C.H.R.I.S.T. System - Query Demonstrations")
    print("=" * 60)

    # Initialize components
    vector_store = VectorStore()
    llm_provider = LLMProvider(provider="mock")  # Use mock for demo
    rag_system = RAGSystem(vector_store, llm_provider)
    db_manager = get_db_manager()

    # 1. Semantic Search
    print("\n1. SEMANTIC SEARCH")
    print("-" * 40)

    queries = [
        "privacy and ethics",
        "family memories",
        "artificial intelligence",
        "personal growth",
        "consciousness preservation"
    ]

    for query in queries:
        print(f"\nSearching for: '{query}'")
        try:
            results = vector_store.search(query, k=3)
            if results:
                for i, result in enumerate(results, 1):
                    score = result.get('score', 0)
                    doc = result.get('document', '')[:100]  # First 100 chars
                    print(f"  {i}. (Score: {score:.2f}) {doc}...")
            else:
                print("  No results found")
        except Exception as e:
            print(f"  Error: {e}")

    # 2. Question Answering
    print("\n2. QUESTION ANSWERING")
    print("-" * 40)

    questions = [
        "What are my goals?",
        "What have I been thinking about lately?",
        "What did I say about privacy?",
        "Who invited me to speak at a conference?",
        "What patterns have I noticed in my behavior?"
    ]

    for question in questions:
        print(f"\nQ: {question}")
        try:
            response = rag_system.query(question, k=5, use_context=True)
            answer = response.get('answer', 'No answer generated')
            print(f"A: {answer[:200]}...")  # First 200 chars of answer

            if response.get('sources'):
                print(f"   (Based on {len(response['sources'])} sources)")
        except Exception as e:
            print(f"A: Error - {e}")

    # 3. Temporal Queries
    print("\n3. TEMPORAL QUERIES")
    print("-" * 40)

    print("\nQuerying events by date range...")
    try:
        from datetime import datetime, timedelta

        # Last 30 days
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)

        events = db_manager.query_events(
            start_date=start_date,
            end_date=end_date,
            limit=5
        )

        print(f"Found {len(events)} recent events:")
        for event in events:
            event_type = event.get('type', 'unknown')
            timestamp = event.get('timestamp', 'no date')
            print(f"  - {event_type} ({timestamp})")

    except Exception as e:
        print(f"Error querying events: {e}")

    # 4. Hybrid Retrieval
    print("\n4. HYBRID RETRIEVAL")
    print("-" * 40)

    print("\nTesting hybrid search (semantic + keyword)...")
    try:
        hybrid = HybridRetriever(vector_store)

        query = "consciousness AI ethics"
        print(f"Query: '{query}'")

        results = hybrid.retrieve(query, k=5)
        print(f"Found {len(results)} results combining semantic and keyword matching")

        for i, result in enumerate(results[:3], 1):
            doc = result.get('document', '')[:100]
            print(f"  {i}. {doc}...")

    except Exception as e:
        print(f"Error in hybrid search: {e}")

    # 5. Reflection Generation
    print("\n5. REFLECTION GENERATION")
    print("-" * 40)

    print("\nGenerating weekly reflection...")
    try:
        reflection = rag_system.reflect(
            time_period={'start': 'last week', 'end': 'today'},
            focus_areas=['personal growth', 'technology', 'family']
        )

        print("Reflection Summary:")
        print(reflection[:300] + "...")  # First 300 chars

    except Exception as e:
        print(f"Error generating reflection: {e}")

    # 6. Statistics
    print("\n6. SYSTEM STATISTICS")
    print("-" * 40)

    try:
        all_events = db_manager.query_events(limit=10000)

        # Count by type
        type_counts = {}
        for event in all_events:
            event_type = event.get('type', 'unknown')
            type_counts[event_type] = type_counts.get(event_type, 0) + 1

        print(f"\nTotal stored events: {len(all_events)}")
        print("\nBreakdown by type:")
        for event_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {event_type}: {count}")

        # Memory usage estimate
        total_chars = sum(len(str(event.get('content', ''))) for event in all_events)
        print(f"\nEstimated memory usage: {total_chars:,} characters")
        print(f"Approximate size: {total_chars / 1024:.1f} KB")

    except Exception as e:
        print(f"Error calculating statistics: {e}")

    print("\n" + "=" * 60)
    print("Query demonstrations complete!")
    print("=" * 60)


async def interactive_mode():
    """Interactive query mode."""

    print("\n" + "=" * 60)
    print("INTERACTIVE QUERY MODE")
    print("Type 'exit' to quit")
    print("=" * 60)

    vector_store = VectorStore()
    llm_provider = LLMProvider(provider="mock")
    rag_system = RAGSystem(vector_store, llm_provider)

    while True:
        try:
            query = input("\nEnter your query: ").strip()

            if query.lower() == 'exit':
                print("Goodbye!")
                break

            if not query:
                continue

            # Perform search
            print("\nSearching...")
            results = vector_store.search(query, k=5)

            if results:
                print(f"\nFound {len(results)} results:")
                for i, result in enumerate(results, 1):
                    doc = result.get('document', '')[:150]
                    score = result.get('score', 0)
                    print(f"\n{i}. (Relevance: {score:.1%})")
                    print(f"   {doc}...")
            else:
                print("No results found.")

            # Generate answer
            print("\nGenerating answer...")
            response = rag_system.query(query, k=3)
            answer = response.get('answer', 'No answer available')
            print(f"\nAnswer: {answer}")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Goodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='C.H.R.I.S.T. Query Demo')
    parser.add_argument('--interactive', '-i', action='store_true',
                        help='Run in interactive mode')

    args = parser.parse_args()

    if args.interactive:
        asyncio.run(interactive_mode())
    else:
        asyncio.run(demo_queries())