# C.H.R.I.S.T. API Specification

Version: 0.1.0
Status: Draft
Last Updated: 2025-01-20

## Overview

The C.H.R.I.S.T. system uses a modular API architecture where each component exposes well-defined interfaces for inter-component communication. This specification defines the REST API endpoints, GraphQL schema, and internal communication protocols.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                  API Gateway                         │
│              (Authentication & Routing)              │
└────────┬──────────┬──────────┬──────────┬──────────┘
         │          │          │          │
    ┌────▼────┐┌────▼────┐┌────▼────┐┌────▼────┐
    │    C    ││    H    ││   R/I   ││   S/T   │
    │  APIs   ││  APIs   ││  APIs   ││  APIs   │
    └─────────┘└─────────┘└─────────┘└─────────┘
```

## Base URL

```
Development: http://localhost:8000/api/v1
Production: https://api.christ.ai/v1
```

## Authentication

All API requests require authentication using JWT tokens.

```http
Authorization: Bearer <token>
```

### Token Structure
```json
{
  "sub": "user_id",
  "exp": 1234567890,
  "iat": 1234567890,
  "permissions": ["read", "write", "delete"],
  "components": ["C", "H", "R", "I", "S", "T"]
}
```

## Common Headers

```http
Content-Type: application/json
X-Request-ID: <uuid>
X-Client-Version: 0.1.0
```

## Error Response Format

```json
{
  "error": {
    "code": "INVALID_REQUEST",
    "message": "Human-readable error message",
    "details": {
      "field": "specific_field",
      "reason": "validation_failed"
    },
    "request_id": "550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2025-01-20T10:30:00Z"
  }
}
```

### Error Codes
| Code | HTTP Status | Description |
|------|-------------|-------------|
| UNAUTHORIZED | 401 | Authentication required |
| FORBIDDEN | 403 | Insufficient permissions |
| NOT_FOUND | 404 | Resource not found |
| INVALID_REQUEST | 400 | Malformed request |
| RATE_LIMITED | 429 | Too many requests |
| INTERNAL_ERROR | 500 | Server error |

## Component APIs

### C - Consciousness Capture

#### POST /consciousness/ingest
Submit data for ingestion.

**Request:**
```json
{
  "source_type": "email",
  "source_id": "gmail_account_1",
  "data": {
    "format": "mbox",
    "content": "base64_encoded_data"
  },
  "options": {
    "async": true,
    "priority": "normal",
    "consent_token": "user_consent_token"
  }
}
```

**Response:**
```json
{
  "job_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "estimated_completion": "2025-01-20T10:35:00Z",
  "status_url": "/jobs/550e8400-e29b-41d4-a716-446655440000"
}
```

#### GET /consciousness/events
Query stored events.

**Query Parameters:**
- `start_date` (ISO 8601)
- `end_date` (ISO 8601)
- `type` (message|activity|thought|media)
- `source` (string)
- `limit` (integer, default: 100)
- `offset` (integer, default: 0)

**Response:**
```json
{
  "events": [
    {
      "id": "event_id",
      "timestamp": "2025-01-20T10:30:00Z",
      "type": "message",
      "content": {
        "text": "encrypted_content"
      },
      "metadata": {}
    }
  ],
  "pagination": {
    "total": 1000,
    "limit": 100,
    "offset": 0,
    "has_more": true
  }
}
```

#### DELETE /consciousness/purge
Delete data (right to forget).

**Request:**
```json
{
  "criteria": {
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    },
    "sources": ["email", "chat"],
    "cascade": true
  },
  "confirmation_token": "delete_confirmation_token"
}
```

### H - Holistic Self-Model

#### GET /holistic/graph
Retrieve knowledge graph.

**Query Parameters:**
- `entity_types[]` (person|location|organization|concept)
- `relationship_types[]` (social|causal|temporal)
- `depth` (integer, graph traversal depth)
- `format` (json|graphml|cypher)

**Response:**
```json
{
  "nodes": [
    {
      "id": "node_1",
      "type": "person",
      "properties": {
        "name": "John Doe",
        "relationship": "friend"
      }
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source": "node_1",
      "target": "node_2",
      "type": "knows",
      "properties": {
        "since": "2020-01-01",
        "strength": 0.8
      }
    }
  ],
  "statistics": {
    "total_nodes": 500,
    "total_edges": 1200,
    "density": 0.0096
  }
}
```

#### POST /holistic/analyze
Analyze patterns and extract insights.

**Request:**
```json
{
  "analysis_type": "behavioral_pattern",
  "time_range": {
    "start": "2024-01-01",
    "end": "2024-12-31"
  },
  "parameters": {
    "min_frequency": 5,
    "confidence_threshold": 0.7
  }
}
```

**Response:**
```json
{
  "patterns": [
    {
      "type": "routine",
      "description": "Weekly gym visits on Tuesday/Thursday",
      "confidence": 0.85,
      "occurrences": 47,
      "insights": ["Consistent exercise pattern", "Health-conscious behavior"]
    }
  ]
}
```

### R - Retrieval & Reflection

#### POST /retrieval/search
Semantic search across consciousness.

**Request:**
```json
{
  "query": "conversations about career change",
  "filters": {
    "date_range": {
      "start": "2024-01-01",
      "end": "2024-12-31"
    },
    "sources": ["email", "journal"]
  },
  "options": {
    "semantic_search": true,
    "include_context": true,
    "max_results": 20
  }
}
```

**Response:**
```json
{
  "results": [
    {
      "id": "result_1",
      "score": 0.92,
      "type": "journal_entry",
      "timestamp": "2024-06-15T10:30:00Z",
      "content": {
        "text": "Today I've been thinking about...",
        "highlights": ["career change", "new opportunities"]
      },
      "context": {
        "before": "Previous journal entry...",
        "after": "Next journal entry..."
      }
    }
  ],
  "query_understanding": {
    "intent": "career_reflection",
    "entities": ["career", "change"],
    "temporal_focus": "past_year"
  }
}
```

#### POST /reflection/generate
Generate reflective insights.

**Request:**
```json
{
  "reflection_type": "monthly_summary",
  "time_period": "2024-12",
  "focus_areas": ["productivity", "relationships", "health"],
  "depth": "detailed"
}
```

**Response:**
```json
{
  "reflection": {
    "period": "December 2024",
    "themes": [
      {
        "theme": "Increased social activity",
        "evidence": ["15 social events", "50% more than November"],
        "sentiment": "positive"
      }
    ],
    "insights": [
      "You were more socially active during the holiday season",
      "Work-life balance improved compared to previous months"
    ],
    "suggestions": [
      "Consider maintaining social connections in January"
    ]
  }
}
```

### I - Intent & Integrity

#### GET /intent/values
Retrieve extracted values and principles.

**Response:**
```json
{
  "values": [
    {
      "id": "value_1",
      "principle": "honesty",
      "importance": 0.95,
      "evidence_count": 234,
      "sources": ["journal", "email"],
      "examples": ["Always told the truth even when..."]
    }
  ],
  "ethical_framework": {
    "primary_orientation": "virtue_ethics",
    "decision_patterns": ["consequentialist", "deontological"]
  }
}
```

#### POST /intent/validate
Validate action against value system.

**Request:**
```json
{
  "action": {
    "type": "response",
    "content": "I should tell them what they want to hear",
    "context": "Friend asking for advice"
  }
}
```

**Response:**
```json
{
  "validation": {
    "aligned": false,
    "conflicts": [
      {
        "value": "honesty",
        "severity": "high",
        "explanation": "Action conflicts with commitment to truthfulness"
      }
    ],
    "suggestions": [
      "Consider providing honest but compassionate feedback"
    ]
  }
}
```

### S - Simulation Engine

#### POST /simulation/interact
Interact with consciousness simulation.

**Request:**
```json
{
  "message": "What did we discuss about the project last week?",
  "context": {
    "persona": "professional",
    "conversation_id": "conv_123",
    "temperature": 0.7
  }
}
```

**Response:**
```json
{
  "response": "Last week we discussed the project timeline and agreed to prioritize the authentication module. You mentioned concerns about the database schema that we should address.",
  "metadata": {
    "confidence": 0.85,
    "sources_used": ["email:2024-12-15", "calendar:2024-12-14"],
    "persona_match": 0.92
  }
}
```

#### GET /simulation/personas
List available personas.

**Response:**
```json
{
  "personas": [
    {
      "id": "professional",
      "name": "Professional",
      "description": "Work and career focused responses",
      "traits": ["formal", "detail-oriented", "analytical"],
      "use_cases": ["work_emails", "professional_advice"]
    },
    {
      "id": "casual",
      "name": "Casual",
      "description": "Relaxed, friendly communication",
      "traits": ["humorous", "informal", "empathetic"],
      "use_cases": ["friend_chats", "social_media"]
    }
  ]
}
```

### T - Teleology & Transformation

#### GET /teleology/goals
Retrieve life goals and progress.

**Response:**
```json
{
  "goals": [
    {
      "id": "goal_1",
      "title": "Learn Spanish",
      "category": "personal_development",
      "created": "2024-01-01",
      "target_date": "2025-01-01",
      "progress": 0.65,
      "milestones": [
        {
          "title": "Complete beginner course",
          "completed": true,
          "date": "2024-06-01"
        }
      ],
      "related_activities": ["Duolingo sessions", "Spanish conversation meetups"]
    }
  ],
  "life_themes": [
    "continuous_learning",
    "cultural_exploration"
  ]
}
```

#### POST /teleology/review
Generate life review.

**Request:**
```json
{
  "period": "year",
  "year": 2024,
  "focus_areas": ["goals", "relationships", "growth"],
  "format": "narrative"
}
```

**Response:**
```json
{
  "review": {
    "narrative": "2024 was a year of significant personal growth...",
    "achievements": [
      "Completed 3 major projects",
      "Strengthened family relationships"
    ],
    "challenges": [
      "Work-life balance during Q3"
    ],
    "growth_areas": [
      "Improved communication skills",
      "Better stress management"
    ],
    "recommendations_2025": [
      "Continue focus on health",
      "Explore new creative outlets"
    ]
  }
}
```

## GraphQL API

### Schema Overview

```graphql
type Query {
  # Consciousness queries
  events(filter: EventFilter, pagination: PaginationInput): EventConnection
  artifacts(filter: ArtifactFilter): [Artifact]

  # Holistic model queries
  entities(type: EntityType): [Entity]
  relationships(filter: RelationshipFilter): [Relationship]
  graph(depth: Int, startNode: ID): Graph

  # Retrieval queries
  search(query: String!, options: SearchOptions): SearchResults

  # Intent queries
  values: [Value]
  validateAction(action: ActionInput): ValidationResult

  # Simulation queries
  personas: [Persona]
  interact(message: String!, context: InteractionContext): InteractionResponse

  # Teleology queries
  goals(status: GoalStatus): [Goal]
  lifeReview(period: Period, focus: [String]): LifeReview
}

