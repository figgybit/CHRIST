#!/usr/bin/env python3
"""
Resurrection Consciousness Demo
Uses the full CHRIST framework with vector databases
Each resurrection has its own portable consciousness bundle
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Ensure we're using venv
if 'VIRTUAL_ENV' not in os.environ:
    print("⚠️  Please activate the virtual environment first:")
    print("   source venv/bin/activate")
    print("   Or set: export VIRTUAL_ENV=venv")

from resurrections.resurrection_consciousness import ResurrectionBot


def main():
    """Run the consciousness-based resurrection demo."""
    print("\n" + "="*70)
    print("     RESURRECTION CONSCIOUSNESS SYSTEM")
    print("     Each figure has their own vector database")
    print("     Portable, distributable consciousness bundles")
    print("="*70)

    # Let user choose figure
    print("\nAvailable resurrections:")
    print("1. Jesus Christ")
    print("2. [Future: Buddha]")
    print("3. [Future: Socrates]")

    choice = input("\nSelect resurrection (1): ").strip() or "1"

    if choice == "1":
        figure_name = "jesus_christ"
    else:
        print("Only Jesus Christ is currently available")
        figure_name = "jesus_christ"

    # Initialize the bot with consciousness
    bot = ResurrectionBot(figure_name)

    # Show capabilities
    print("\n✨ This resurrection uses:")
    print("  - Vector database for semantic search")
    print("  - RAG (Retrieval-Augmented Generation) if Ollama is running")
    print("  - Portable consciousness bundle in resurrections/bundles/")
    print("\nAsk questions about:")
    print("  - Thomas and the apostles")
    print("  - Daily life and ministry")
    print("  - Teachings and parables")
    print("  - Love, faith, prayer")
    print("\nType 'quit' to exit")
    print("="*70 + "\n")

    # Interactive loop
    while True:
        try:
            query = input("You: ").strip()

            if query.lower() in ['quit', 'exit', 'goodbye']:
                print("\n🕊️ Go in peace.")
                break

            if not query:
                continue

            # Get response from consciousness
            response = bot.respond(query)
            print(f"\n🕊️ {figure_name.replace('_', ' ').title()}: {response}\n")

        except KeyboardInterrupt:
            print("\n\nPeace be with you.")
            break
        except Exception as e:
            print(f"\n⚠️ Error: {e}\n")

    # Show bundle info
    stats = bot.consciousness.get_stats()
    print("\n📊 Consciousness Bundle Statistics:")
    print(f"  Documents: {stats.get('metadata', {}).get('statistics', {}).get('total_documents', 0)}")
    print(f"  Bundle size: {stats.get('bundle_size', 0) / 1024:.1f} KB")
    print(f"  Location: resurrections/bundles/{figure_name}/")


if __name__ == "__main__":
    main()