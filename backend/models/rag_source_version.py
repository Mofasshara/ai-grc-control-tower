import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.dialects.postgresql import UUID

from . import Base, generate_uuid


class RAGSourceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    ACTIVE = "ACTIVE"
    RETIRED = "RETIRED"


class RAGSourceVersion(Base):
    __tablename__ = "rag_source_versions"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)

    rag_source_id = Column(
        UUID(as_uuid=False),
        ForeignKey("rag_sources.id"),
        nullable=False,
    )

    version = Column(Integer, nullable=False)

    status = Column(Enum(RAGSourceStatus, create_type=False), default=RAGSourceStatus.DRAFT, nullable=False)

    uri = Column(Text, nullable=False)

    ingestion_config = Column(JSON, nullable=False)
    embedding_config = Column(JSON, nullable=False)

    content_hash = Column(String, nullable=False)

    diff_from_prev = Column(Text, nullable=True)

    change_request_id = Column(
        UUID(as_uuid=False),
        ForeignKey("change_requests.id"),
        nullable=True,
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=False)