type Mutation {
  # Consciousness mutations
  ingestData(input: IngestInput!): IngestJob
  deleteData(criteria: DeleteCriteria!): DeleteResult

  # Holistic model mutations
  addEntity(input: EntityInput!): Entity
  linkEntities(source: ID!, target: ID!, relationship: RelationshipInput!): Relationship

  # Intent mutations
  updateValues(values: [ValueInput]!): [Value]

  # Simulation mutations
  createPersona(input: PersonaInput!): Persona
  updatePersona(id: ID!, input: PersonaInput!): Persona

  # Teleology mutations
  createGoal(input: GoalInput!): Goal
  updateGoal(id: ID!, progress: Float, milestones: [MilestoneInput]): Goal
}

type Subscription {
  # Real-time updates
  ingestionProgress(jobId: ID!): IngestJobUpdate
  newEvents(filter: EventFilter): Event
  goalProgress(goalId: ID!): GoalUpdate
}
```

### Example Queries

#### Complex Graph Query
```graphql
query GetSocialNetwork {
  graph(depth: 3, startNode: "self") {
    nodes {
      id
      type
      properties
    }
    edges {
      source
      target
      type
      weight
    }
    statistics {
      totalNodes
      totalEdges
      averageDegree
      clustering
    }
  }
}
```

#### Life Summary Query
```graphql
query GetLifeSummary($year: Int!) {
  lifeReview(period: YEAR, focus: ["goals", "relationships"]) {
    narrative
    achievements
    challenges
  }
  goals(status: ACTIVE) {
    title
    progress
    targetDate
  }
  events(filter: {year: $year, type: SIGNIFICANT}) {
    edges {
      node {
        id
        timestamp
        description
        impact
      }
    }
  }
}
```

## WebSocket API

For real-time communication and streaming responses.

### Connection
```javascript
const ws = new WebSocket('wss://api.christ.ai/v1/stream');

