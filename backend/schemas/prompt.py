from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from models.prompt_version import PromptStatus


class PromptTemplateCreate(BaseModel):
    name: str = Field(..., description="Unique prompt template name")
    description: str = Field(..., description="Prompt template purpose")


class PromptTemplateResponse(BaseModel):
    id: str
    name: str
    description: str
    created_at: datetime
    created_by: str

    model_config = ConfigDict(from_attributes=True)


class PromptVersionCreate(BaseModel):
    prompt_text: str = Field(..., description="Prompt text for this version")
    parameters_schema: Optional[dict] = Field(
        None,
        description="Optional schema for prompt parameters",
    )


class PromptVersionResponse(BaseModel):
    id: str
    prompt_template_id: str
    version: int
    status: PromptStatus
    prompt_text: str
    parameters_schema: Optional[dict]
    content_hash: str
    diff_from_prev: Optional[str]
    change_request_id: Optional[str]
    created_at: datetime
    created_by: str

    model_config = ConfigDict(from_attributes=True)
