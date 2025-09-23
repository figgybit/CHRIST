# C.H.R.I.S.T. Data Schema Standards

Version: 0.1.0
Last Updated: 2025-01-20
Status: Draft

## Overview

This document defines the standardized data schemas used across all C.H.R.I.S.T. components. These schemas ensure consistent data representation, enable interoperability between modules, and facilitate privacy-preserving operations.

## Core Principles

1. **Extensibility**: Schemas can be extended without breaking compatibility
2. **Privacy-First**: PII fields are clearly marked and encrypted
3. **Temporal Awareness**: All data includes temporal context
4. **Provenance Tracking**: Source and transformation history preserved
5. **Semantic Richness**: Sufficient metadata for AI/ML processing

## Schema Hierarchy

```
Base Schema
├── Event (timestamped occurrences)
│   ├── Message Event
│   ├── Activity Event
│   ├── Thought Event
│   └── Media Event
├── Entity (persons, places, things)
│   ├── Person Entity
│   ├── Location Entity
│   ├── Organization Entity
│   └── Concept Entity
├── Relationship (connections between entities/events)
│   ├── Social Relationship
│   ├── Causal Relationship
│   └── Temporal Relationship
└── Artifact (files and documents)
    ├── Document Artifact
    ├── Media Artifact
    └── Code Artifact
```

## Base Schema

