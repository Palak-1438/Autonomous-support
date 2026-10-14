import uuid
from datetime import datetime, timezone
from fastapi import FastAPI

from app.config import get_settings
from app.domains.registry import get_registry
from app.schemas.api import (
    ConversationCreate,
    ConversationResponse,
    MessageCreate,
    MessageResponse,
)
from app.schemas.common import HealthResponse
from app.orchestration.graph import app_graph

app = FastAPI(title="Autonomous Support API")

def utcnow() -> datetime:
    return datetime.now(timezone.utc)

@app.get("/health", response_model=HealthResponse)
def health_check():
    settings = get_settings()
    registry = get_registry()
    domain_count = len(registry.all())

    return HealthResponse(
        status="ok",
        llm_mode=settings.llm_mode,
        database="connected",
        domains=domain_count,
    )

@app.post("/api/conversations", response_model=ConversationResponse)
def create_conversation(request: ConversationCreate):
    return ConversationResponse(
        id=f"conv_{uuid.uuid4().hex[:16]}",
        tenant_id="tenant_demo",
        domain=request.domain_hint or "unknown",
        status="OPEN",
        messages=[],
        created_at=utcnow(),
    )

@app.post("/api/conversations/{conversation_id}/messages", response_model=MessageResponse)
def add_message(conversation_id: str, request: MessageCreate):
    content = request.content
    msg_id = f"msg_{uuid.uuid4().hex[:16]}"

    initial_state = {
        "content": content,
        "classification": None,
        "specialist": None,
        "supervisor": None,
        "response_content": None,
        "escalated": False
    }

    final_state = app_graph.invoke(initial_state)

    return MessageResponse(
        id=msg_id,
        role="assistant",
        content=final_state.get("response_content", "Error processing request"),
        created_at=utcnow(),
        classification=final_state.get("classification"),
        specialist=final_state.get("specialist"),
        supervisor=final_state.get("supervisor"),
    )
