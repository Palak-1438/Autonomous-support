from typing import Any, Generic, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class ErrorResponse(BaseModel):
    error: str
    detail: str | None = None
    request_id: str | None = None


class HealthResponse(BaseModel):
    status: str
    llm_mode: str
    database: str
    domains: int


class Paginated(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int


class DomainSummary(BaseModel):
    id: str
    name: str
    description: str
    intents: list[str]
    specialists: list[str]


class AgentSummary(BaseModel):
    id: str
    name: str
    description: str
    permitted_intents: list[str]


class MetricsResponse(BaseModel):
    conversations: int
    cases_open: int
    escalations: int
    tool_failures: int
    routing_events: int
    extra: dict[str, Any] = Field(default_factory=dict)
