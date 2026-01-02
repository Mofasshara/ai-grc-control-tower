from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models.ai_incident import AIIncident, IncidentStatus
from models.ai_system import AISystem
from schemas.ai_incident import AIIncidentCreate, AIIncidentResponse
from security.auth import get_current_user

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
    state["audit_action"] = "AI_INCIDENT_REPORTED"
    state["audit_entity_id"] = incident.id
    state["audit_entity_type"] = "AI_INCIDENT"

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
