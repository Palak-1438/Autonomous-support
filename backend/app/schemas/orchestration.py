from typing import Any, Literal

from pydantic import BaseModel, Field


Urgency = Literal["low", "medium", "high", "critical"]
RiskLevel = Literal["low", "medium", "high", "restricted"]
SupervisorOutcome = Literal["APPROVE", "RETRY", "ESCALATE"]


class ClassificationResult(BaseModel):
    domain: str
    intent: str
    selected_specialist: str
    routing_confidence: float = Field(ge=0, le=1)
    urgency: Urgency = "medium"
    risk_level: RiskLevel = "low"
    required_information: list[str] = Field(default_factory=list)
    escalation_recommendation: bool = False
    rationale: str
    mixed_intent: bool = False
    secondary_intents: list[str] = Field(default_factory=list)
    out_of_scope: bool = False
    ambiguous: bool = False
    calibrated: bool = True


class ToolExecutionResult(BaseModel):
    tool_name: str
    success: bool
    operation: Literal["read", "write"]
    output: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    idempotency_key: str | None = None
    authorized: bool = True


class EvidenceRef(BaseModel):
    source_id: str
    title: str
    passage: str
    version: str = "1"


class SpecialistResult(BaseModel):
    specialist_id: str
    proposed_answer: str
    evidence: list[EvidenceRef] = Field(default_factory=list)
    tool_results: list[ToolExecutionResult] = Field(default_factory=list)
    uncertainty: float = Field(ge=0, le=1, default=0.3)
    needs_escalation: bool = False
    escalation_reason: str | None = None
    claimed_actions: list[str] = Field(default_factory=list)
    addresses_request: bool = True
    clarifying_question: str | None = None


class SupervisorDecision(BaseModel):
    outcome: SupervisorOutcome
    reason: str
    policy_gates: list[str] = Field(default_factory=list)
    approved_answer: str | None = None
    retry_instruction: str | None = None
    require_human: bool = False
