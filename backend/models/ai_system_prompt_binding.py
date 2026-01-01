from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from . import Base, generate_uuid


class AISystemPromptBinding(Base):
    __tablename__ = "ai_system_prompt_bindings"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)

    ai_system_id = Column(UUID(as_uuid=False), ForeignKey("ai_systems.id"), nullable=False)
    prompt_version_id = Column(UUID(as_uuid=False), ForeignKey("prompt_versions.id"), nullable=False)

    active_from = Column(DateTime, default=datetime.utcnow, nullable=False)
    active_to = Column(DateTime, nullable=True)

    activated_by = Column(String, nullable=False)
    change_request_id = Column(UUID(as_uuid=False), ForeignKey("change_requests.id"), nullable=False)
