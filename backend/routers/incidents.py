from datetime import datetime

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
    TriageConfirmRequest,
)
from utils.audit import (
    AI_INCIDENT_ASSIGNED,
    AI_INCIDENT_INVESTIGATED,
    AI_INCIDENT_REPORTED,
    AI_INCIDENT_RESOLVED,
    AI_INCIDENT_TRIAGE_SUGGESTED,
    AI_INCIDENT_TRIAGE_CONFIRMED,
)
from services.incident_triage_service import IncidentTriageService
from security.auth import get_current_user, require_not_auditor
from security.roles import Role

router = APIRouter(prefix="/incidents", tags=["AI Incidents"])


@router.post(
    "/ai-systems/{ai_system_id}/incidents",
    response_model=AIIncidentResponse,
    dependencies=[Depends(require_not_auditor)],
)
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
        contains_personal_data=payload.contains_personal_data,
        detected_by=user.username,
        created_by=user.username,
        status=IncidentStatus.OPEN,
    )

    triage_service = IncidentTriageService(db)
    suggestion = triage_service.suggest(incident)
    incident.triage_suggested_severity = suggestion["severity"]
    incident.triage_suggested_owner_role = suggestion["owner_role"]
    incident.triage_suggested_root_cause_category = suggestion["root_cause"]
    root_cause_explanation = suggestion.get("root_cause_explanation")
    if root_cause_explanation:
        incident.triage_suggestion_reason = (
            f"{suggestion['reason']} | RCA: {root_cause_explanation}"
        )
    else:
        incident.triage_suggestion_reason = suggestion["reason"]
    incident.triage_status = "SUGGESTED"

    incident.assigned_to_role = suggestion["owner_role"]
    incident.assigned_at = datetime.utcnow()
    risk_value = getattr(system.risk_classification, "value", system.risk_classification)
    if risk_value in ("high", "critical"):
        incident.assigned_to_role = "COMPLIANCE"
        incident.triage_suggestion_reason = (
            f"{incident.triage_suggestion_reason} | Auto-escalated due to high-risk system"
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
        "triage_action": AI_INCIDENT_TRIAGE_SUGGESTED,
        "triage_suggestion": suggestion,
        "assignment_action": AI_INCIDENT_ASSIGNED,
        "assigned_to_role": incident.assigned_to_role,
        "assigned_to_user": incident.assigned_to_user,
        "assigned_at": incident.assigned_at.isoformat() if incident.assigned_at else None,
    }

    return incident


@router.post(
    "/{incident_id}/triage/confirm",
    response_model=AIIncidentResponse,
    dependencies=[Depends(require_not_auditor)],
)
def confirm_triage(
    incident_id: str,
    payload: TriageConfirmRequest,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    incident = db.query(AIIncident).filter(AIIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    if not any(role in user.mapped_roles for role in (Role.COMPLIANCE, Role.AI_OWNER)):
        raise HTTPException(status_code=403, detail="Not authorized")

    override = False
    if (
        incident.triage_suggested_severity
        and payload.confirmed_severity.value != incident.triage_suggested_severity
    ):
        override = True
    if (
        incident.triage_suggested_owner_role
        and payload.confirmed_owner_role != incident.triage_suggested_owner_role
    ):
        override = True
    if (
        incident.triage_suggested_root_cause_category
        and payload.confirmed_root_cause_category.value
        != incident.triage_suggested_root_cause_category
    ):
        override = True

    if override and not payload.override_reason:
        raise HTTPException(
            status_code=400,
            detail="Override reason required when changing triage suggestion.",
        )

    incident.triage_status = "OVERRIDDEN" if override else "CONFIRMED"
    incident.triage_confirmed_by = user.username
    incident.triage_confirmed_at = datetime.utcnow()
    incident.triage_override_reason = payload.override_reason

    incident.severity = payload.confirmed_severity
    incident.root_cause_category = payload.confirmed_root_cause_category.value

    db.commit()
    db.refresh(incident)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = AI_INCIDENT_TRIAGE_CONFIRMED
    state["audit_entity_id"] = incident.id
    state["audit_entity_type"] = "AI_INCIDENT"
    state["audit_metadata"] = {
        "incident_id": incident.id,
        "confirmed_severity": payload.confirmed_severity.value,
        "confirmed_owner_role": payload.confirmed_owner_role,
        "confirmed_root_cause_category": payload.confirmed_root_cause_category.value,
        "override": override,
        "override_reason": payload.override_reason,
    }

    return incident

@router.get("/", response_model=list[AIIncidentResponse])
def list_incidents(db: Session = Depends(get_db)):
    return db.query(AIIncident).order_by(AIIncident.created_at.desc()).all()


@router.get("/queue", response_model=list[AIIncidentResponse])
def get_queue(role: str, db: Session = Depends(get_db)):
    role_value = role.upper()
    if role_value not in {"AI_OWNER", "COMPLIANCE"}:
        raise HTTPException(status_code=400, detail="Invalid role. Use ai_owner or compliance.")
    return (
        db.query(AIIncident)
        .filter(AIIncident.assigned_to_role == role_value)
        .order_by(AIIncident.created_at.desc())
        .all()
    )


@router.get("/{incident_id}", response_model=AIIncidentResponse)
def get_incident(incident_id: str, db: Session = Depends(get_db)):
    incident = db.query(AIIncident).filter(AIIncident.id == incident_id).first()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.post(
    "/{incident_id}/investigate",
    response_model=AIIncidentResponse,
    dependencies=[Depends(require_not_auditor)],
)
def investigate_incident(
    incident_id: str,
    payload: AIIncidentInvestigation,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    if not any(role in user.mapped_roles for role in (Role.COMPLIANCE, Role.AI_OWNER)):
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


@router.post(
    "/{incident_id}/corrective-action",
    response_model=AIIncidentResponse,
    dependencies=[Depends(require_not_auditor)],
)
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
