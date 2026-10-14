from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.orchestration import ClassificationResult, SpecialistResult, SupervisorDecision

CaseStatus = Literal["OPEN", "ASSIGNED", "IN_PROGRESS", "RESOLVED", "CLOSED"]


class ConversationCreate(BaseModel):
    domain_hint: str | None = None
    customer_external_id: str | None = None
    channel: str = "api"


class MessageCreate(BaseModel):
    content: str = Field(min_length=1, max_length=8000)
    confirm_sensitive_action: bool = False


class MessageResponse(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime
    classification: ClassificationResult | None = None
    specialist: SpecialistResult | None = None
    supervisor: SupervisorDecision | None = None
    case_id: str | None = None


class ConversationResponse(BaseModel):
    id: str
    tenant_id: str
    domain: str | None
    status: str
    messages: list[MessageResponse] = Field(default_factory=list)
    case_id: str | None = None
    created_at: datetime


class AssignCaseRequest(BaseModel):
    assignee_id: str | None = None


class ResolveCaseRequest(BaseModel):
    resolution: str = Field(min_length=1, max_length=8000)
    return_to_automation: bool = False
    close: bool = False


class CaseResponse(BaseModel):
    id: str
    tenant_id: str
    domain: str
    conversation_id: str
    status: CaseStatus
    customer_request: str
    classification: dict[str, Any] | None = None
    specialist_id: str | None = None
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    tool_results: list[dict[str, Any]] = Field(default_factory=list)
    escalation_reason: str
    risk_level: str
    urgency: str
    draft_response: str | None = None
    assigned_to: str | None = None
    sla_due_at: datetime | None = None
    created_at: datetime
    updated_at: datetime
    history: list[dict[str, Any]] = Field(default_factory=list)
