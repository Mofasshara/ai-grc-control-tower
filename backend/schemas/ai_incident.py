from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.ai_incident import (
    ImpactArea,
    IncidentSeverity,
    IncidentStatus,
    IncidentType,
    RootCauseCategory,
)


class AIIncidentCreate(BaseModel):
    incident_type: IncidentType = Field(..., description="Type of AI incident")
    severity: IncidentSeverity = Field(..., description="Severity level")
    impact_area: ImpactArea = Field(..., description="Impact area")
    description: str = Field(..., description="Detailed description of the incident")
    contains_personal_data: bool = Field(
        default=False,
        description="Whether this incident contains personal data subject to GDPR",
    )


class AIIncidentResponse(BaseModel):
    id: str
    ai_system_id: str
    corrective_change_request_id: str | None = None
    incident_type: IncidentType
    severity: IncidentSeverity
    impact_area: ImpactArea
    description: str
    contains_personal_data: bool
    detected_by: str
    detection_date: datetime
    status: IncidentStatus
    created_at: datetime
    created_by: str

    model_config = ConfigDict(from_attributes=True)


class AIIncidentInvestigation(BaseModel):
    root_cause_category: RootCauseCategory
    root_cause_description: str


class CorrectiveActionLink(BaseModel):
    change_request_id: str
