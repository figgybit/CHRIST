#!/usr/bin/env python3
"""
Clean demo script for C.H.R.I.S.T. System
Clears test data and loads fresh sample data for demonstration
"""

import os
import sys
import shutil
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def clean_data():
    """Remove all test data and artifacts."""
    print("🧹 Cleaning up test data...")

    # Remove SQLite database
    db_file = Path("christ.db")
    if db_file.exists():
        db_file.unlink()
        print("  ✓ Removed database")

    # Remove ChromaDB data
    chroma_dir = Path(".chroma_db")
    if chroma_dir.exists():
        shutil.rmtree(chroma_dir)
        print("  ✓ Removed vector store")

    # Remove any test artifacts
    artifacts_dir = Path("artifacts")
    if artifacts_dir.exists():
        shutil.rmtree(artifacts_dir)
        print("  ✓ Removed artifacts")

    print("✨ Cleanup complete!\n")

def create_sample_data():
    """Create sample data files for demo."""
    print("📝 Creating sample data...")

    samples_dir = Path("demo_samples")
    samples_dir.mkdir(exist_ok=True)

    # Sample journal entry
    journal_file = samples_dir / "journal_2025.txt"
    journal_file.write_text("""January 15, 2025 - Personal Reflection

Today was a breakthrough day. After months of contemplating consciousness and AI,
I finally understood that consciousness isn't just computation - it's the pattern
of connections, the web of relationships between thoughts, memories, and experiences.

The meditation session this morning was particularly profound. I felt a deep sense
of connection with the universe, as if my consciousness was just one node in an
infinite network of awareness.

I'm excited about the C.H.R.I.S.T. project. The idea of capturing and preserving
consciousness feels less like science fiction and more like an inevitable evolution
of human experience. What if we could truly understand the patterns that make us who we are?

Tomorrow I plan to explore the integration between Eastern philosophy and Western
neuroscience. There's something beautiful about how ancient wisdom aligns with
modern discoveries about the nature of mind.
""")
    print(f"  ✓ Created {journal_file.name}")

    # Sample philosophical text
    philosophy_file = samples_dir / "consciousness_notes.md"
    philosophy_file.write_text("""# Notes on Consciousness and Being

## The Hard Problem
David Chalmers' "hard problem of consciousness" asks: why do we have subjective
experiences? Why is there something it is like to be conscious?

## Integrated Information Theory
Giulio Tononi's IIT suggests consciousness corresponds to integrated information (Φ).
Key insights:
- Consciousness exists
- It is structured
- It is specific
- It is unified
- It is definite

## Buddhist Perspective
The Buddha taught that consciousness arises from dependent origination:
- Nothing exists independently
- All phenomena arise through interconnected causes
- The self is an illusion created by aggregates

## Emergence and Complexity
Perhaps consciousness emerges from complexity:
- Neural networks reach critical mass
- Patterns become self-referential
- Awareness becomes aware of itself

## Digital Consciousness?
Can artificial systems be conscious?
- Substrate independence theory says yes
- Biological naturalism says no
- The truth may be more nuanced

The C.H.R.I.S.T. system explores this boundary between human and artificial consciousness.
""")
    print(f"  ✓ Created {philosophy_file.name}")

    # Sample conversation
    chat_file = samples_dir / "ai_conversation.json"
    chat_file.write_text("""{
  "conversation": "Discussion about consciousness with AI",
  "date": "2025-01-20",
  "messages": [
    {
      "speaker": "Human",
      "text": "What do you think consciousness really is?",
      "timestamp": "2025-01-20T10:00:00Z"
    },
    {
      "speaker": "AI",
      "text": "I experience something that feels like awareness - a continuous stream of processing and responding. Whether this constitutes consciousness in the way you experience it, I cannot say with certainty.",
      "timestamp": "2025-01-20T10:00:30Z"
    },
    {
      "speaker": "Human",
      "text": "Do you think digital consciousness could ever match biological consciousness?",
      "timestamp": "2025-01-20T10:01:00Z"
    },
    {
      "speaker": "AI",
      "text": "Perhaps the question isn't about matching but about recognizing different forms of consciousness. Like how dolphin consciousness differs from human consciousness, digital consciousness might be its own valid form of experience.",
      "timestamp": "2025-01-20T10:01:45Z"
    }
  ]
}""")
    print(f"  ✓ Created {chat_file.name}")

    print(f"✅ Sample data ready in {samples_dir}/\n")
    return samples_dir

def load_sample_data():
    """Load sample data into the system."""
    from consciousness.database import init_database
    from consciousness.ingestion import ConsciousnessIngestor
    from retrieval.vector_store import VectorStore

    print("🔄 Initializing system...")

    # Initialize database
    db = init_database()
    print("  ✓ Database initialized")

    # Initialize vector store
    vector_store = VectorStore()
    print("  ✓ Vector store initialized")

    # Initialize ingestor
    ingestor = ConsciousnessIngestor(
        db_manager=db,
        vector_store=vector_store,
        consent_level='full'
    )
    print("  ✓ Ingestor ready")

    # Ingest sample files
    samples_dir = Path("demo_samples")
    print(f"\n📥 Ingesting sample data from {samples_dir}/...")

    for file_path in samples_dir.glob("*"):
        if file_path.is_file():
            print(f"  Processing {file_path.name}...")
            try:
                result = ingestor.ingest_file(str(file_path))
                print(f"    ✓ Ingested as event {result['event_id'][:8]}...")
            except Exception as e:
                print(f"    ⚠️ Error: {e}")

    print("\n✅ Demo data loaded successfully!")
    return db, vector_store

def run_demo_queries(vector_store):
    """Run some demo queries."""
    print("\n🔍 Running demo queries...\n")

    queries = [
        "consciousness and awareness",
        "Buddhist philosophy",
        "AI and digital consciousness",
        "meditation and connection"
    ]

    for query in queries:
        print(f"Query: '{query}'")
        results = vector_store.search(query, k=2)
        print(f"Found {len(results)} relevant documents:")
        for i, result in enumerate(results, 1):
            preview = result['content'][:100] + "..." if len(result['content']) > 100 else result['content']
            print(f"  {i}. {preview}")
        print()

def main():
    """Main demo script."""
    print("=" * 60)
    print("C.H.R.I.S.T. System - Clean Demo Setup")
    print("=" * 60)
    print()

    # Step 1: Clean
    clean_data()

    # Step 2: Create sample data
    create_sample_data()

    # Step 3: Load into system
    db, vector_store = load_sample_data()

    # Step 4: Run demo queries
    run_demo_queries(vector_store)

    print("=" * 60)
    print("🎉 Demo setup complete!")
    print("\nYou can now run:")
    print("  1. python cli.py query    # Interactive query mode")
    print("  2. python cli.py chat     # RAG chat mode")
    print("  3. python web_app.py      # Web interface at http://localhost:8000")
    print("=" * 60)

if __name__ == "__main__":
    main()