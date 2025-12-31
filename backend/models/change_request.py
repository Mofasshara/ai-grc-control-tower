import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from . import Base, generate_uuid


class ChangeType(str, enum.Enum):
    MODEL = "model"
    PROMPT = "prompt"
    RAG_SOURCE = "rag_source"
    CONFIG = "config"


class ChangeStatus(str, enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    APPROVED = "approved"
    IMPLEMENTED = "implemented"
    REJECTED = "rejected"


class ChangeRequest(Base):
    __tablename__ = "change_requests"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)

    ai_system_id = Column(
        UUID(as_uuid=False),
        ForeignKey("ai_systems.id"),
        nullable=False,
    )

    change_type = Column(
        Enum(ChangeType, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        nullable=False,
    )

    description = Column(Text, nullable=False)
    business_justification = Column(Text, nullable=False)
    impact_assessment = Column(Text, nullable=False)
    rollback_plan = Column(Text, nullable=False)

    status = Column(
        Enum(ChangeStatus, values_callable=lambda enum_cls: [e.value for e in enum_cls]),
        default=ChangeStatus.DRAFT,
        nullable=False,
    )

    requested_by = Column(String, nullable=False)
    approved_by = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    approved_at = Column(DateTime, nullable=True)


ALLOWED_CHANGE_TRANSITIONS = {
    "draft": ["submitted"],
    "submitted": ["approved", "rejected"],
    "approved": ["implemented"],
    "rejected": [],
    "implemented": [],
}


def is_valid_transition(current: str, new: str) -> bool:
    return new in ALLOWED_CHANGE_TRANSITIONS[current]
