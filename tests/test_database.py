#!/usr/bin/env python3
"""
Unit tests for database operations.
"""

import unittest
import tempfile
import os
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from consciousness.database import DatabaseManager, get_db_manager


class TestDatabaseManager(unittest.TestCase):
    """Test database manager functionality."""

    def setUp(self):
        """Create temporary database for testing."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        os.environ['DATABASE_URL'] = f'sqlite:///{self.temp_db.name}'
        self.db_manager = DatabaseManager(f'sqlite:///{self.temp_db.name}')

    def tearDown(self):
        """Clean up temporary database."""
        try:
            os.unlink(self.temp_db.name)
        except:
            pass

    def test_database_initialization(self):
        """Test that database tables are created."""
        # Tables should be created on init
        self.assertIsNotNone(self.db_manager.engine)
        self.assertIsNotNone(self.db_manager.SessionLocal)

    def test_store_event(self):
        """Test storing an event."""
        event_data = {
            'id': 'test-event-001',
            'user_id': 'test-user',
            'timestamp': datetime.now().isoformat(),
            'type': 'test_event',
            'source': 'unit_test',
            'content_encrypted': 'encrypted_content',
            'content_hash': 'hash123',
            'metadata': {'test_key': 'test_value'},
            'consent_level': 'full'
        }

        event_id = self.db_manager.store_event(event_data)
        self.assertEqual(event_id, 'test-event-001')

    def test_query_events(self):
        """Test querying events."""
        # Store some test events
        for i in range(3):
            event_data = {
                'id': f'test-event-{i:03d}',
                'user_id': 'test-user',
                'timestamp': datetime.now().isoformat(),
                'type': 'test_event',
                'metadata': {'index': i}
            }
            self.db_manager.store_event(event_data)

        # Query events
        events = self.db_manager.query_events(user_id='test-user', limit=10)
        self.assertEqual(len(events), 3)

        # Check event structure
        first_event = events[0]
        self.assertIn('id', first_event)
        self.assertIn('timestamp', first_event)
        self.assertIn('type', first_event)
        self.assertIn('metadata', first_event)

    def test_query_events_with_filters(self):
        """Test querying events with filters."""
        # Store events with different types
        event_types = ['email', 'journal', 'chat']
        for i, event_type in enumerate(event_types):
            event_data = {
                'id': f'test-event-{i:03d}',
                'user_id': 'test-user',
                'timestamp': datetime.now().isoformat(),
                'type': event_type,
                'metadata': {'type': event_type}
            }
            self.db_manager.store_event(event_data)

        # Query by event type
        email_events = self.db_manager.query_events(
            user_id='test-user',
            event_type='email',
            limit=10
        )
        self.assertEqual(len(email_events), 1)
        self.assertEqual(email_events[0]['type'], 'email')

    def test_store_consent(self):
        """Test storing consent records."""
        consent_data = {
            'level': 'full',
            'granted': True,
            'purposes': ['research', 'analysis'],
            'source_types': ['email', 'chat']
        }

        consent_id = self.db_manager.store_consent('test-user', consent_data)
        self.assertIsNotNone(consent_id)

    def test_audit_log(self):
        """Test audit logging."""
        audit_data = {
            'user_id': 'test-user',
            'action': 'test_action',
            'resource_type': 'test_resource',
            'details': {'test': 'data'}
        }
        # log_audit doesn't return anything, just verify no exception
        self.db_manager.log_audit(audit_data)
        # If we reach here, audit log succeeded

    def test_metadata_field_fix(self):
        """Test that metadata field is correctly renamed to meta_data."""
        # This test ensures our fix for the SQLAlchemy reserved word works
        event_data = {
            'id': 'metadata-test',
            'user_id': 'test-user',
            'timestamp': datetime.now().isoformat(),
            'type': 'test',
            'metadata': {'key': 'value'}  # Input uses 'metadata'
        }

        event_id = self.db_manager.store_event(event_data)
        events = self.db_manager.query_events(user_id='test-user', limit=1)

        # Output should also use 'metadata' for consistency
        self.assertIn('metadata', events[0])
        self.assertEqual(events[0]['metadata']['key'], 'value')


class TestDatabaseIntegrity(unittest.TestCase):
    """Test database integrity and error handling."""

    def setUp(self):
        """Create temporary database for testing."""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.db_manager = DatabaseManager(f'sqlite:///{self.temp_db.name}')

    def tearDown(self):
        """Clean up temporary database."""
        try:
            os.unlink(self.temp_db.name)
        except:
            pass

    def test_duplicate_event_id(self):
        """Test handling of duplicate event IDs."""
        event_data = {
            'id': 'duplicate-id',
            'user_id': 'test-user',
            'timestamp': datetime.now().isoformat(),
            'type': 'test'
        }

        # First insert should succeed
        self.db_manager.store_event(event_data)

        # Second insert with same ID should fail
        with self.assertRaises(Exception):
            self.db_manager.store_event(event_data)

    def test_missing_required_fields(self):
        """Test handling of missing required fields."""
        event_data = {
            'user_id': 'test-user',
            # Missing 'id' and 'timestamp'
            'type': 'test'
        }

        with self.assertRaises(Exception):
            self.db_manager.store_event(event_data)

    def test_invalid_timestamp_format(self):
        """Test handling of invalid timestamp formats."""
        event_data = {
            'id': 'test-id',
            'user_id': 'test-user',
            'timestamp': 'invalid-timestamp',
            'type': 'test'
        }

        with self.assertRaises(Exception):
            self.db_manager.store_event(event_data)


if __name__ == '__main__':
    unittest.main()