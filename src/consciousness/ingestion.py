"""
Consciousness ingestion module for processing and storing various data formats.
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
import uuid

from consciousness.parsers import UniversalParser
from consciousness.encryption import EncryptionManager
from consciousness.database import DatabaseManager


class ConsciousnessIngestor:
    """Main ingestion class for processing consciousness data."""

    def __init__(
        self,
        db_manager: DatabaseManager,
        vector_store: Optional[Any] = None,
        encryption_enabled: bool = True,
        consent_level: str = 'full'
    ):
        """
        Initialize the consciousness ingestor.

        Args:
            db_manager: Database manager instance
            vector_store: Vector store for embeddings (optional)
            encryption_enabled: Whether to encrypt content
            consent_level: Privacy consent level
        """
        self.db_manager = db_manager
        self.vector_store = vector_store
        self.parser = UniversalParser()
        self.encryption_manager = EncryptionManager() if encryption_enabled else None
        self.consent_level = consent_level
        self.encryption_enabled = encryption_enabled

    def ingest_file(self, file_path: str) -> Dict[str, Any]:
        """
        Ingest a single file into the consciousness system.

        Args:
            file_path: Path to the file to ingest

        Returns:
            Dict with ingestion results
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Parse the file
        parsed_data = self.parser.parse(str(file_path))

        # Process based on data type
        if parsed_data['type'] == 'email':
            return self._process_email(parsed_data, str(file_path))
        elif parsed_data['type'] == 'text_file':
            return self._process_text(parsed_data, str(file_path))
        elif parsed_data['type'] == 'chat_message':
            return self._process_chat(parsed_data, str(file_path))
        else:
            return self._process_generic(parsed_data, str(file_path))

    def _process_email(self, data: Dict[str, Any], source_path: str) -> Dict[str, Any]:
        """Process email data."""
        event_id = str(uuid.uuid4())

        # Extract content
        content = data.get('content', {})
        text_content = content.get('plain', '') or content.get('html', '')

        # Encrypt if enabled
        if self.encryption_enabled and text_content:
            encrypted_data = self.encryption_manager.encrypt_data(
                text_content.encode('utf-8'),
                {'type': 'email', 'source': source_path}
            )
            content_encrypted = encrypted_data
        else:
            content_encrypted = {'content': text_content}

        # Create event
        event_data = {
            'id': event_id,
            'user_id': 'default',
            'timestamp': data.get('timestamp', datetime.utcnow().isoformat()),
            'type': 'email',
            'source': source_path,
            'content_encrypted': content_encrypted,
            'content_hash': hashlib.sha256(text_content.encode()).hexdigest(),
            'metadata': {
                'headers': data.get('headers', {}),
                'has_attachments': len(data.get('attachments', [])) > 0
            },
            'consent_level': self.consent_level
        }

        # Store in database
        self.db_manager.store_event(event_data)

        # Add to vector store if available
        if self.vector_store and text_content:
            self.vector_store.add_documents(
                documents=[text_content],
                ids=[event_id],
                metadatas=[{'type': 'email', 'source': source_path}]
            )

        return {
            'event_id': event_id,
            'type': 'email',
            'status': 'success'
        }

    def _process_text(self, data: Dict[str, Any], source_path: str) -> Dict[str, Any]:
        """Process text file data."""
        event_id = str(uuid.uuid4())

        # Extract content
        text_content = data.get('content', {}).get('text', '')

        # Encrypt if enabled
        if self.encryption_enabled and text_content:
            encrypted_data = self.encryption_manager.encrypt_data(
                text_content.encode('utf-8'),
                {'type': 'text', 'source': source_path}
            )
            content_encrypted = encrypted_data
        else:
            content_encrypted = {'content': text_content}

        # Create event
        event_data = {
            'id': event_id,
            'user_id': 'default',
            'timestamp': datetime.utcnow().isoformat(),
            'type': 'text_file',
            'source': source_path,
            'content_encrypted': content_encrypted,
            'content_hash': hashlib.sha256(text_content.encode()).hexdigest(),
            'metadata': data.get('metadata', {}),
            'consent_level': self.consent_level
        }

        # Store in database
        self.db_manager.store_event(event_data)

        # Add to vector store if available
        if self.vector_store and text_content:
            self.vector_store.add_documents(
                documents=[text_content],
                ids=[event_id],
                metadatas=[{'type': 'text_file', 'source': source_path}]
            )

        return {
            'event_id': event_id,
            'type': 'text_file',
            'status': 'success'
        }

    def _process_chat(self, data: Dict[str, Any], source_path: str) -> Dict[str, Any]:
        """Process chat message data."""
        event_id = str(uuid.uuid4())

        # Extract content
        text_content = data.get('content', {}).get('text', '')

        # Encrypt if enabled
        if self.encryption_enabled and text_content:
            encrypted_data = self.encryption_manager.encrypt_data(
                text_content.encode('utf-8'),
                {'type': 'chat', 'source': source_path}
            )
            content_encrypted = encrypted_data
        else:
            content_encrypted = {'content': text_content}

        # Create event
        event_data = {
            'id': event_id,
            'user_id': 'default',
            'timestamp': data.get('timestamp', datetime.utcnow().isoformat()),
            'type': 'chat_message',
            'source': source_path,
            'content_encrypted': content_encrypted,
            'content_hash': hashlib.sha256(text_content.encode()).hexdigest(),
            'metadata': {
                'platform': data.get('platform'),
                'sender': data.get('sender'),
                'channel': data.get('metadata', {}).get('channel')
            },
            'consent_level': self.consent_level
        }

        # Store in database
        self.db_manager.store_event(event_data)

        # Add to vector store if available
        if self.vector_store and text_content:
            self.vector_store.add_documents(
                documents=[text_content],
                ids=[event_id],
                metadatas=[{'type': 'chat', 'platform': data.get('platform')}]
            )

        return {
            'event_id': event_id,
            'type': 'chat_message',
            'status': 'success'
        }

    def _process_generic(self, data: Dict[str, Any], source_path: str) -> Dict[str, Any]:
        """Process generic data."""
        event_id = str(uuid.uuid4())

        # Try to extract text content
        text_content = str(data.get('content', data))

        # Encrypt if enabled
        if self.encryption_enabled:
            encrypted_data = self.encryption_manager.encrypt_data(
                text_content.encode('utf-8'),
                {'type': 'generic', 'source': source_path}
            )
            content_encrypted = encrypted_data
        else:
            content_encrypted = {'content': text_content}

        # Create event
        event_data = {
            'id': event_id,
            'user_id': 'default',
            'timestamp': datetime.utcnow().isoformat(),
            'type': data.get('type', 'unknown'),
            'source': source_path,
            'content_encrypted': content_encrypted,
            'content_hash': hashlib.sha256(text_content.encode()).hexdigest(),
            'metadata': data.get('metadata', {}),
            'consent_level': self.consent_level
        }

        # Store in database
        self.db_manager.store_event(event_data)

        # Add to vector store if available
        if self.vector_store and text_content:
            self.vector_store.add_documents(
                documents=[text_content],
                ids=[event_id],
                metadatas=[{'type': data.get('type', 'unknown')}]
            )

        return {
            'event_id': event_id,
            'type': data.get('type', 'unknown'),
            'status': 'success'
        }

    def ingest_directory(
        self,
        directory_path: str,
        recursive: bool = False,
        extensions: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Ingest all files in a directory.

        Args:
            directory_path: Path to directory
            recursive: Whether to process subdirectories
            extensions: List of file extensions to process (e.g., ['.txt', '.eml'])

        Returns:
            List of ingestion results
        """
        directory = Path(directory_path)
        if not directory.is_dir():
            raise ValueError(f"Not a directory: {directory_path}")

        results = []

        # Get files to process
        if recursive:
            files = directory.rglob('*')
        else:
            files = directory.glob('*')

        for file_path in files:
            if not file_path.is_file():
                continue

            # Check extension filter
            if extensions and file_path.suffix not in extensions:
                continue

            try:
                result = self.ingest_file(str(file_path))
                result['file'] = str(file_path)
                results.append(result)
            except Exception as e:
                results.append({
                    'file': str(file_path),
                    'status': 'error',
                    'error': str(e)
                })

        return results