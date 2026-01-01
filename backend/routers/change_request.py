from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models.ai_system import AISystem
from models.change_request import ChangeRequest, ChangeStatus, is_valid_transition
from schemas.change_request import ChangeRequestCreate, ChangeRequestResponse
from security.auth import get_current_user, require_roles
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


@router.post(
    "/changes/{change_id}/approve",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.COMPLIANCE))],
)
def approve_change_request(
    change_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    change = db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Change request not found")

    current_value = getattr(change.status, "value", change.status)
    new_value = ChangeStatus.APPROVED.value

    if not is_valid_transition(current_value, new_value):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: {current_value} -> {new_value}",
        )

    if current_value == "submitted" and user.role != Role.COMPLIANCE:
        raise HTTPException(
            status_code=403,
            detail="Only Compliance can approve submitted changes",
        )

    change.status = ChangeStatus.APPROVED
    change.approved_by = user.username
    change.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(change)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "CHANGE_REQUEST_APPROVED"
    state["audit_entity_id"] = change.id
    state["audit_entity_type"] = "CHANGE_REQUEST"
    state["audit_previous_state"] = current_value
    state["audit_new_state"] = new_value

    return {
        "id": change.id,
        "old_status": current_value,
        "new_status": new_value,
        "approved_by": user.username,
        "approved_at": change.approved_at,
    }


@router.post(
    "/changes/{change_id}/reject",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.COMPLIANCE))],
)
def reject_change_request(
    change_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    change = db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Change request not found")

    current_value = getattr(change.status, "value", change.status)
    new_value = ChangeStatus.REJECTED.value

    if not is_valid_transition(current_value, new_value):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: {current_value} -> {new_value}",
        )

    change.status = ChangeStatus.REJECTED
    change.approved_by = user.username
    change.approved_at = datetime.utcnow()

    db.commit()
    db.refresh(change)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "CHANGE_REQUEST_REJECTED"
    state["audit_entity_id"] = change.id
    state["audit_entity_type"] = "CHANGE_REQUEST"
    state["audit_previous_state"] = current_value
    state["audit_new_state"] = new_value

    return {
        "id": change.id,
        "old_status": current_value,
        "new_status": new_value,
        "rejected_by": user.username,
        "rejected_at": change.approved_at,
    }


@router.post(
    "/changes/{change_id}/submit",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AI_OWNER))],
)
def submit_change_request(
    change_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    change = db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Change request not found")

    current_value = getattr(change.status, "value", change.status)
    new_value = ChangeStatus.SUBMITTED.value

    if not is_valid_transition(current_value, new_value):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: {current_value} -> {new_value}",
        )

    change.status = ChangeStatus.SUBMITTED
    change.approved_by = None
    change.approved_at = None

    db.commit()
    db.refresh(change)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "CHANGE_REQUEST_SUBMITTED"
    state["audit_entity_id"] = change.id
    state["audit_entity_type"] = "CHANGE_REQUEST"
    state["audit_previous_state"] = current_value
    state["audit_new_state"] = new_value

    return {
        "id": change.id,
        "old_status": current_value,
        "new_status": new_value,
        "submitted_by": user.username,
    }


@router.post(
    "/changes/{change_id}/implement",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AI_OWNER))],
)
def implement_change_request(
    change_id: str,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    change = db.query(ChangeRequest).filter(ChangeRequest.id == change_id).first()
    if not change:
        raise HTTPException(status_code=404, detail="Change request not found")

    current_value = getattr(change.status, "value", change.status)
    new_value = ChangeStatus.IMPLEMENTED.value

    if current_value != ChangeStatus.APPROVED.value:
        raise HTTPException(
            status_code=400,
            detail="Change cannot be implemented unless status = APPROVED",
        )

    change.status = ChangeStatus.IMPLEMENTED
    change.approved_by = user.username
    change.approved_at = datetime.utcnow()
    ai_system.last_changed_at = datetime.utcnow()
    ai_system.last_change_request_id = change.id

    db.commit()
    db.refresh(change)
    db.refresh(ai_system)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "CHANGE_REQUEST_IMPLEMENTED"
    state["audit_entity_id"] = change.id
    state["audit_entity_type"] = "CHANGE_REQUEST"
    state["audit_previous_state"] = current_value
    state["audit_new_state"] = new_value

    return {
        "change_id": change.id,
        "ai_system_id": ai_system.id,
        "old_status": current_value,
        "new_status": new_value,
        "implemented_by": user.username,
        "implemented_at": change.approved_at,
        "last_changed_at": ai_system.last_changed_at,
    }