ws.onopen = () => {
  ws.send(JSON.stringify({
    type: 'authenticate',
    token: 'jwt_token'
  }));
};
```

### Message Types

#### Subscribe to Events
```json
{
  "type": "subscribe",
  "channel": "events",
  "filters": {
    "types": ["message", "thought"]
  }
}
```

#### Stream Interaction
```json
{
  "type": "interact",
  "message": "Tell me about my day",
  "stream": true
}
```

#### Receive Streamed Response
```json
{
  "type": "response_chunk",
  "content": "Based on your calendar, today you had...",
  "done": false
}
```

## Rate Limiting

| Endpoint | Rate Limit | Window |
|----------|------------|---------|
| /consciousness/ingest | 100 | 1 hour |
| /retrieval/search | 1000 | 1 hour |
| /simulation/interact | 500 | 1 hour |
| GraphQL | 5000 points | 1 hour |

### Rate Limit Headers
```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1640995200
```

## Pagination

### Cursor-Based Pagination
```json
{
  "data": [...],
  "pagination": {
    "cursor": "eyJpZCI6MTAwfQ==",
    "has_next": true,
    "has_previous": false
  }
}
```

### Offset-Based Pagination
```json
{
  "data": [...],
  "pagination": {
    "total": 1000,
    "limit": 20,
    "offset": 0,
    "pages": 50
  }
}
```

## Webhooks

Configure webhooks for async events.

### Webhook Events
- `ingestion.completed`
- `ingestion.failed`
- `analysis.ready`
- `goal.achieved`
- `anomaly.detected`

### Webhook Payload
```json
{
  "event": "ingestion.completed",
  "timestamp": "2025-01-20T10:30:00Z",
  "data": {
    "job_id": "550e8400-e29b-41d4-a716-446655440000",
    "source": "email",
    "events_processed": 150,
    "duration_seconds": 45
  }
}
```

## SDK Examples

### Python
```python
from christ import ChristClient

