from pydantic import BaseModel, Field


class PromptActivationRequest(BaseModel):
    prompt_version_id: str = Field(..., description="Prompt version to activate")
    change_request_id: str = Field(..., description="Approved change request")


class RAGActivationRequest(BaseModel):
    rag_source_version_id: str = Field(..., description="RAG source version to activate")
    change_request_id: str = Field(..., description="Approved change request")
