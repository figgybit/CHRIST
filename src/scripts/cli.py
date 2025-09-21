#!/usr/bin/env python3
"""
Command-line interface for C.H.R.I.S.T. data ingestion.
"""

import click
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from consciousness.parsers import UniversalParser
from consciousness.database import init_database, get_db_manager
from consciousness.encryption import get_encryption_manager, ConsentBasedEncryption


@click.group()
@click.pass_context
def cli(ctx):
    """C.H.R.I.S.T. - Consciousness Capture CLI"""
    ctx.ensure_object(dict)
    click.echo("🧠 C.H.R.I.S.T. Consciousness Capture System")


@cli.command()
@click.option('--file', '-f', required=True, help='File to ingest')
@click.option('--type', '-t', help='File type (auto-detected if not specified)')
@click.option('--consent', '-c',
              type=click.Choice(['none', 'metadata_only', 'anonymized', 'full']),
              default='full',
              help='Consent level for data processing')
@click.option('--user-id', '-u', default='default', help='User ID')
@click.pass_context
def ingest(ctx, file, type, consent, user_id):
    """Ingest a file into the consciousness system."""

    file_path = Path(file)
    if not file_path.exists():
        click.echo(f"❌ Error: File not found: {file}", err=True)
        sys.exit(1)

    click.echo(f"📄 Processing file: {file_path.name}")
    click.echo(f"🔒 Consent level: {consent}")

    try:
        # Initialize components
        db_manager = get_db_manager()
        encryption_manager = get_encryption_manager()
        consent_encryption = ConsentBasedEncryption(encryption_manager)
        parser = UniversalParser()

        # Parse file
        click.echo("🔍 Parsing file...")
        data = parser.parse(str(file_path))

        # Process based on consent
        if isinstance(data, list):
            # Multiple items (e.g., mbox file)
            count = 0
            for item in data:
                processed = consent_encryption.process_data(item, consent)
                if processed:
                    processed['user_id'] = user_id
                    db_manager.store_event(processed)
                    count += 1
            click.echo(f"✅ Successfully ingested {count} items")
        else:
            # Single item
            processed = consent_encryption.process_data(data, consent)
            if processed:
                processed['user_id'] = user_id
                event_id = db_manager.store_event(processed)
                click.echo(f"✅ Successfully ingested with ID: {event_id}")

        # Log audit event
        db_manager.log_audit({
            'user_id': user_id,
            'action': 'ingest',
            'resource_type': 'file',
            'resource_id': str(file_path),
            'details': {
                'consent_level': consent,
                'file_type': type or 'auto-detected'
            },
            'success': True
        })

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--user-id', '-u', default='default', help='User ID')
@click.option('--start-date', '-s', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', '-e', help='End date (YYYY-MM-DD)')
@click.option('--type', '-t', help='Event type filter')
@click.option('--limit', '-l', default=10, help='Maximum number of results')
@click.pass_context
def query(ctx, user_id, start_date, end_date, type, limit):
    """Query stored events."""

    try:
        db_manager = get_db_manager()

        # Parse dates
        start_dt = datetime.fromisoformat(start_date) if start_date else None
        end_dt = datetime.fromisoformat(end_date) if end_date else None

        # Query events
        events = db_manager.query_events(
            user_id=user_id,
            start_date=start_dt,
            end_date=end_dt,
            event_type=type,
            limit=limit
        )

        if not events:
            click.echo("No events found matching criteria")
            return

        # Display results
        click.echo(f"\n📊 Found {len(events)} event(s):\n")
        for event in events:
            click.echo(f"ID: {event['id']}")
            click.echo(f"  Timestamp: {event['timestamp']}")
            click.echo(f"  Type: {event['type']}")
            click.echo(f"  Source: {event.get('source', 'N/A')}")
            if event.get('metadata'):
                click.echo(f"  Metadata: {json.dumps(event['metadata'], indent=2)}")
            click.echo()

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--user-id', '-u', default='default', help='User ID')
@click.option('--level', '-l',
              type=click.Choice(['none', 'metadata_only', 'anonymized', 'full']),
              required=True,
              help='New consent level')
@click.option('--sources', '-s', multiple=True, help='Consented source types')
@click.pass_context
def consent(ctx, user_id, level, sources):
    """Update consent settings."""

    try:
        db_manager = get_db_manager()

        # Store consent record
        consent_id = db_manager.store_consent(user_id, {
            'type': 'data_processing',
            'level': level,
            'granted': level != 'none',
            'source_types': list(sources),
            'purposes': ['consciousness_capture'],
        })

        click.echo(f"✅ Consent updated successfully")
        click.echo(f"   Consent ID: {consent_id}")
        click.echo(f"   Level: {level}")
        if sources:
            click.echo(f"   Sources: {', '.join(sources)}")

        # Log audit event
        db_manager.log_audit({
            'user_id': user_id,
            'action': 'update_consent',
            'resource_type': 'consent',
            'resource_id': consent_id,
            'details': {
                'level': level,
                'sources': list(sources)
            },
            'success': True
        })

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def init_db(ctx):
    """Initialize the database."""

    try:
        click.echo("🗄️  Initializing database...")
        db_manager = init_database()
        click.echo("✅ Database initialized successfully")
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--output', '-o', help='Output file (defaults to stdout)')
@click.pass_context
def stats(ctx, output):
    """Display system statistics."""

    try:
        db_manager = get_db_manager()
        session = db_manager.get_session()

        from consciousness.database import Event, Entity, Artifact, ConsentRecord

        # Get counts
        stats_data = {
            'timestamp': datetime.now().isoformat(),
            'events': session.query(Event).count(),
            'entities': session.query(Entity).count(),
            'artifacts': session.query(Artifact).count(),
            'consent_records': session.query(ConsentRecord).count(),
        }

        # Get event types breakdown
        from sqlalchemy import func
        event_types = session.query(
            Event.event_type,
            func.count(Event.id)
        ).group_by(Event.event_type).all()

        stats_data['event_types'] = {
            event_type: count for event_type, count in event_types
        }

        session.close()

        # Output
        if output:
            with open(output, 'w') as f:
                json.dump(stats_data, f, indent=2)
            click.echo(f"✅ Statistics saved to {output}")
        else:
            click.echo("\n📊 System Statistics:\n")
            click.echo(f"Total Events: {stats_data['events']}")
            click.echo(f"Total Entities: {stats_data['entities']}")
            click.echo(f"Total Artifacts: {stats_data['artifacts']}")
            click.echo(f"Consent Records: {stats_data['consent_records']}")

            if stats_data['event_types']:
                click.echo("\nEvent Types:")
                for event_type, count in stats_data['event_types'].items():
                    click.echo(f"  {event_type}: {count}")

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


@cli.command()
@click.option('--confirm', is_flag=True, help='Confirm deletion')
@click.option('--user-id', '-u', default='default', help='User ID')
@click.pass_context
def delete_all(ctx, confirm, user_id):
    """Delete all data for a user (right to forget)."""

    if not confirm:
        click.echo("⚠️  Warning: This will permanently delete all data for user: " + user_id)
        click.echo("Use --confirm to proceed")
        return

    try:
        db_manager = get_db_manager()
        session = db_manager.get_session()

        from consciousness.database import Event, Entity, Artifact, Relationship

        # Delete all user data
        session.query(Event).filter(Event.user_id == user_id).delete()
        session.query(Entity).filter(Entity.user_id == user_id).delete()
        session.query(Artifact).filter(Artifact.user_id == user_id).delete()
        session.query(Relationship).filter(Relationship.user_id == user_id).delete()

        session.commit()
        session.close()

        click.echo(f"✅ All data deleted for user: {user_id}")

        # Log audit event
        db_manager.log_audit({
            'user_id': user_id,
            'action': 'delete_all',
            'resource_type': 'user_data',
            'resource_id': user_id,
            'details': {'confirmed': True},
            'success': True
        })

    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()