client = ChristClient(api_key="your_api_key")

# Ingest data
job = client.consciousness.ingest(
    source_type="email",
    data=email_data
)

# Search memories
results = client.retrieval.search(
    query="vacation plans",
    date_range=("2024-01-01", "2024-12-31")
)

# Interact with simulation
response = client.simulation.interact(
    message="What should I focus on today?",
    persona="professional"
)
```

### JavaScript/TypeScript
```typescript
import { ChristClient } from '@christ/client';

const client = new ChristClient({ apiKey: 'your_api_key' });

// GraphQL query
const result = await client.graphql({
  query: `
    query GetRecentEvents {
      events(filter: { days: 7 }) {
        edges {
          node {
            id
            type
            content
          }
        }
      }
    }
  `
});

// REST API call
const searchResults = await client.retrieval.search({
  query: 'important decisions',
  options: { semantic: true }
});
```

## Testing

### Test Environment
```
Base URL: https://sandbox.christ.ai/v1
Test API Key: test_key_xxxxx
```

### Postman Collection
Available at: https://christ.ai/api/postman-collection.json

### Example cURL
```bash
curl -X POST https://api.christ.ai/v1/retrieval/search \
  -H "Authorization: Bearer your_token" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "meetings last week",
    "filters": {
      "sources": ["calendar", "email"]
    }
  }'
```

## Versioning

API versions are included in the URL path:
- Current: `/v1`
- Beta: `/v2-beta`
- Deprecated: `/v0` (sunset date: 2025-06-01)

### Breaking Changes Policy
- 6-month deprecation notice
- Migration guides provided
- Backward compatibility maintained when possible

## Security

### Best Practices
1. Always use HTTPS in production
2. Rotate API keys regularly
3. Implement request signing for sensitive operations
4. Use webhook signatures to verify authenticity
5. Enable audit logging for all API access

### CORS Policy
```http
Access-Control-Allow-Origin: https://app.christ.ai
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

*API documentation is auto-generated from OpenAPI specs. See `/docs` endpoint for interactive documentation.*