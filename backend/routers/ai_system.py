from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from schemas.ai_system import AISystemCreate, AISystemResponse
from models.ai_system import AISystem
from database import get_db
from security.auth import require_roles
from security.roles import Role

router = APIRouter(prefix="/ai-systems", tags=["AI Systems"])


@router.post(
    "/",
    response_model=AISystemResponse,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AI_OWNER))],
)
def create_ai_system(payload: AISystemCreate, request: Request, db: Session = Depends(get_db)):
    existing = db.query(AISystem).filter(AISystem.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="AI system name must be unique")

    new_system = AISystem(
        name=payload.name,
        business_purpose=payload.business_purpose,
        intended_users=payload.intended_users,
        risk_classification=payload.risk_classification,
        owner=payload.owner,
        lifecycle_status="draft",
        created_by=payload.created_by,
    )

    db.add(new_system)
    db.commit()
    db.refresh(new_system)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "AI_SYSTEM_CREATED"
    state["audit_entity_id"] = new_system.id

    return new_system


@router.get("/", response_model=list[AISystemResponse])
def list_ai_systems(db: Session = Depends(get_db)):
    systems = db.query(AISystem).all()
    return systems


@router.get("/{system_id}", response_model=AISystemResponse)
def get_ai_system(system_id: str, request: Request, db: Session = Depends(get_db)):
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not system:
        raise HTTPException(status_code=404, detail="AI system not found")

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "AI_SYSTEM_VIEWED"
    state["audit_entity_id"] = system.id

    return system
