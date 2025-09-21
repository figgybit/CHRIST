# Consciousness Capture (C) - Technical Specification

Version: 0.1.0-MVP
Status: Draft
Last Updated: 2025-01-20

## Executive Summary

The Consciousness Capture component is responsible for ingesting, processing, and storing the raw data streams that constitute a person's digital footprint. This component forms the foundation of the C.H.R.I.S.T. system by creating a comprehensive, privacy-preserving archive of personal data.

## Core Requirements

### Functional Requirements

1. **Multi-Source Ingestion**
   - Support for 10+ data stream types in MVP
   - Extensible plugin architecture for new sources
   - Real-time and batch processing capabilities
   - Automatic format detection and parsing

2. **Privacy & Security**
   - End-to-end encryption for all data at rest
   - Local-first storage with optional cloud sync
   - Granular consent management per data source
   - Complete data deletion capabilities ("right to forget")
   - Zero-knowledge architecture where feasible

3. **Data Integrity**
   - Content-addressable storage with hash verification
   - Immutable append-only logs for audit trails
   - Cryptographic signatures for data provenance
   - Versioning and rollback capabilities

### Non-Functional Requirements

- **Performance**: Process 1GB of mixed data in <5 minutes
- **Scalability**: Support 10TB+ personal archives
- **Reliability**: 99.9% uptime for ingestion services
- **Compatibility**: Cross-platform (Windows, macOS, Linux, Mobile)

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Consciousness Capture                    │
├───────────────┬───────────────┬───────────────┬────────────┤
│   Ingestion   │  Processing   │    Storage    │   Export   │
│    Layer      │    Pipeline   │    Engine     │    API     │
├───────────────┼───────────────┼───────────────┼────────────┤
│ • Collectors  │ • Parsers     │ • Encryption  │ • REST API │
│ • Validators  │ • Normalizers │ • Database    │ • GraphQL  │
│ • Schedulers  │ • Enrichers   │ • File Store  │ • Webhooks │
│ • Monitors    │ • Indexers    │ • Replication │ • Streams  │
└───────────────┴───────────────┴───────────────┴────────────┘
```

### Data Flow

1. **Collection** → Raw data from sources
2. **Validation** → Schema and format checks
3. **Parsing** → Extract structured information
4. **Normalization** → Convert to standard format
5. **Enrichment** → Add metadata and context
6. **Encryption** → Secure the data
7. **Storage** → Persist to database/filesystem
8. **Indexing** → Enable fast retrieval

## Supported Data Streams

### Tier 1 (MVP)

| Stream Type | Formats | Priority | Status |
|------------|---------|----------|--------|
| Text Files | .txt, .md, .doc | HIGH | 🔄 Planning |
| Emails | IMAP, mbox, .eml | HIGH | 🔄 Planning |
| Chat Logs | WhatsApp, Telegram, Discord | HIGH | 🔄 Planning |
| Photos | JPEG, PNG, HEIC + EXIF | MEDIUM | 🔄 Planning |
| Calendar | .ics, Google, Outlook | MEDIUM | 🔄 Planning |

### Tier 2 (Post-MVP)

| Stream Type | Formats | Priority | Status |
|------------|---------|----------|--------|
| Social Media | Twitter, Facebook, LinkedIn | MEDIUM | 📋 Backlog |
| Code Repositories | Git history, commits | LOW | 📋 Backlog |
| Browser History | Chrome, Firefox, Safari | LOW | 📋 Backlog |
| Location Data | GPX, Google Timeline | LOW | 📋 Backlog |
| Biometrics | Heart rate, sleep, activity | LOW | 📋 Backlog |

## Data Schemas

### Event Schema (Core)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "timestamp", "type", "source", "content", "metadata"],
  "properties": {
    "id": {
      "type": "string",
      "description": "UUID v4 identifier"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "ISO 8601 timestamp of event"
    },
    "type": {
      "type": "string",
      "enum": ["message", "document", "media", "activity", "thought"],
      "description": "Classification of event"
    },
    "source": {
      "type": "object",
      "properties": {
        "platform": {"type": "string"},
        "account": {"type": "string"},
        "device": {"type": "string"}
      }
    },
    "content": {
      "type": "object",
      "description": "Actual event data (encrypted)"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "hash": {"type": "string"},
        "signature": {"type": "string"},
        "encryption": {"type": "string"},
        "version": {"type": "string"},
        "tags": {"type": "array", "items": {"type": "string"}},
        "consent": {"type": "object"}
      }
    }
  }
}
```

### Artifact Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["id", "type", "path", "metadata"],
  "properties": {
    "id": {
      "type": "string",
      "description": "Content hash (SHA-256)"
    },
    "type": {
      "type": "string",
      "enum": ["image", "video", "audio", "document", "archive"]
    },
    "path": {
      "type": "string",
      "description": "Storage location (encrypted)"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "original_name": {"type": "string"},
        "size": {"type": "integer"},
        "mime_type": {"type": "string"},
        "created": {"type": "string", "format": "date-time"},
        "modified": {"type": "string", "format": "date-time"},
        "extracted_text": {"type": "string"},
        "thumbnails": {"type": "array"}
      }
    }
  }
}
```

## API Specification

### REST Endpoints

```yaml
openapi: 3.0.0
paths:
  /ingest:
    post:
      summary: Submit data for ingestion
      requestBody:
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                source:
                  type: string
                data:
                  type: string
                  format: binary
      responses:
        '202':
          description: Accepted for processing
          content:
            application/json:
              schema:
                type: object
                properties:
                  job_id:
                    type: string
                  status_url:
                    type: string

  /events:
    get:
      summary: Query events
      parameters:
        - name: start_date
          in: query
          schema:
            type: string
            format: date-time
        - name: end_date
          in: query
          schema:
            type: string
            format: date-time
        - name: type
          in: query
          schema:
            type: string
        - name: source
          in: query
          schema:
            type: string
      responses:
        '200':
          description: List of events
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Event'

  /consent:
    put:
      summary: Update consent settings
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                source:
                  type: string
                consent_level:
                  type: string
                  enum: [none, metadata, full]
                retention_days:
                  type: integer
      responses:
        '200':
          description: Consent updated

  /delete:
    post:
      summary: Delete specific data (right to forget)
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                query:
                  type: object
                confirm:
                  type: boolean
      responses:
        '200':
          description: Deletion completed
