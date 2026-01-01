from pydantic import BaseModel, Field


class VersionSubmitRequest(BaseModel):
    change_request_id: str = Field(..., description="Change request to link")
