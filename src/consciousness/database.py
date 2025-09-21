"""
Database models and operations for Consciousness Capture.
"""

import os
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import create_engine, Column, String, Text, DateTime, Float, Boolean, Integer, JSON, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.pool import StaticPool

Base = declarative_base()


class Event(Base):
    """Event model for storing timestamped occurrences."""

    __tablename__ = 'events'

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    source = Column(String(50))
    source_id = Column(String(255))

    # Encrypted content
    content_encrypted = Column(Text)
    content_hash = Column(String(64))

    # Metadata
    meta_data = Column(JSON)
    confidence = Column(Float, default=1.0)
    processing_status = Column(String(20), default='pending')

    # Privacy
    consent_level = Column(String(20), default='full')
    encryption_key_id = Column(String(36))

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    artifacts = relationship("Artifact", back_populates="event")

    # Indexes
    __table_args__ = (
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_type_timestamp', 'event_type', 'timestamp'),
    )


class Artifact(Base):
    """Artifact model for storing files and media."""

    __tablename__ = 'artifacts'

    id = Column(String(36), primary_key=True)
    event_id = Column(String(36), ForeignKey('events.id'), nullable=True)
    user_id = Column(String(36), nullable=False, index=True)

    artifact_type = Column(String(50), nullable=False)
    storage_path = Column(Text)
    content_hash = Column(String(64), unique=True, index=True)

    # File info
    original_name = Column(String(255))
    mime_type = Column(String(100))
    size_bytes = Column(Integer)

    # Encryption
    encrypted = Column(Boolean, default=True)
    encryption_key_id = Column(String(36))

    # Metadata
    meta_data = Column(JSON)
    extracted_text = Column(Text)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    accessed_at = Column(DateTime)

    # Relationships
    event = relationship("Event", back_populates="artifacts")


class Entity(Base):
    """Entity model for persons, places, organizations, etc."""

    __tablename__ = 'entities'

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)
    entity_type = Column(String(50), nullable=False, index=True)

    # Basic info
    name = Column(String(255), nullable=False)
    description = Column(Text)

    # Properties stored as JSON
    properties = Column(JSON)

    # Statistics
    first_mention = Column(DateTime)
    last_mention = Column(DateTime)
    mention_count = Column(Integer, default=0)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Relationship(Base):
    """Relationship model for connections between entities/events."""

    __tablename__ = 'relationships'

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)

    source_id = Column(String(36), nullable=False, index=True)
    source_type = Column(String(20))  # 'event', 'entity', 'artifact'

    target_id = Column(String(36), nullable=False, index=True)
    target_type = Column(String(20))

    relationship_type = Column(String(50), nullable=False)
    properties = Column(JSON)
    strength = Column(Float, default=1.0)

    # Temporal bounds
    start_date = Column(DateTime)
    end_date = Column(DateTime)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)


class ConsentRecord(Base):
    """Consent record for privacy compliance."""

    __tablename__ = 'consent_records'

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), nullable=False, index=True)

    consent_type = Column(String(50))
    consent_level = Column(String(20))  # none, metadata_only, anonymized, full
    granted = Column(Boolean, default=False)

    source_types = Column(JSON)  # List of consented source types
    purposes = Column(JSON)  # List of consented purposes

    granted_at = Column(DateTime)
    expires_at = Column(DateTime)
    revoked_at = Column(DateTime, nullable=True)

    signature = Column(Text)  # Cryptographic signature
    ip_address = Column(String(45))  # Anonymized IP

    created_at = Column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    """Audit log for tracking all data access."""

    __tablename__ = 'audit_logs'

    id = Column(String(36), primary_key=True)
    user_id = Column(String(36), index=True)
    actor_id = Column(String(36))

    action = Column(String(50), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(36))

    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(255))

    success = Column(Boolean, default=True)
    error_message = Column(Text)

    timestamp = Column(DateTime, default=datetime.utcnow, index=True)

    __table_args__ = (
        Index('idx_audit_user_time', 'user_id', 'timestamp'),
    )


