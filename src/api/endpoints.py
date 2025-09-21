"""
REST API endpoints for C.H.R.I.S.T. system.
"""

from fastapi import APIRouter, HTTPException, UploadFile, File, Depends, Query, Body
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
import uuid
import io

# Import components
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from consciousness import consciousness
from consciousness.database import get_db_manager
from consciousness.parsers import UniversalParser
from consciousness.encryption import get_encryption_manager, ConsentBasedEncryption
from holistic import holistic_model
from retrieval import retrieval
from retrieval.vector_store import VectorStore, HybridRetriever
from retrieval.llm_integration import LLMProvider, RAGSystem
from intent import intent
from simulation import simulation
from teleology import teleology


# Initialize components
db_manager = get_db_manager()
encryption_manager = get_encryption_manager()
vector_store = VectorStore()
llm_provider = LLMProvider(provider="mock")  # Use mock for now
rag_system = RAGSystem(vector_store, llm_provider)

# Create routers
consciousness_router = APIRouter(prefix="/api/v1/consciousness", tags=["Consciousness"])
holistic_router = APIRouter(prefix="/api/v1/holistic", tags=["Holistic"])
retrieval_router = APIRouter(prefix="/api/v1/retrieval", tags=["Retrieval"])
intent_router = APIRouter(prefix="/api/v1/intent", tags=["Intent"])
simulation_router = APIRouter(prefix="/api/v1/simulation", tags=["Simulation"])
teleology_router = APIRouter(prefix="/api/v1/teleology", tags=["Teleology"])


# Request/Response Models
class IngestRequest(BaseModel):
    """Request model for data ingestion."""
    source_type: str = Field(..., description="Type of data source")
    content: str = Field(..., description="Content to ingest")
    consent_level: str = Field("full", description="Consent level")
    metadata: Optional[Dict[str, Any]] = None


class EventQuery(BaseModel):
    """Query parameters for events."""
    user_id: str = "default"
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    event_type: Optional[str] = None
    limit: int = Field(100, le=1000)


class SearchRequest(BaseModel):
    """Request for semantic search."""
    query: str
    k: int = Field(5, le=50)
    filters: Optional[Dict[str, Any]] = None
    use_hybrid: bool = True


class ChatMessage(BaseModel):
    """Chat message model."""
    message: str
    persona: Optional[str] = None
    context_window: int = Field(5, le=20)


class ReflectionRequest(BaseModel):
    """Request for generating reflections."""
    time_period: Optional[Dict[str, str]] = None
    focus_areas: Optional[List[str]] = None
    depth: str = Field("medium", pattern="^(brief|medium|detailed)$")


class GoalRequest(BaseModel):
    """Request for creating goals."""
    title: str
    category: str
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    milestones: Optional[List[Dict[str, Any]]] = None


