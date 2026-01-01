from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from schemas.ai_system import AISystemCreate, AISystemResponse
from schemas.lifecycle import LifecycleUpdate
from models.ai_system import AISystem, ALLOWED_TRANSITIONS
from models.change_request import ChangeRequest
from models.ai_system_prompt_binding import AISystemPromptBinding
from models.ai_system_rag_binding import AISystemRAGBinding
from models.prompt_version import PromptVersion, PromptStatus
from models.rag_source_version import RAGSourceVersion, RAGSourceStatus
from schemas.activation import PromptActivationRequest, RAGActivationRequest
from database import get_db
from security.auth import get_current_user, require_roles
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


@router.post(
    "/{system_id}/prompts/activate",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AI_OWNER, Role.COMPLIANCE))],
)
def activate_prompt_version(
    system_id: str,
    payload: PromptActivationRequest,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ai_system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not ai_system:
        raise HTTPException(status_code=404, detail="AI system not found")

    risk_value = getattr(ai_system.risk_classification, "value", ai_system.risk_classification)
    if risk_value == "high" and user.role not in (Role.COMPLIANCE, Role.ADMIN):
        raise HTTPException(
            status_code=403,
            detail="Only Compliance or Admin can activate prompts for high-risk systems",
        )

    version = db.query(PromptVersion).filter(PromptVersion.id == payload.prompt_version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Prompt version not found")

    change_request = (
        db.query(ChangeRequest)
        .filter(ChangeRequest.id == payload.change_request_id)
        .first()
    )
    if not change_request:
        raise HTTPException(status_code=404, detail="Change request not found")

    change_status = getattr(change_request.status, "value", change_request.status)
    if change_status != "approved":
        raise HTTPException(
            status_code=400,
            detail="Change request must be APPROVED before activation",
        )

    if str(version.change_request_id) != payload.change_request_id:
        raise HTTPException(
            status_code=400,
            detail="Prompt version not linked to this change request",
        )

    if getattr(version.status, "value", version.status) != PromptStatus.SUBMITTED.value:
        raise HTTPException(status_code=400, detail="Prompt version must be SUBMITTED")

    db.query(AISystemPromptBinding).filter(
        AISystemPromptBinding.ai_system_id == system_id,
        AISystemPromptBinding.active_to.is_(None),
    ).update({"active_to": datetime.utcnow()})

    binding = AISystemPromptBinding(
        ai_system_id=system_id,
        prompt_version_id=payload.prompt_version_id,
        active_from=datetime.utcnow(),
        active_to=None,
        activated_by=user.username,
        change_request_id=payload.change_request_id,
    )
    db.add(binding)

    version.status = PromptStatus.ACTIVE

    db.commit()

    state = request.scope.setdefault("state", {})
    state["audit_action"] = (
        f"PROMPT_VERSION_ACTIVATED ai_system_id={system_id} "
        f"change_request_id={payload.change_request_id}"
    )
    state["audit_entity_id"] = payload.prompt_version_id
    state["audit_entity_type"] = "PROMPT_VERSION"

    return {
        "ai_system_id": system_id,
        "prompt_version_id": payload.prompt_version_id,
        "change_request_id": payload.change_request_id,
        "activated_by": user.username,
    }


@router.post(
    "/{system_id}/rag/activate",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AI_OWNER, Role.COMPLIANCE))],
)
def activate_rag_version(
    system_id: str,
    payload: RAGActivationRequest,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    ai_system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not ai_system:
        raise HTTPException(status_code=404, detail="AI system not found")

    risk_value = getattr(ai_system.risk_classification, "value", ai_system.risk_classification)
    if risk_value == "high" and user.role not in (Role.COMPLIANCE, Role.ADMIN):
        raise HTTPException(
            status_code=403,
            detail="Only Compliance or Admin can activate RAG for high-risk systems",
        )

    version = db.query(RAGSourceVersion).filter(RAGSourceVersion.id == payload.rag_source_version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="RAG source version not found")

    change_request = (
        db.query(ChangeRequest)
        .filter(ChangeRequest.id == payload.change_request_id)
        .first()
    )
    if not change_request:
        raise HTTPException(status_code=404, detail="Change request not found")

    change_status = getattr(change_request.status, "value", change_request.status)
    if change_status != "approved":
        raise HTTPException(
            status_code=400,
            detail="Change request must be APPROVED before activation",
        )

    if str(version.change_request_id) != payload.change_request_id:
        raise HTTPException(
            status_code=400,
            detail="RAG version not linked to this change request",
        )

    if getattr(version.status, "value", version.status) != RAGSourceStatus.SUBMITTED.value:
        raise HTTPException(status_code=400, detail="RAG version must be SUBMITTED")

    db.query(AISystemRAGBinding).filter(
        AISystemRAGBinding.ai_system_id == system_id,
        AISystemRAGBinding.active_to.is_(None),
    ).update({"active_to": datetime.utcnow()})

    binding = AISystemRAGBinding(
        ai_system_id=system_id,
        rag_source_version_id=payload.rag_source_version_id,
        active_from=datetime.utcnow(),
        active_to=None,
        activated_by=user.username,
        change_request_id=payload.change_request_id,
    )
    db.add(binding)

    version.status = RAGSourceStatus.ACTIVE

    db.commit()

    state = request.scope.setdefault("state", {})
    state["audit_action"] = (
        f"RAG_VERSION_ACTIVATED ai_system_id={system_id} "
        f"change_request_id={payload.change_request_id}"
    )
    state["audit_entity_id"] = payload.rag_source_version_id
    state["audit_entity_type"] = "RAG_SOURCE_VERSION"

    return {
        "ai_system_id": system_id,
        "rag_source_version_id": payload.rag_source_version_id,
        "change_request_id": payload.change_request_id,
        "activated_by": user.username,
    }


@router.patch(
    "/{system_id}/lifecycle",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AI_OWNER, Role.COMPLIANCE))],
)
def update_lifecycle_state(
    system_id: str,
    payload: LifecycleUpdate,
    request: Request,
    db: Session = Depends(get_db),
):
    system = db.query(AISystem).filter(AISystem.id == system_id).first()
    if not system:
        raise HTTPException(status_code=404, detail="AI system not found")

    current_value = getattr(system.lifecycle_status, "value", system.lifecycle_status)
    new_value = payload.new_state.value

    if new_value not in ALLOWED_TRANSITIONS[current_value]:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid transition: {current_value} -> {new_value}",
        )

    if current_value == "submitted" and new_value == "approved":
        state = request.scope.get("state", {})
        user = state.get("user")
        if not user or user.role != Role.COMPLIANCE:
            raise HTTPException(
                status_code=403,
                detail="Only Compliance can approve submitted systems",
            )

    system.lifecycle_status = new_value
    db.commit()
    db.refresh(system)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "LIFECYCLE_STATE_CHANGED"
    state["audit_entity_id"] = system.id
    state["audit_entity_type"] = "AI_SYSTEM"
    state["audit_previous_state"] = current_value
    state["audit_new_state"] = new_value

    return {"id": system.id, "old_state": current_value, "new_state": new_value}
