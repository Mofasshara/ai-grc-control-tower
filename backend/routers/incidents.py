from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models.ai_incident import AIIncident, IncidentStatus
from models.change_request import ChangeRequest, ChangeType
from models.ai_system import AISystem
from schemas.ai_incident import (
    AIIncidentCreate,
    AIIncidentInvestigation,
    AIIncidentResponse,
    CorrectiveActionLink,
)
from utils.audit import (
    AI_INCIDENT_INVESTIGATED,
    AI_INCIDENT_REPORTED,
    AI_INCIDENT_RESOLVED,
)
from security.auth import get_current_user
from security.roles import Role

router = APIRouter(prefix="/incidents", tags=["AI Incidents"])


@router.post("/ai-systems/{ai_system_id}/incidents", response_model=AIIncidentResponse)
def create_incident(
    ai_system_id: str,
    payload: AIIncidentCreate,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    system = db.query(AISystem).filter(AISystem.id == ai_system_id).first()
    if not system:
        raise HTTPException(status_code=404, detail="AI system not found")

    incident = AIIncident(
        ai_system_id=ai_system_id,
        incident_type=payload.incident_type,
        severity=payload.severity,
        impact_area=payload.impact_area,
        description=payload.description,
        detected_by=user.username,
        created_by=user.username,
        status=IncidentStatus.OPEN,
    )

    db.add(incident)
    db.commit()
    db.refresh(incident)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = AI_INCIDENT_REPORTED
    state["audit_entity_id"] = incident.id
    state["audit_entity_type"] = "AI_INCIDENT"
    state["audit_metadata"] = {
        "ai_system_id": ai_system_id,
        "incident_id": incident.id,
        "user": user.username,
    }

    return incident


@router.get("/", response_model=list[AIIncidentResponse])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(AIIncident).order_by(AIIncident.created_at.desc()).all()


@router.get("/{incident_id}", response_model=AIIncidentResponse)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(AIIncident).filter(AIIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post("/{incident_id}/investigate", response_model=AIIncidentResponse)
def investigate_incident(
    incident_id: str,
    payload: AIIncidentInvestigation,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if user.role not in (Role.COMPLIANCE, Role.AI_OWNER):
        raise HTTPException(status_code=403, detail="Not authorized")

    incident = db.query(AIIncident).filter(AIIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    # Ensure enum stored as its string value for DB enum compatibility.
    incident.root_cause_category = payload.root_cause_category.value
    incident.root_cause_description = payload.root_cause_description
    incident.status = IncidentStatus.UNDER_INVESTIGATION

    db.commit()
    db.refresh(incident)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = AI_INCIDENT_INVESTIGATED
    state["audit_entity_id"] = incident.id
    state["audit_entity_type"] = "AI_INCIDENT"
    state["audit_metadata"] = {
        "ai_system_id": incident.ai_system_id,
        "incident_id": incident.id,
        "user": user.username,
    }

    return incident


@router.post("/{incident_id}/corrective-action", response_model=AIIncidentResponse)
def link_corrective_action(
    incident_id: str,
    payload: CorrectiveActionLink,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    incident = db.query(AIIncident).filter(AIIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    change_request = (
        db.query(ChangeRequest)
        .filter(ChangeRequest.id == payload.change_request_id)
        .first()
    )
    if not change_request:
        raise HTTPException(status_code=404, detail="Change request not found")

    allowed_types = {
        ChangeType.PROMPT.value,
        ChangeType.RAG_SOURCE.value,
        ChangeType.CONFIG.value,
    }
    change_type_value = getattr(change_request.change_type, "value", change_request.change_type)
    if change_type_value not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail="Invalid change request type for corrective action",
        )

    incident.corrective_change_request_id = payload.change_request_id
    incident.status = IncidentStatus.RESOLVED

    db.commit()
    db.refresh(incident)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = AI_INCIDENT_RESOLVED
    state["audit_entity_id"] = incident.id
    state["audit_entity_type"] = "AI_INCIDENT"
    state["audit_metadata"] = {
        "ai_system_id": incident.ai_system_id,
        "incident_id": incident.id,
        "user": user.username,
    }

    return incident
