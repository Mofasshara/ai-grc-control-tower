from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from models.rag_source import RAGSourceType
from models.rag_source_version import RAGSourceStatus


class RAGSourceCreate(BaseModel):
    name: str = Field(..., description="Unique RAG source name")
    description: str = Field(..., description="RAG source description")
    source_type: RAGSourceType = Field(..., description="RAG source type")


class RAGSourceResponse(BaseModel):
    id: str
    name: str
    description: str
    source_type: RAGSourceType
    created_at: datetime
    created_by: str

    model_config = ConfigDict(from_attributes=True)


class RAGSourceVersionCreate(BaseModel):
    uri: str = Field(..., description="Source URI")
    ingestion_config: dict = Field(..., description="Ingestion configuration")
    embedding_config: dict = Field(..., description="Embedding configuration")


class RAGSourceVersionResponse(BaseModel):
    id: str
    rag_source_id: str
    version: int
    status: RAGSourceStatus
    uri: str
    ingestion_config: dict
    embedding_config: dict
    content_hash: str
    diff_from_prev: Optional[str]
    change_request_id: Optional[str]
    created_at: datetime
    created_by: str

    model_config = ConfigDict(from_attributes=True)
