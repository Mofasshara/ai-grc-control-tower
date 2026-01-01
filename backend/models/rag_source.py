import enum
from datetime import datetime

from sqlalchemy import Column, DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID

from . import Base, generate_uuid


class RAGSourceType(str, enum.Enum):
    SHAREPOINT = "SharePoint"
    BLOB = "Blob"
    WEB = "Web"
    CONFLUENCE = "Confluence"
    FILE = "File"


class RAGSource(Base):
    __tablename__ = "rag_sources"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text, nullable=False)
    source_type = Column(
        Enum(
            RAGSourceType,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            create_type=False,
        ),
        nullable=False,
    )

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=False)