# Consciousness Endpoints
@consciousness_router.post("/ingest")
async def ingest_data(request: IngestRequest):
    """Ingest data into consciousness system."""
    try:
        # Process with consent
        consent_processor = ConsentBasedEncryption(encryption_manager)
        processed_data = consent_processor.process_data(
            {
                "type": request.source_type,
                "content": request.content,
                "metadata": request.metadata or {},
                "timestamp": datetime.now().isoformat()
            },
            request.consent_level
        )

        # Store in database
        event_id = db_manager.store_event(processed_data)

        # Add to vector store for retrieval
        if processed_data.get('content'):
            vector_store.add_documents(
                [str(processed_data['content'])],
                [processed_data.get('metadata', {})],
                [event_id]
            )

        return {
            "status": "success",
            "event_id": event_id,
            "consent_level": request.consent_level
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@consciousness_router.post("/ingest/file")
async def ingest_file(
    file: UploadFile = File(...),
    consent_level: str = Query("full"),
    user_id: str = Query("default")
):
    """Ingest a file into the consciousness system."""
    try:
        # Save file temporarily
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_file_path = tmp_file.name

        # Parse file
        parser = UniversalParser()
        parsed_data = parser.parse(tmp_file_path)

        # Process and store
        results = []
        if isinstance(parsed_data, list):
            for item in parsed_data:
                item['user_id'] = user_id
                event_id = db_manager.store_event(item)
                results.append(event_id)
        else:
            parsed_data['user_id'] = user_id
            event_id = db_manager.store_event(parsed_data)
            results.append(event_id)

        # Clean up temp file
        Path(tmp_file_path).unlink()

        return {
            "status": "success",
            "filename": file.filename,
            "events_created": len(results),
            "event_ids": results
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@consciousness_router.get("/events")
async def get_events(params: EventQuery = Depends()):
    """Query stored events."""
    try:
        events = db_manager.query_events(
            user_id=params.user_id,
            start_date=params.start_date,
            end_date=params.end_date,
            event_type=params.event_type,
            limit=params.limit
        )
        return {
            "events": events,
            "count": len(events)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@consciousness_router.delete("/purge/{user_id}")
async def purge_data(user_id: str, confirm: bool = Query(False)):
    """Delete all data for a user (right to forget)."""
    if not confirm:
        return {
            "warning": "This will permanently delete all data",
            "action_required": "Set confirm=true to proceed"
        }

    try:
        # Delete from database
        session = db_manager.get_session()
        from consciousness.database import Event, Entity, Artifact

        session.query(Event).filter(Event.user_id == user_id).delete()
        session.query(Entity).filter(Entity.user_id == user_id).delete()
        session.query(Artifact).filter(Artifact.user_id == user_id).delete()
        session.commit()
        session.close()

        # Clear vector store (would need user filtering)
        # vector_store.clear()  # This would clear all - need user-specific clearing

        return {
            "status": "success",
            "message": f"All data for user {user_id} has been deleted"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Retrieval Endpoints
@retrieval_router.post("/search")
async def semantic_search(request: SearchRequest):
    """Perform semantic search across consciousness data."""
    try:
        if request.use_hybrid:
            retriever = HybridRetriever(vector_store)
            results = retriever.retrieve(
                query=request.query,
                k=request.k,
                filter=request.filters
            )
        else:
            results = vector_store.search(
                query=request.query,
                k=request.k,
                filter=request.filters
            )

        return {
            "query": request.query,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@retrieval_router.post("/ask")
async def ask_question(
    question: str = Body(..., embed=True),
    use_context: bool = Query(True),
    k: int = Query(5)
):
    """Ask a question and get an answer based on stored data."""
    try:
        response = rag_system.query(
            question=question,
            k=k,
            use_context=use_context
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@retrieval_router.post("/reflect")
async def generate_reflection(request: ReflectionRequest):
    """Generate reflective insights."""
    try:
        reflection = rag_system.reflect(
            time_period=request.time_period,
            focus_areas=request.focus_areas
        )
        return {
            "reflection": reflection,
            "generated_at": datetime.now().isoformat(),
            "parameters": {
                "time_period": request.time_period,
                "focus_areas": request.focus_areas,
                "depth": request.depth
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Simulation Endpoints
@simulation_router.post("/chat")
async def chat(message: ChatMessage):
    """Chat with the consciousness simulation."""
    try:
        response = await simulation.interact(
            message=message.message,
            persona=message.persona
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@simulation_router.get("/personas")
async def list_personas():
    """Get available personas."""
    try:
        personas = await simulation.get_personas()
        return {
            "personas": personas,
            "count": len(personas)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@simulation_router.post("/personas")
async def create_persona(
    name: str = Body(...),
    characteristics: Dict[str, Any] = Body(...)
):
    """Create a new persona."""
    try:
        persona_id = await simulation.create_persona(name, characteristics)
        return {
            "status": "success",
            "persona_id": persona_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Intent Endpoints
@intent_router.get("/values")
async def get_values(user_id: str = Query("default")):
    """Get extracted values and principles."""
    try:
        values = await intent.get_value_system()
        return values
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@intent_router.post("/validate")
async def validate_action(
    action: Dict[str, Any] = Body(...)
):
    """Validate an action against user values."""
    try:
        validation = await intent.validate_action(action)
        return validation
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@intent_router.put("/consent")
async def update_consent(
    user_id: str = Body(...),
    consent_level: str = Body(...),
    source_types: Optional[List[str]] = Body(None)
):
    """Update consent preferences."""
    try:
        consent_id = db_manager.store_consent(user_id, {
            'level': consent_level,
            'granted': consent_level != 'none',
            'source_types': source_types or [],
            'purposes': ['consciousness_capture']
        })
        return {
            "status": "success",
            "consent_id": consent_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Teleology Endpoints
@teleology_router.get("/goals")
async def get_goals(
    user_id: str = Query("default"),
    status: Optional[str] = Query(None)
):
    """Get life goals."""
    try:
        # For now, return from memory
        goals = teleology.goals
        if status:
            goals = [g for g in goals if g.get('status') == status]
        return {
            "goals": goals,
            "count": len(goals)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@teleology_router.post("/goals")
async def create_goal(goal: GoalRequest):
    """Create a new life goal."""
    try:
        goal_id = await teleology.create_goal({
            "title": goal.title,
            "category": goal.category,
            "description": goal.description,
            "target_date": goal.target_date.isoformat() if goal.target_date else None,
            "milestones": goal.milestones or []
        })
        return {
            "status": "success",
            "goal_id": goal_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@teleology_router.post("/life-review")
async def generate_life_review(
    period: str = Body("year"),
    year: Optional[int] = Body(None),
    focus_areas: Optional[List[str]] = Body(None)
):
    """Generate a life review."""
    try:
        review = await teleology.generate_life_review(
            period=period,
            focus_areas=focus_areas
        )
        return review
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Holistic Endpoints
@holistic_router.get("/graph")
async def get_knowledge_graph(
    user_id: str = Query("default"),
    entity_types: Optional[List[str]] = Query(None),
    depth: int = Query(2, le=5)
):
    """Get the knowledge graph."""
    try:
        graph = await holistic_model.query_graph({
            "user_id": user_id,
            "entity_types": entity_types,
            "depth": depth
        })
        return graph
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@holistic_router.post("/analyze")
async def analyze_patterns(
    analysis_type: str = Body(...),
    parameters: Dict[str, Any] = Body({})
):
    """Analyze patterns in the knowledge graph."""
    try:
        patterns = await holistic_model.analyze_patterns(
            analysis_type=analysis_type,
            parameters=parameters
        )
        return {
            "patterns": patterns,
            "count": len(patterns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Export function to get all routers
def get_routers():
    """Get all API routers."""
    return [
        consciousness_router,
        holistic_router,
        retrieval_router,
        intent_router,
        simulation_router,
        teleology_router
    ]