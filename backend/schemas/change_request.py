from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.models.change_request import ChangeStatus, ChangeType


class ChangeRequestCreate(BaseModel):
    change_type: ChangeType = Field(..., description="Type of change being requested")
    description: str = Field(..., description="Detailed description of the change")
    business_justification: str = Field(..., description="Why this change is needed")
    impact_assessment: str = Field(..., description="Impact on users, systems, and risk")
    rollback_plan: str = Field(..., description="How to revert if something goes wrong")
    requested_by: str = Field(..., description="User requesting the change")


class ChangeRequestResponse(BaseModel):
    id: str
    ai_system_id: str
    change_type: ChangeType
    description: str
    business_justification: str
    impact_assessment: str
    rollback_plan: str
    status: ChangeStatus
    requested_by: str
    approved_by: Optional[str]
    created_at: datetime
    approved_at: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
