from datetime import datetime

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.dialects.postgresql import UUID

from . import Base, generate_uuid


class PromptTemplate(Base):
    __tablename__ = "prompt_templates"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=False)