class DatabaseManager:
    """Manager class for database operations."""

    def __init__(self, database_url: str = None):
        """
        Initialize database manager.

        Args:
            database_url: SQLAlchemy database URL
        """
        if database_url is None:
            # Use SQLite for development
            database_url = os.getenv('DATABASE_URL', 'sqlite:///./christ.db')

        # Special handling for SQLite to avoid threading issues
        if database_url.startswith('sqlite'):
            self.engine = create_engine(
                database_url,
                connect_args={'check_same_thread': False},
                poolclass=StaticPool,
                echo=False
            )
        else:
            self.engine = create_engine(database_url, echo=False)

        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

        # Create tables automatically
        self.create_tables()

    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)

    def drop_tables(self):
        """Drop all tables from the database."""
        Base.metadata.drop_all(bind=self.engine)

    def get_session(self) -> Session:
        """Get a new database session."""
        return self.SessionLocal()

    def store_event(self, event_data: Dict[str, Any]) -> str:
        """
        Store an event in the database.

        Args:
            event_data: Event data dictionary

        Returns:
            Event ID
        """
        session = self.get_session()
        try:
            # Convert encrypted content to JSON string if it's a dict
            content_encrypted = event_data.get('content_encrypted')
            if isinstance(content_encrypted, dict):
                import json
                content_encrypted = json.dumps(content_encrypted)

            event = Event(
                id=event_data['id'],
                user_id=event_data.get('user_id', 'default'),
                timestamp=datetime.fromisoformat(event_data['timestamp']),
                event_type=event_data['type'],
                source=event_data.get('source'),
                content_encrypted=content_encrypted,
                content_hash=event_data.get('content_hash'),
                meta_data=event_data.get('metadata', {}),
                consent_level=event_data.get('consent_level', 'full')
            )
            session.add(event)
            session.commit()
            return event.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def query_events(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        event_type: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Query events from the database.

        Args:
            user_id: User ID to query
            start_date: Start date filter
            end_date: End date filter
            event_type: Event type filter
            limit: Maximum number of results

        Returns:
            List of event dictionaries
        """
        session = self.get_session()
        try:
            query = session.query(Event).filter(Event.user_id == user_id)

            if start_date:
                query = query.filter(Event.timestamp >= start_date)
            if end_date:
                query = query.filter(Event.timestamp <= end_date)
            if event_type:
                query = query.filter(Event.event_type == event_type)

            query = query.order_by(Event.timestamp.desc()).limit(limit)

            events = []
            for event in query.all():
                events.append({
                    'id': event.id,
                    'timestamp': event.timestamp.isoformat(),
                    'type': event.event_type,
                    'source': event.source,
                    'metadata': event.meta_data,
                    'created_at': event.created_at.isoformat()
                })

            return events
        finally:
            session.close()

    def store_consent(self, user_id: str, consent_data: Dict[str, Any]) -> str:
        """
        Store consent record.

        Args:
            user_id: User ID
            consent_data: Consent data

        Returns:
            Consent record ID
        """
        session = self.get_session()
        try:
            import uuid
            consent = ConsentRecord(
                id=str(uuid.uuid4()),
                user_id=user_id,
                consent_type=consent_data.get('type', 'general'),
                consent_level=consent_data.get('level', 'full'),
                granted=consent_data.get('granted', True),
                source_types=consent_data.get('source_types', []),
                purposes=consent_data.get('purposes', []),
                granted_at=datetime.utcnow(),
                expires_at=consent_data.get('expires_at'),
                signature=consent_data.get('signature'),
                ip_address=consent_data.get('ip_address')
            )
            session.add(consent)
            session.commit()
            return consent.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def log_audit(self, audit_data: Dict[str, Any]):
        """
        Log an audit event.

        Args:
            audit_data: Audit event data
        """
        session = self.get_session()
        try:
            import uuid
            audit = AuditLog(
                id=str(uuid.uuid4()),
                user_id=audit_data.get('user_id'),
                actor_id=audit_data.get('actor_id'),
                action=audit_data['action'],
                resource_type=audit_data.get('resource_type'),
                resource_id=audit_data.get('resource_id'),
                details=audit_data.get('details', {}),
                ip_address=audit_data.get('ip_address'),
                user_agent=audit_data.get('user_agent'),
                success=audit_data.get('success', True),
                error_message=audit_data.get('error_message')
            )
            session.add(audit)
            session.commit()
        except Exception as e:
            session.rollback()
            # Don't raise - audit logging shouldn't break the app
            print(f"Audit log error: {e}")
        finally:
            session.close()


# Global database manager instance
db_manager = None


def init_database(database_url: str = None):
    """
    Initialize the database.

    Args:
        database_url: Optional database URL
    """
    global db_manager
    db_manager = DatabaseManager(database_url)
    db_manager.create_tables()
    return db_manager


def get_db_manager() -> DatabaseManager:
    """Get the database manager instance."""
    global db_manager
    if db_manager is None:
        db_manager = init_database()
    return db_manager