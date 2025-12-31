from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class RiskClassification(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class LifecycleStatus(str, Enum):
    draft = "draft"
    submitted = "submitted"
    approved = "approved"
    active = "active"
    deprecated = "deprecated"
    retired = "retired"


class AISystemCreate(BaseModel):
    name: str = Field(..., description="Unique name of the AI system")
    business_purpose: str = Field(..., description="Why this AI system exists")
    intended_users: str = Field(..., description="Who will use this system")
    risk_classification: RiskClassification = Field(..., description="Risk level")
    owner: str = Field(..., description="Accountable owner")
    created_by: str = Field(..., description="User creating this record")


class AISystemResponse(BaseModel):
    id: str
    name: str
    business_purpose: str
    intended_users: str
    risk_classification: RiskClassification
    owner: str
    lifecycle_status: LifecycleStatus
    created_at: datetime
    created_by: str

    model_config = ConfigDict(from_attributes=True)
