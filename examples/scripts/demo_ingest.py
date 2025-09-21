#!/usr/bin/env python3
"""
Demo script for ingesting sample data into C.H.R.I.S.T. system.
"""

import sys
import json
import asyncio
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from consciousness.database import get_db_manager
from consciousness.parsers import UniversalParser
from consciousness.encryption import get_encryption_manager, ConsentBasedEncryption
from retrieval.vector_store import VectorStore


async def ingest_sample_data():
    """Ingest sample data into the system."""

    print("=" * 60)
    print("C.H.R.I.S.T. System - Sample Data Ingestion")
    print("=" * 60)

    # Initialize components
    db_manager = get_db_manager()
    parser = UniversalParser()
    encryption_manager = get_encryption_manager()
    consent_processor = ConsentBasedEncryption(encryption_manager)
    vector_store = VectorStore()

    # Paths to sample data
    examples_dir = Path(__file__).parent.parent / "data"
    journal_file = examples_dir / "sample_journal.txt"
    emails_file = examples_dir / "sample_emails.json"

    # 1. Ingest journal entries
    print("\n1. Ingesting journal entries...")
    if journal_file.exists():
        try:
            parsed_journal = parser.parse(str(journal_file))

            # Process with consent
            processed = consent_processor.process_data(
                parsed_journal,
                consent_level="full"
            )

            # Store in database
            event_id = db_manager.store_event(processed)

            # Add to vector store
            vector_store.add_documents(
                [processed['content']['text']],
                [processed['metadata']],
                [event_id]
            )

            print(f"   ✓ Journal ingested: {event_id}")
            print(f"   - {processed['metadata']['line_count']} lines")
            print(f"   - {processed['metadata']['word_count']} words")

        except Exception as e:
            print(f"   ✗ Error ingesting journal: {e}")
    else:
        print(f"   ✗ Journal file not found: {journal_file}")

    # 2. Ingest email samples
    print("\n2. Ingesting email samples...")
    if emails_file.exists():
        try:
            with open(emails_file, 'r') as f:
                emails = json.load(f)

            for email in emails:
                # Process each email
                email_data = {
                    'id': email['id'],
                    'type': 'email',
                    'timestamp': email['date'],
                    'headers': {
                        'from': email['from'],
                        'to': email['to'],
                        'subject': email['subject']
                    },
                    'content': {
                        'plain': email['body']
                    },
                    'metadata': {
                        'char_count': len(email['body'])
                    }
                }

                # Process with consent
                processed = consent_processor.process_data(
                    email_data,
                    consent_level="full"
                )

                # Store in database
                event_id = db_manager.store_event(processed)

                # Add to vector store
                vector_store.add_documents(
                    [email['body']],
                    [{'source': 'email', 'subject': email['subject'], 'from': email['from']}],
                    [event_id]
                )

            print(f"   ✓ {len(emails)} emails ingested")

        except Exception as e:
            print(f"   ✗ Error ingesting emails: {e}")
    else:
        print(f"   ✗ Email file not found: {emails_file}")

    # 3. Create sample goals
    print("\n3. Creating sample goals...")
    goals = [
        {
            "title": "Complete C.H.R.I.S.T. Implementation",
            "category": "Technology",
            "description": "Fully implement and deploy the consciousness capture system",
            "target_date": "2024-06-01",
            "status": "in_progress"
        },
        {
            "title": "Daily Journaling Practice",
            "category": "Personal Development",
            "description": "Write journal entries every day for reflection and growth",
            "target_date": "2024-12-31",
            "status": "active"
        },
        {
            "title": "Privacy Framework Documentation",
            "category": "Documentation",
            "description": "Create comprehensive privacy documentation for users",
            "target_date": "2024-02-15",
            "status": "pending"
        }
    ]

    for goal in goals:
        try:
            # Store goal (in a real system, this would go to a goals table)
            goal_data = {
                'type': 'goal',
                'timestamp': datetime.now().isoformat(),
                'content': goal,
                'metadata': {'category': goal['category']},
                'user_id': 'demo_user'
            }

            event_id = db_manager.store_event(goal_data)
            print(f"   ✓ Goal created: {goal['title']}")

        except Exception as e:
            print(f"   ✗ Error creating goal: {e}")

    # 4. Display statistics
    print("\n" + "=" * 60)
    print("Ingestion Complete!")
    print("=" * 60)

    # Query total events
    events = db_manager.query_events(limit=1000)

    # Group by type
    event_types = {}
    for event in events:
        event_type = event.get('type', 'unknown')
        event_types[event_type] = event_types.get(event_type, 0) + 1

    print(f"\nTotal Events: {len(events)}")
    print("\nEvents by Type:")
    for event_type, count in event_types.items():
        print(f"  - {event_type}: {count}")

    print("\nVector Store Statistics:")
    print(f"  - Documents indexed: {len(events)}")
    print(f"  - Ready for semantic search: Yes")

    print("\n✅ Sample data successfully ingested!")
    print("You can now:")
    print("  1. Search memories using the web UI (/search)")
    print("  2. Chat with your consciousness (/chat)")
    print("  3. Generate reflections (/reflections)")
    print("  4. Track goals (/goals)")


if __name__ == "__main__":
    asyncio.run(ingest_sample_data())