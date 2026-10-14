from typing import Any

from pydantic import BaseModel, Field


class DomainConfig(BaseModel):
    id: str
    name: str
    description: str
    intents: list[str]
    specialists: list[str]
    system_prompt: str
    response_policy: str
    knowledge_sources: list[str] = Field(default_factory=list)
    permitted_tools: list[str]
    risk_classifications: dict[str, str] = Field(default_factory=dict)
    routing_threshold: float = 0.62
    resolution_threshold: float = 0.72
    mandatory_human_review: list[str] = Field(default_factory=list)
    data_retention_days: int = 365
    privacy: dict[str, Any] = Field(default_factory=dict)
    escalation_conditions: list[str] = Field(default_factory=list)
    high_impact: bool = False
    healthcare_admin_only: bool = False
    clinical_diagnosis_forbidden: bool = False
    write_confirmation_required: list[str] = Field(default_factory=list)
    evaluation_cases: list[dict[str, Any]] = Field(default_factory=list)
    keywords: dict[str, list[str]] = Field(default_factory=dict)
    out_of_scope_topics: list[str] = Field(default_factory=list)
