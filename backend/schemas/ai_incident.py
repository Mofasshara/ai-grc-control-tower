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
    triage_suggested_severity: str | None = None
    triage_suggested_owner_role: str | None = None
    triage_suggested_root_cause_category: str | None = None
    triage_suggestion_reason: str | None = None
    triage_status: str | None = None
    triage_confirmed_by: str | None = None
    triage_confirmed_at: datetime | None = None
    triage_override_reason: str | None = None
    assigned_to_role: str | None = None
    assigned_to_user: str | None = None
    assigned_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class AIIncidentInvestigation(BaseModel):
    root_cause_category: RootCauseCategory
    root_cause_description: str


class TriageConfirmRequest(BaseModel):
    confirmed_severity: IncidentSeverity
    confirmed_owner_role: str
    confirmed_root_cause_category: RootCauseCategory
    override_reason: str | None = None


class CorrectiveActionLink(BaseModel):
    change_request_id: str