All data objects inherit from this base schema:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://christs.ai/schemas/base.json",
  "type": "object",
  "required": ["id", "created_at", "schema_version"],
  "properties": {
    "id": {
      "type": "string",
      "format": "uuid",
      "description": "Unique identifier (UUID v4)"
    },
    "created_at": {
      "type": "string",
      "format": "date-time",
      "description": "Creation timestamp (ISO 8601)"
    },
    "updated_at": {
      "type": "string",
      "format": "date-time",
      "description": "Last modification timestamp"
    },
    "schema_version": {
      "type": "string",
      "pattern": "^\\d+\\.\\d+\\.\\d+$",
      "description": "Schema version (semver)"
    },
    "metadata": {
      "type": "object",
      "properties": {
        "source": {
          "type": "string",
          "description": "Data source identifier"
        },
        "confidence": {
          "type": "number",
          "minimum": 0,
          "maximum": 1,
          "description": "Confidence score (0-1)"
        },
        "processing_history": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "timestamp": {"type": "string", "format": "date-time"},
              "operation": {"type": "string"},
              "agent": {"type": "string"}
            }
          }
        }
      }
    }
  }
}
```

## Event Schemas

### Message Event

For emails, chats, SMS, social media posts:

```json
{
  "$id": "https://christs.ai/schemas/event/message.json",
  "allOf": [{"$ref": "base.json"}],
  "type": "object",
  "required": ["event_type", "timestamp", "content"],
  "properties": {
    "event_type": {
      "const": "message"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time",
      "description": "When the message was sent/received"
    },
    "content": {
      "type": "object",
      "properties": {
        "text": {
          "type": "string",
          "description": "Message text (encrypted)"
        },
        "html": {
          "type": "string",
          "description": "HTML version if available"
        },
        "summary": {
          "type": "string",
          "description": "AI-generated summary"
        }
      }
    },
    "participants": {
      "type": "object",
      "properties": {
        "from": {
          "$ref": "#/definitions/participant"
        },
        "to": {
          "type": "array",
          "items": {"$ref": "#/definitions/participant"}
        },
        "cc": {
          "type": "array",
          "items": {"$ref": "#/definitions/participant"}
        }
      }
    },
    "platform": {
      "type": "string",
      "enum": ["email", "sms", "whatsapp", "telegram", "discord", "slack", "twitter", "facebook", "linkedin", "other"]
    },
    "thread_id": {
      "type": "string",
      "description": "Conversation thread identifier"
    },
    "attachments": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "artifact_id": {"type": "string"},
          "filename": {"type": "string"},
          "mime_type": {"type": "string"},
          "size": {"type": "integer"}
        }
      }
    },
    "sentiment": {
      "type": "object",
      "properties": {
        "polarity": {"type": "number", "minimum": -1, "maximum": 1},
        "emotions": {
          "type": "object",
          "properties": {
            "joy": {"type": "number"},
            "sadness": {"type": "number"},
            "anger": {"type": "number"},
            "fear": {"type": "number"},
            "surprise": {"type": "number"}
          }
        }
      }
    }
  },
  "definitions": {
    "participant": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "name": {"type": "string"},
        "email": {"type": "string", "format": "email"},
        "phone": {"type": "string"},
        "is_self": {"type": "boolean"}
      }
    }
  }
}
```

### Activity Event

For calendar events, location checkins, health activities:

```json
{
  "$id": "https://christs.ai/schemas/event/activity.json",
  "allOf": [{"$ref": "base.json"}],
  "type": "object",
  "required": ["event_type", "activity_type", "start_time"],
  "properties": {
    "event_type": {
      "const": "activity"
    },
    "activity_type": {
      "type": "string",
      "enum": ["meeting", "travel", "exercise", "meal", "sleep", "work", "entertainment", "social", "health", "other"]
    },
    "start_time": {
      "type": "string",
      "format": "date-time"
    },
    "end_time": {
      "type": "string",
      "format": "date-time"
    },
    "duration_minutes": {
      "type": "integer",
      "minimum": 0
    },
    "title": {
      "type": "string"
    },
    "description": {
      "type": "string"
    },
    "location": {
      "type": "object",
      "properties": {
        "name": {"type": "string"},
        "address": {"type": "string"},
        "coordinates": {
          "type": "object",
          "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"},
            "altitude": {"type": "number"}
          }
        }
      }
    },
    "participants": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "person_id": {"type": "string"},
          "name": {"type": "string"},
          "role": {"type": "string"}
        }
      }
    },
    "metrics": {
      "type": "object",
      "description": "Activity-specific metrics",
      "additionalProperties": true
    }
  }
}
```

### Thought Event

For journal entries, notes, voice memos:

```json
{
  "$id": "https://christs.ai/schemas/event/thought.json",
  "allOf": [{"$ref": "base.json"}],
  "type": "object",
  "required": ["event_type", "timestamp", "content"],
  "properties": {
    "event_type": {
      "const": "thought"
    },
    "timestamp": {
      "type": "string",
      "format": "date-time"
    },
    "content": {
      "type": "object",
      "properties": {
        "text": {
          "type": "string",
          "description": "Thought content (encrypted)"
        },
        "title": {
          "type": "string"
        },
        "format": {
          "type": "string",
          "enum": ["markdown", "plain", "html", "audio_transcript"]
        }
      }
    },
    "thought_type": {
      "type": "string",
      "enum": ["journal", "idea", "reflection", "goal", "dream", "memory", "note", "other"]
    },
    "topics": {
      "type": "array",
      "items": {"type": "string"}
    },
    "mood": {
      "type": "object",
      "properties": {
        "valence": {"type": "number", "minimum": -1, "maximum": 1},
        "arousal": {"type": "number", "minimum": 0, "maximum": 1},
        "descriptors": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "privacy_level": {
      "type": "string",
      "enum": ["private", "trusted", "public"],
      "default": "private"
    }
  }
}
```

## Entity Schemas

### Person Entity

```json
{
  "$id": "https://christs.ai/schemas/entity/person.json",
  "allOf": [{"$ref": "base.json"}],
  "type": "object",
  "required": ["entity_type", "names"],
  "properties": {
    "entity_type": {
      "const": "person"
    },
    "names": {
      "type": "object",
      "properties": {
        "full": {"type": "string"},
        "given": {"type": "string"},
        "family": {"type": "string"},
        "nicknames": {
          "type": "array",
          "items": {"type": "string"}
        }
      }
    },
    "relationship": {
      "type": "string",
      "enum": ["self", "family", "friend", "colleague", "acquaintance", "public_figure", "other"]
    },
    "contact_info": {
      "type": "object",
      "properties": {
        "emails": {"type": "array", "items": {"type": "string"}},
        "phones": {"type": "array", "items": {"type": "string"}},
        "addresses": {"type": "array", "items": {"type": "object"}},
        "social_media": {"type": "object"}
      }
    },
    "demographics": {
      "type": "object",
      "properties": {
        "birth_date": {"type": "string", "format": "date"},
        "gender": {"type": "string"},
        "occupation": {"type": "string"},
        "organization": {"type": "string"}
      }
    },
    "interaction_stats": {
      "type": "object",
      "properties": {
        "first_interaction": {"type": "string", "format": "date-time"},
        "last_interaction": {"type": "string", "format": "date-time"},
        "total_interactions": {"type": "integer"},
        "communication_frequency": {"type": "string"}
      }
    },
    "notes": {
      "type": "string",
      "description": "Personal notes about this person"
    }
  }
}
```

### Location Entity

```json
{
  "$id": "https://christs.ai/schemas/entity/location.json",
  "allOf": [{"$ref": "base.json"}],
  "type": "object",
  "required": ["entity_type", "name"],
  "properties": {
    "entity_type": {
      "const": "location"
    },
    "name": {
      "type": "string"
    },
    "type": {
      "type": "string",
      "enum": ["home", "work", "school", "restaurant", "store", "park", "transit", "city", "country", "other"]
    },
    "address": {
      "type": "object",
      "properties": {
        "street": {"type": "string"},
        "city": {"type": "string"},
        "state": {"type": "string"},
        "country": {"type": "string"},
        "postal_code": {"type": "string"}
      }
    },
    "coordinates": {
      "type": "object",
      "properties": {
        "latitude": {"type": "number"},
        "longitude": {"type": "number"},
        "altitude": {"type": "number"}
      }
    },
    "visit_stats": {
      "type": "object",
      "properties": {
        "first_visit": {"type": "string", "format": "date-time"},
        "last_visit": {"type": "string", "format": "date-time"},
        "total_visits": {"type": "integer"},
        "average_duration_minutes": {"type": "number"}
      }
    },
    "significance": {
      "type": "string",
      "description": "Personal significance of this location"
    }
  }
}
```

## Relationship Schema

```json
{
  "$id": "https://christs.ai/schemas/relationship.json",
  "allOf": [{"$ref": "base.json"}],
  "type": "object",
  "required": ["relationship_type", "source_id", "target_id"],
  "properties": {
    "relationship_type": {
      "type": "string",
      "enum": ["social", "causal", "temporal", "spatial", "semantic", "emotional"]
    },
    "source_id": {
      "type": "string",
      "description": "ID of source entity/event"
    },
    "source_type": {
      "type": "string",
      "enum": ["event", "entity", "artifact"]
    },
    "target_id": {
      "type": "string",
      "description": "ID of target entity/event"
    },
    "target_type": {
      "type": "string",
      "enum": ["event", "entity", "artifact"]
    },
    "properties": {
      "type": "object",
      "description": "Relationship-specific properties",
      "additionalProperties": true
    },
    "strength": {
      "type": "number",
      "minimum": 0,
      "maximum": 1,
      "description": "Relationship strength (0-1)"
    },
    "bidirectional": {
      "type": "boolean",
      "default": false
    },
    "temporal_bounds": {
      "type": "object",
      "properties": {
        "start": {"type": "string", "format": "date-time"},
        "end": {"type": "string", "format": "date-time"}
      }
    }
  }
}
```

## Artifact Schema

```json
{
  "$id": "https://christs.ai/schemas/artifact.json",
  "allOf": [{"$ref": "base.json"}],
  "type": "object",
  "required": ["artifact_type", "storage_path", "hash"],
  "properties": {
    "artifact_type": {
      "type": "string",
      "enum": ["document", "image", "video", "audio", "code", "archive", "other"]
    },
    "storage_path": {
      "type": "string",
      "description": "Encrypted storage location"
    },
    "hash": {
      "type": "object",
      "properties": {
        "algorithm": {"type": "string", "enum": ["sha256", "sha512", "blake3"]},
        "value": {"type": "string"}
      }
    },
    "encryption": {
      "type": "object",
      "properties": {
        "algorithm": {"type": "string"},
        "key_id": {"type": "string"},
        "encrypted": {"type": "boolean"}
      }
    },
    "file_info": {
      "type": "object",
      "properties": {
        "original_name": {"type": "string"},
        "size_bytes": {"type": "integer"},
        "mime_type": {"type": "string"},
        "extension": {"type": "string"}
      }
    },
    "content_analysis": {
      "type": "object",
      "properties": {
        "text_content": {"type": "string"},
        "language": {"type": "string"},
        "summary": {"type": "string"},
        "keywords": {"type": "array", "items": {"type": "string"}},
        "entities_detected": {"type": "array", "items": {"type": "string"}},
        "ocr_performed": {"type": "boolean"},
        "transcription": {"type": "string"}
      }
    },
    "media_metadata": {
      "type": "object",
      "properties": {
        "width": {"type": "integer"},
        "height": {"type": "integer"},
        "duration_seconds": {"type": "number"},
        "framerate": {"type": "number"},
        "bitrate": {"type": "integer"},
        "codec": {"type": "string"},
        "exif": {"type": "object"},
        "location": {
          "type": "object",
          "properties": {
            "latitude": {"type": "number"},
            "longitude": {"type": "number"}
          }
        }
      }
    }
  }
}
```

## Privacy Annotations

Special fields that require encryption:

```json
{
  "$id": "https://christs.ai/schemas/privacy-annotations.json",
  "type": "object",
  "properties": {
    "pii_fields": {
      "type": "array",
      "description": "Fields containing personally identifiable information",
      "items": {
        "type": "string"
      },
      "examples": [
        "content.text",
        "participants.from.email",
        "location.coordinates",
        "contact_info",
        "demographics.birth_date"
      ]
    },
    "encryption_required": {
      "type": "boolean",
      "description": "Whether this data must be encrypted at rest"
    },
    "consent_level_minimum": {
      "type": "string",
      "enum": ["none", "metadata", "anonymized", "full"],
      "description": "Minimum consent level required"
    },
    "retention_policy": {
      "type": "object",
      "properties": {
        "default_days": {"type": "integer"},
        "maximum_days": {"type": "integer"},
        "deletion_method": {
          "type": "string",
          "enum": ["soft", "hard", "crypto_erase"]
        }
      }
    }
  }
}
```

## Validation Rules

### Required Field Validation
```python
def validate_required_fields(data: dict, schema: dict) -> List[str]:
    """Validate that all required fields are present."""
    errors = []
    for field in schema.get("required", []):
        if field not in data:
            errors.append(f"Missing required field: {field}")
    return errors
```

### Temporal Consistency
```python
def validate_temporal_consistency(data: dict) -> List[str]:
    """Ensure temporal fields are logically consistent."""
    errors = []
    if "start_time" in data and "end_time" in data:
        if data["end_time"] < data["start_time"]:
            errors.append("end_time cannot be before start_time")
    return errors
```

### Privacy Field Encryption
```python
def validate_encryption(data: dict, schema: dict) -> List[str]:
    """Ensure PII fields are properly encrypted."""
    errors = []
    pii_fields = schema.get("pii_fields", [])
    for field_path in pii_fields:
        value = get_nested_field(data, field_path)
        if value and not is_encrypted(value):
            errors.append(f"PII field {field_path} is not encrypted")
    return errors
```

## Schema Evolution

### Versioning Strategy
- **Major**: Breaking changes (field removal, type changes)
- **Minor**: Additive changes (new optional fields)
- **Patch**: Documentation updates, bug fixes

### Migration Path
```python
class SchemaMigrator:
    """Handle schema version migrations."""

    migrations = {
        "1.0.0->2.0.0": migrate_v1_to_v2,
        "2.0.0->2.1.0": migrate_v2_0_to_v2_1,
    }

    def migrate(self, data: dict, from_version: str, to_version: str) -> dict:
        """Migrate data between schema versions."""
        path = self.find_migration_path(from_version, to_version)
        for migration in path:
            data = self.migrations[migration](data)
        return data
```

## Implementation Guidelines

### Schema Validation
```python
from jsonschema import validate, ValidationError

def validate_data(data: dict, schema_id: str) -> bool:
    """Validate data against schema."""
    schema = load_schema(schema_id)
    try:
        validate(instance=data, schema=schema)
        return True
    except ValidationError as e:
        log_validation_error(e)
        return False
```

### Serialization
```python
import json
from datetime import datetime
from decimal import Decimal

class ChristJSONEncoder(json.JSONEncoder):
    """Custom JSON encoder for C.H.R.I.S.T. data types."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, Decimal):
            return float(obj)
        elif isinstance(obj, bytes):
            return obj.hex()
        return super().default(obj)
```

## Testing Requirements

### Schema Test Coverage
- Valid data acceptance
- Invalid data rejection
- Edge cases (nulls, empty strings, boundary values)
- Schema evolution compatibility
- Performance with large datasets

### Example Test
```python
def test_message_event_schema():
    """Test message event schema validation."""
    valid_message = {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "created_at": "2025-01-20T10:30:00Z",
        "schema_version": "1.0.0",
        "event_type": "message",
        "timestamp": "2025-01-20T10:30:00Z",
        "content": {
            "text": "Hello, world!"
        },
        "platform": "email"
    }

    assert validate_data(valid_message, "event/message.json") == True

    invalid_message = valid_message.copy()
    del invalid_message["timestamp"]
    assert validate_data(invalid_message, "event/message.json") == False
```

## Performance Considerations

### Indexing Strategy
```sql
-- Recommended indexes for common queries
CREATE INDEX idx_events_timestamp ON events(timestamp);
CREATE INDEX idx_events_type ON events(event_type);
CREATE INDEX idx_entities_type ON entities(entity_type);
CREATE INDEX idx_relationships_source ON relationships(source_id);
CREATE INDEX idx_relationships_target ON relationships(target_id);
CREATE INDEX idx_artifacts_hash ON artifacts(hash);
```

### Storage Optimization
- Use compression for text content (gzip/brotli)
- Store media artifacts separately from metadata
- Implement tiered storage (hot/warm/cold)
- Use columnar storage for analytics queries

## Security Notes

### Encryption Requirements
- All PII fields must use AES-256-GCM
- Keys must be derived using Argon2id
- Implement key rotation every 90 days
- Support hardware security modules (HSM)

### Access Control
- Field-level access control for PII
- Audit all data access
- Implement rate limiting
- Support zero-knowledge proofs where applicable

---

*Schema standards are enforced via automated validation in CI/CD pipeline.*