from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models.ai_system import AISystem
from models.change_request import ChangeRequest, ChangeStatus
from schemas.change_request import ChangeRequestCreate, ChangeRequestResponse
from security.auth import require_roles
from security.roles import Role

router = APIRouter(tags=["Change Requests"])


@router.post(
    "/ai-systems/{system_id}/changes",
    response_model=ChangeRequestResponse,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AI_OWNER))],
)
def create_change_request(
    system_id: str,
    payload: ChangeRequestCreate,
    request: Request,
    db: Session = Depends(get_db),
):
    ai_system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not ai_system:
        raise HTTPException(status_code=404, detail="AI system not found")

    change = ChangeRequest(
        ai_system_id=system_id,
        change_type=payload.change_type,
        description=payload.description,
        business_justification=payload.business_justification,
        impact_assessment=payload.impact_assessment,
        rollback_plan=payload.rollback_plan,
        status=ChangeStatus.DRAFT,
        requested_by=payload.requested_by,
    )

    db.add(change)
    db.commit()
    db.refresh(change)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "CHANGE_REQUEST_CREATED"
    state["audit_entity_id"] = change.id
    state["audit_entity_type"] = "CHANGE_REQUEST"

    return change


@router.get("/changes", response_model=list[ChangeRequestResponse])
def list_change_requests(db: Session = Depends(get_db)):
    changes = db.query(ChangeRequest).all()
    return changes


@router.get("/changes/{change_id}", response_model=ChangeRequestResponse)
def get_change_request(change_id: str, db: Session = Depends(get_db)):
    change = db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Change request not found")
    return change
