import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


def generate_uuid() -> str:
    return str(uuid.uuid4())


class TraceableMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
    purpose: Mapped[str] = mapped_column(Text, nullable=False)


class Approval(TraceableMixin, Base):
    __tablename__ = "approvals"

    change_request_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    notes: Mapped[str] = mapped_column(Text, nullable=True)


class Incident(TraceableMixin, Base):
    __tablename__ = "incidents"

    ai_system_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    incident_type: Mapped[str] = mapped_column(String(100), nullable=False)
    details: Mapped[str] = mapped_column(Text, nullable=False)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    entity_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payload_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    state_hash: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)


from .ai_system import AISystem, LifecycleStatus, RiskClassification  # noqa: E402
from .change_request import ChangeRequest, ChangeStatus, ChangeType  # noqa: E402
from .prompt_template import PromptTemplate  # noqa: E402
from .prompt_version import PromptStatus, PromptVersion  # noqa: E402
