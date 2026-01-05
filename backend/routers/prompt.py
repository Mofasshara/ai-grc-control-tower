import hashlib
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models.prompt_template import PromptTemplate
from models.prompt_version import PromptStatus, PromptVersion
from models.change_request import ChangeRequest
from schemas.prompt import (
    PromptTemplateCreate,
    PromptTemplateResponse,
    PromptVersionCreate,
    PromptVersionResponse,
)
from security.auth import get_current_user, require_not_auditor, require_roles
from security.roles import Role
from schemas.submit import VersionSubmitRequest
from utils.diff import generate_unified_diff

router = APIRouter(prefix="/prompts", tags=["Prompt Governance"])


@router.post(
    "/templates",
    response_model=PromptTemplateResponse,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AI_OWNER)), Depends(require_not_auditor)],
)
def create_prompt_template(
    payload: PromptTemplateCreate,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    template = PromptTemplate(
        name=payload.name,
        description=payload.description,
        created_by=user.username,
    )

    db.add(template)
    db.commit()
    db.refresh(template)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "PROMPT_TEMPLATE_CREATED"
    state["audit_entity_id"] = template.id
    state["audit_entity_type"] = "PROMPT_TEMPLATE"

    return template


@router.get("/templates", response_model=list[PromptTemplateResponse])
def list_prompt_templates(db: Session = Depends(get_db)):
    return db.query(PromptTemplate).all()


@router.get("/templates/{template_id}", response_model=PromptTemplateResponse)
def get_prompt_template(template_id: str, db: Session = Depends(get_db)):
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")
    return template


@router.post(
    "/templates/{template_id}/versions",
    response_model=PromptVersionResponse,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AI_OWNER)), Depends(require_not_auditor)],
)
def create_prompt_version(
    template_id: str,
    payload: PromptVersionCreate,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    template = db.query(PromptTemplate).filter(PromptTemplate.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Prompt template not found")

    prev_version = (
        db.query(PromptVersion)
        .filter(PromptVersion.prompt_template_id == template_id)
        .order_by(PromptVersion.version.desc())
        .first()
    )

    new_version_number = 1 if not prev_version else prev_version.version + 1

    diff = generate_unified_diff(
        prev_version.prompt_text if prev_version else None,
        payload.prompt_text,
    )

    hash_input = payload.prompt_text + str(payload.parameters_schema or "")
    content_hash = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()

    version = PromptVersion(
        prompt_template_id=template_id,
        version=new_version_number,
        status=PromptStatus.DRAFT,
        prompt_text=payload.prompt_text,
        parameters_schema=payload.parameters_schema,
        diff_from_prev=diff,
        content_hash=content_hash,
        created_by=user.username,
    )

    db.add(version)
    db.commit()
    db.refresh(version)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "PROMPT_VERSION_CREATED"
    state["audit_entity_id"] = version.id
    state["audit_entity_type"] = "PROMPT_VERSION"

    return version


@router.get("/templates/{template_id}/versions", response_model=list[PromptVersionResponse])
def list_prompt_versions(template_id: str, db: Session = Depends(get_db)):
    return (
        db.query(PromptVersion)
        .filter(PromptVersion.prompt_template_id == template_id)
        .order_by(PromptVersion.version.asc())
        .all()
    )


@router.get("/versions/{version_id}", response_model=PromptVersionResponse)
def get_prompt_version(version_id: str, request: Request, db: Session = Depends(get_db)):
    version = db.query(PromptVersion).filter(PromptVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Prompt version not found")

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "PROMPT_VERSION_VIEWED"
    state["audit_entity_id"] = version.id
    state["audit_entity_type"] = "PROMPT_VERSION"

    return version


@router.get("/versions/{version_id}/diff")
def get_prompt_diff(version_id: str, db: Session = Depends(get_db)):
    version = db.query(PromptVersion).filter(PromptVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="Prompt version not found")

    return {"diff": version.diff_from_prev}


@router.post(
    "/versions/{version_id}/submit",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AI_OWNER)), Depends(require_not_auditor)],
)
def submit_prompt_version(
    version_id: str,
    payload: VersionSubmitRequest,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    version = db.query(PromptVersion).filter(PromptVersion.id == version_id).first()
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
    if change_status != "submitted":
        raise HTTPException(
            status_code=400,
            detail="Change request must be SUBMITTED before linking",
        )

    if version.change_request_id and str(version.change_request_id) != payload.change_request_id:
        raise HTTPException(status_code=400, detail="Prompt version already linked")

    version.change_request_id = change_request.id
    version.status = PromptStatus.SUBMITTED

    db.commit()
    db.refresh(version)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "PROMPT_VERSION_SUBMITTED"
    state["audit_entity_id"] = version.id
    state["audit_entity_type"] = "PROMPT_VERSION"

    return {
        "id": version.id,
        "status": getattr(version.status, "value", version.status),
        "change_request_id": version.change_request_id,
        "submitted_by": user.username,
    }