```

## Privacy Framework

### Consent Levels

1. **None**: No data collection
2. **Metadata Only**: Timestamps, counts, but no content
3. **Anonymized**: Content with PII removed
4. **Full**: Complete data with user consent

### Data Retention

- Default: Indefinite with user control
- Configurable per source
- Automatic expiry support
- Batch deletion capabilities

### Encryption

```python
class EncryptionSpec:
    """
    All data at rest must be encrypted using:
    - AES-256-GCM for content
    - RSA-4096 for key management
    - Argon2id for key derivation
    """

    content_cipher = "AES-256-GCM"
    key_size = 256
    kdf = "Argon2id"
    kdf_iterations = 3
    kdf_memory = 64 * 1024  # 64MB
    kdf_parallelism = 4
```

## Implementation Roadmap

### Phase 1: MVP Core (Weeks 1-4)
- [ ] Basic ingestion framework
- [ ] Text and email parsers
- [ ] Local SQLite storage
- [ ] Simple encryption

### Phase 2: Enhanced Privacy (Weeks 5-8)
- [ ] Consent management system
- [ ] Advanced encryption
- [ ] Audit logging
- [ ] Right to forget implementation

### Phase 3: Scalability (Weeks 9-12)
- [ ] Distributed storage options
- [ ] Stream processing
- [ ] Performance optimization
- [ ] Monitoring and alerting

## Testing Requirements

### Unit Tests
- Parser accuracy: >95%
- Encryption/decryption roundtrip
- Schema validation
- API endpoint coverage: 100%

### Integration Tests
- End-to-end ingestion flows
- Multi-source synchronization
- Consent enforcement
- Data deletion verification

### Performance Tests
- Ingestion throughput
- Query latency
- Storage efficiency
- Memory usage under load

## Security Considerations

### Threat Model
1. **External attackers** trying to access stored data
2. **Malicious insiders** with system access
3. **Legal requests** for data disclosure
4. **User mistakes** (accidental deletion/exposure)

### Mitigations
- Zero-knowledge encryption where possible
- Principle of least privilege
- Secure key management (HSM support)
- Regular security audits
- Incident response procedures

## Dependencies

### Required Libraries
```python
# requirements.txt
pycryptodome==3.19.0  # Encryption
sqlalchemy==2.0.0     # Database ORM
fastapi==0.104.0      # REST API
pydantic==2.0.0       # Data validation
celery==5.3.0         # Task queue
redis==5.0.0          # Cache/queue backend
minio==7.2.0          # Object storage
```

### External Services (Optional)
- Cloud storage (S3-compatible)
- Message queue (RabbitMQ/Kafka)
- Time-series database (InfluxDB)
- Search engine (Elasticsearch)

## Monitoring & Observability

### Metrics
- Ingestion rate (events/second)
- Storage usage (GB)
- Error rates by source
- API latency (p50, p95, p99)
- Active users/sources

### Logging
- Structured JSON logs
- Log levels: DEBUG, INFO, WARN, ERROR
- Sensitive data redaction
- Centralized aggregation

### Alerting
- Failed ingestion jobs
- Storage capacity warnings
- Unusual access patterns
- Security events

## Glossary

- **Event**: Timestamped unit of activity or data
- **Artifact**: File or media object
- **Source**: Origin system/platform of data
- **Consent**: User permission for data processing
- **Provenance**: Chain of custody for data
- **PII**: Personally Identifiable Information

## References

- [GDPR Requirements](https://gdpr.eu/)
- [NIST Privacy Framework](https://www.nist.gov/privacy-framework)
- [Content-Addressable Storage](https://en.wikipedia.org/wiki/Content-addressable_storage)
- [Zero-Knowledge Encryption](https://en.wikipedia.org/wiki/Zero-knowledge_proof)

## Appendix A: Example Ingestion Flow

```python
# Example: Email ingestion pipeline
async def ingest_email(mbox_path: str, user_id: str):
    """
    Example email ingestion flow
    """
    # 1. Validate user consent
    consent = await check_consent(user_id, "email")
    if not consent.allowed:
        return

    # 2. Parse mbox file
    messages = parse_mbox(mbox_path)

    # 3. Process each message
    for msg in messages:
        # Extract metadata
        event = {
            "id": generate_uuid(),
            "timestamp": msg.date,
            "type": "message",
            "source": {
                "platform": "email",
                "account": msg.from_address
            },
            "content": encrypt_content(msg.body, user_id),
            "metadata": {
                "hash": hash_content(msg.body),
                "consent": consent.to_dict()
            }
        }

        # Store event
        await store_event(event)

        # Process attachments
        for attachment in msg.attachments:
            artifact = await store_artifact(attachment, user_id)
            await link_artifact_to_event(event["id"], artifact["id"])

    # 4. Update index
    await update_search_index(user_id, messages)

    return {"processed": len(messages)}
```

---

*This specification is a living document. Please submit PRs for improvements.*