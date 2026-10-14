import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def new_id(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    allowed_domains: Mapped[list] = mapped_column(JSON, default=list)
    retention_days: Mapped[int] = mapped_column(default=365)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ApiUser(Base):
    __tablename__ = "api_users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("usr"))
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    role: Mapped[str] = mapped_column(String(32))
    display_name: Mapped[str] = mapped_column(String(200))
    api_key_hash: Mapped[str] = mapped_column(String(128), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Conversation(Base):
    __tablename__ = "conversations"
    __table_args__ = (Index("ix_conv_tenant_created", "tenant_id", "created_at"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("conv"))
    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id"), index=True)
    customer_user_id: Mapped[str] = mapped_column(String(64), index=True)
    customer_external_id: Mapped[str | None] = mapped_column(String(128), nullable=True)
    domain: Mapped[str | None] = mapped_column(String(64), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="open")
    channel: Mapped[str] = mapped_column(String(32), default="api")
    case_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    messages: Mapped[list["Message"]] = relationship(back_populates="conversation", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("msg"))
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), index=True)
    role: Mapped[str] = mapped_column(String(32))
    content: Mapped[str] = mapped_column(Text)
    classification_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    specialist_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    supervisor_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    case_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    conversation: Mapped[Conversation] = relationship(back_populates="messages")


class SupportCase(Base):
    __tablename__ = "support_cases"
    __table_args__ = (Index("ix_case_tenant_status", "tenant_id", "status"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("case"))
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    domain: Mapped[str] = mapped_column(String(64))
    conversation_id: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(32), default="OPEN")
    customer_request: Mapped[str] = mapped_column(Text)
    classification_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    specialist_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    evidence_json: Mapped[list] = mapped_column(JSON, default=list)
    tool_results_json: Mapped[list] = mapped_column(JSON, default=list)
    escalation_reason: Mapped[str] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(String(32))
    urgency: Mapped[str] = mapped_column(String(32))
    draft_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    assigned_to: Mapped[str | None] = mapped_column(String(64), nullable=True)
    sla_due_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    history_json: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("aud"))
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    conversation_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    case_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    event_type: Mapped[str] = mapped_column(String(64), index=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"
    __table_args__ = (UniqueConstraint("tenant_id", "domain", "source_id", "version"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("doc"))
    tenant_id: Mapped[str] = mapped_column(String(64), index=True)
    domain: Mapped[str] = mapped_column(String(64), index=True)
    source_id: Mapped[str] = mapped_column(String(128))
    title: Mapped[str] = mapped_column(String(300))
    content: Mapped[str] = mapped_column(Text)
    version: Mapped[str] = mapped_column(String(32), default="1")
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class IdempotencyRecord(Base):
    __tablename__ = "idempotency_records"
    __table_args__ = (UniqueConstraint("tenant_id", "key"),)

    id: Mapped[str] = mapped_column(String(64), primary_key=True, default=lambda: new_id("idp"))
    tenant_id: Mapped[str] = mapped_column(String(64))
    key: Mapped[str] = mapped_column(String(200))
    result_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
