import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID

from . import Base, generate_uuid


class PromptStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)

    prompt_template_id = Column(
        UUID(as_uuid=False),
        ForeignKey("prompt_templates.id"),
        nullable=False,
    )

    version = Column(Integer, nullable=False)

    status = Column(Enum(PromptStatus), default=PromptStatus.DRAFT, nullable=False)

    prompt_text = Column(Text, nullable=False)

    parameters_schema = Column(JSON, nullable=True)

    content_hash = Column(String, nullable=False)

    diff_from_prev = Column(Text, nullable=True)

    change_request_id = Column(
        UUID(as_uuid=False),
        ForeignKey("change_requests.id"),
        nullable=True,
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=False)
