from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from models.ai_incident import ImpactArea, IncidentSeverity, IncidentStatus, IncidentType


class AIIncidentCreate(BaseModel):
    incident_type: IncidentType = Field(..., description="Type of AI incident")
    severity: IncidentSeverity = Field(..., description="Severity level")
    impact_area: ImpactArea = Field(..., description="Impact area")
    description: str = Field(..., description="Detailed description of the incident")


class AIIncidentResponse(BaseModel):
    id: str
    ai_system_id: str
    incident_type: IncidentType
    severity: IncidentSeverity
    impact_area: ImpactArea
    description: str
    detected_by: str
    detection_date: datetime
    status: IncidentStatus
    created_at: datetime
    created_by: str

    model_config = ConfigDict(from_attributes=True)
