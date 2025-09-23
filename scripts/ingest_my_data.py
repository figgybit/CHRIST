#!/usr/bin/env python3
"""
Comprehensive data ingestion script for C.H.R.I.S.T. System
Handles multiple file types and provides progress tracking
"""

import os
import sys
import json
import hashlib
import mimetypes
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import argparse

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from consciousness.database import init_database
from consciousness.ingestion import ConsciousnessIngestor
from retrieval.vector_store import VectorStore


class DataIngestionPipeline:
    """Complete pipeline for ingesting personal data."""

    def __init__(self, consent_level='full', encryption_enabled=True):
        """Initialize ingestion pipeline."""
        print("🔧 Initializing C.H.R.I.S.T. ingestion system...")

        self.db = init_database()
        self.vector_store = VectorStore()
        self.ingestor = ConsciousnessIngestor(
            db_manager=self.db,
            vector_store=self.vector_store,
            consent_level=consent_level,
            encryption_enabled=encryption_enabled
        )

        # File type mappings
        self.supported_extensions = {
            # Text formats
            '.txt': 'text',
            '.md': 'text',
            '.markdown': 'text',
            '.rst': 'text',
            '.log': 'text',

            # Documents
            '.pdf': 'document',
            '.doc': 'document',
            '.docx': 'document',
            '.odt': 'document',
            '.rtf': 'document',

            # Code
            '.py': 'code',
            '.js': 'code',
            '.java': 'code',
            '.cpp': 'code',
            '.c': 'code',
            '.html': 'code',
            '.css': 'code',
            '.json': 'data',
            '.xml': 'data',
            '.yaml': 'data',
            '.yml': 'data',

            # Emails
            '.eml': 'email',
            '.mbox': 'email',
            '.msg': 'email',

            # Images (for future OCR)
            '.jpg': 'image',
            '.jpeg': 'image',
            '.png': 'image',
            '.gif': 'image',
            '.bmp': 'image',

            # Audio (for future transcription)
            '.mp3': 'audio',
            '.wav': 'audio',
            '.m4a': 'audio',
            '.ogg': 'audio',

            # Video (for future processing)
            '.mp4': 'video',
            '.avi': 'video',
            '.mkv': 'video',
            '.mov': 'video',
        }

        self.stats = {
            'total_files': 0,
            'processed': 0,
            'skipped': 0,
            'errors': 0,
            'by_type': {}
        }

    def should_process_file(self, file_path: Path) -> bool:
        """Determine if file should be processed."""
        # Skip hidden files and directories
        if file_path.name.startswith('.'):
            return False

        # Skip system files
        if file_path.name in ['desktop.ini', 'Thumbs.db', '.DS_Store']:
            return False

        # Skip if no extension
        if not file_path.suffix:
            return False

        # Check if supported
        return file_path.suffix.lower() in self.supported_extensions

    def process_file(self, file_path: Path) -> Dict[str, Any]:
        """Process a single file."""
        extension = file_path.suffix.lower()
        file_type = self.supported_extensions.get(extension, 'unknown')

        try:
            # Currently supported formats
            if extension in ['.txt', '.md', '.log', '.py', '.js', '.html', '.css']:
                result = self.ingestor.ingest_file(str(file_path))
                return {'status': 'success', 'type': file_type, 'id': result['event_id']}

            elif extension in ['.json', '.yaml', '.yml']:
                result = self.ingestor.ingest_file(str(file_path))
                return {'status': 'success', 'type': file_type, 'id': result['event_id']}

            elif extension in ['.eml', '.mbox']:
                result = self.ingestor.ingest_file(str(file_path))
                return {'status': 'success', 'type': file_type, 'id': result['event_id']}

            elif extension == '.pdf':
                # Basic PDF support - needs enhancement
                return {'status': 'skipped', 'reason': 'PDF support coming soon'}

            elif file_type == 'image':
                # Future: OCR processing
                return {'status': 'skipped', 'reason': 'Image OCR not yet implemented'}

            elif file_type == 'audio':
                # Future: Speech-to-text
                return {'status': 'skipped', 'reason': 'Audio transcription not yet implemented'}

            elif file_type == 'video':
                # Future: Video processing
                return {'status': 'skipped', 'reason': 'Video processing not yet implemented'}

            else:
                return {'status': 'skipped', 'reason': 'Unsupported file type'}

        except Exception as e:
            return {'status': 'error', 'error': str(e)}

    def scan_directory(self, directory: Path) -> List[Path]:
        """Scan directory and return list of files to process."""
        files_to_process = []

        print(f"\n📂 Scanning {directory}...")

        for file_path in directory.rglob('*'):
            if file_path.is_file():
                self.stats['total_files'] += 1

                if self.should_process_file(file_path):
                    files_to_process.append(file_path)

        return files_to_process

    def ingest_directory(
        self,
        directory: str,
        batch_size: int = 10,
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Ingest all supported files from a directory.

        Args:
            directory: Path to directory
            batch_size: Number of files to process before showing progress
            dry_run: If True, only scan without processing
        """
        dir_path = Path(directory)
        if not dir_path.exists():
            print(f"❌ Directory not found: {directory}")
            return self.stats

        # Scan for files
        files = self.scan_directory(dir_path)

        print(f"\n📊 Found {len(files)} processable files out of {self.stats['total_files']} total")

        if dry_run:
            print("\n🔍 Dry run - showing what would be processed:")

            # Group by type
            by_type = {}
            for file_path in files[:50]:  # Show first 50
                ext = file_path.suffix.lower()
                file_type = self.supported_extensions.get(ext, 'unknown')
                if file_type not in by_type:
                    by_type[file_type] = []
                by_type[file_type].append(file_path.name)

            for file_type, file_names in by_type.items():
                print(f"\n{file_type.upper()} ({len(file_names)} files):")
                for name in file_names[:5]:
                    print(f"  - {name}")
                if len(file_names) > 5:
                    print(f"  ... and {len(file_names) - 5} more")

            return self.stats

        # Process files
        print(f"\n🚀 Starting ingestion of {len(files)} files...")
        print("=" * 60)

        for i, file_path in enumerate(files, 1):
            # Progress indicator
            if i % batch_size == 0:
                print(f"\n📈 Progress: {i}/{len(files)} files processed")
                print(f"   ✅ Success: {self.stats['processed']}")
                print(f"   ⏭️ Skipped: {self.stats['skipped']}")
                print(f"   ❌ Errors: {self.stats['errors']}")
                print("-" * 40)

            # Show current file
            relative_path = file_path.relative_to(dir_path)
            print(f"[{i}/{len(files)}] Processing: {relative_path}")

            # Process file
            result = self.process_file(file_path)

            # Update stats
            if result['status'] == 'success':
                self.stats['processed'] += 1
                file_type = result['type']
                if file_type not in self.stats['by_type']:
                    self.stats['by_type'][file_type] = 0
                self.stats['by_type'][file_type] += 1
                print(f"  ✅ Ingested as {result['id'][:8]}...")

            elif result['status'] == 'skipped':
                self.stats['skipped'] += 1
                print(f"  ⏭️ Skipped: {result['reason']}")

            else:  # error
                self.stats['errors'] += 1
                print(f"  ❌ Error: {result.get('error', 'Unknown error')}")

        # Final summary
        print("\n" + "=" * 60)
        print("📊 INGESTION COMPLETE")
        print("=" * 60)
        print(f"Total files scanned: {self.stats['total_files']}")
        print(f"Files processed: {self.stats['processed']}")
        print(f"Files skipped: {self.stats['skipped']}")
        print(f"Errors: {self.stats['errors']}")

        if self.stats['by_type']:
            print("\nBy type:")
            for file_type, count in self.stats['by_type'].items():
                print(f"  {file_type}: {count}")

        return self.stats


def main():
    """Main ingestion CLI."""
    parser = argparse.ArgumentParser(
        description='Ingest your personal data into C.H.R.I.S.T. consciousness system'
    )

    parser.add_argument(
        'directory',
        help='Directory containing your data'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Scan only, do not process files'
    )

    parser.add_argument(
        '--consent',
        choices=['none', 'metadata_only', 'anonymized', 'full'],
        default='full',
        help='Privacy consent level (default: full)'
    )

    parser.add_argument(
        '--no-encryption',
        action='store_true',
        help='Disable encryption (faster but less secure)'
    )

    parser.add_argument(
        '--batch-size',
        type=int,
        default=10,
        help='Show progress every N files (default: 10)'
    )

    args = parser.parse_args()

    print("=" * 60)
    print("C.H.R.I.S.T. Data Ingestion System")
    print("=" * 60)

    # Create pipeline
    pipeline = DataIngestionPipeline(
        consent_level=args.consent,
        encryption_enabled=not args.no_encryption
    )

    # Run ingestion
    stats = pipeline.ingest_directory(
        args.directory,
        batch_size=args.batch_size,
        dry_run=args.dry_run
    )

    if not args.dry_run and stats['processed'] > 0:
        print("\n✨ Your consciousness data has been captured!")
        print("You can now:")
        print("  1. Search it: python cli.py query")
        print("  2. Chat with it: python cli.py chat")
        print("  3. Browse it: python web_app.py")


if __name__ == '__main__':
    main()