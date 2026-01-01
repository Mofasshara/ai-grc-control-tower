import hashlib
import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from database import get_db
from models.rag_source import RAGSource
from models.rag_source_version import RAGSourceStatus, RAGSourceVersion
from models.change_request import ChangeRequest
from schemas.rag import (
    RAGSourceCreate,
    RAGSourceResponse,
    RAGSourceVersionCreate,
    RAGSourceVersionResponse,
)
from security.auth import get_current_user, require_roles
from security.roles import Role
from utils.diff import generate_unified_diff
from schemas.submit import VersionSubmitRequest

router = APIRouter(prefix="/rag", tags=["RAG Governance"])


@router.post(
    "/sources",
    response_model=RAGSourceResponse,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AI_OWNER))],
)
def create_rag_source(
    payload: RAGSourceCreate,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    source = RAGSource(
        name=payload.name,
        description=payload.description,
        source_type=payload.source_type,
        created_by=user.username,
    )

    db.add(source)
    db.commit()
    db.refresh(source)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "RAG_SOURCE_CREATED"
    state["audit_entity_id"] = source.id
    state["audit_entity_type"] = "RAG_SOURCE"

    return source


@router.get("/sources", response_model=list[RAGSourceResponse])
def list_rag_sources(db: Session = Depends(get_db)):
    return db.query(RAGSource).all()


@router.get("/sources/{source_id}", response_model=RAGSourceResponse)
def get_rag_source(source_id: str, db: Session = Depends(get_db)):
    source = db.query(RAGSource).filter(RAGSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="RAG source not found")
    return source


@router.post(
    "/sources/{source_id}/versions",
    response_model=RAGSourceVersionResponse,
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AI_OWNER))],
)
def create_rag_source_version(
    source_id: str,
    payload: RAGSourceVersionCreate,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    source = db.query(RAGSource).filter(RAGSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="RAG source not found")

    prev_version = (
        db.query(RAGSourceVersion)
        .filter(RAGSourceVersion.rag_source_id == source_id)
        .order_by(RAGSourceVersion.version.desc())
        .first()
    )

    new_version_number = 1 if not prev_version else prev_version.version + 1

    prev_config = None
    if prev_version:
        prev_config = json.dumps(
            {
                "uri": prev_version.uri,
                "ingestion_config": prev_version.ingestion_config,
                "embedding_config": prev_version.embedding_config,
            },
            sort_keys=True,
            default=str,
        )

    current_config = json.dumps(
        {
            "uri": payload.uri,
            "ingestion_config": payload.ingestion_config,
            "embedding_config": payload.embedding_config,
        },
        sort_keys=True,
        default=str,
    )

    diff = generate_unified_diff(prev_config, current_config)

    content_hash = hashlib.sha256(current_config.encode("utf-8")).hexdigest()

    version = RAGSourceVersion(
        rag_source_id=source_id,
        version=new_version_number,
        status=RAGSourceStatus.DRAFT,
        uri=payload.uri,
        ingestion_config=payload.ingestion_config,
        embedding_config=payload.embedding_config,
        content_hash=content_hash,
        diff_from_prev=diff,
        created_by=user.username,
    )

    db.add(version)
    db.commit()
    db.refresh(version)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "RAG_SOURCE_VERSION_CREATED"
    state["audit_entity_id"] = version.id
    state["audit_entity_type"] = "RAG_SOURCE_VERSION"

    return version


@router.get("/sources/{source_id}/versions", response_model=list[RAGSourceVersionResponse])
def list_rag_versions(source_id: str, db: Session = Depends(get_db)):
    return (
        db.query(RAGSourceVersion)
        .filter(RAGSourceVersion.rag_source_id == source_id)
        .order_by(RAGSourceVersion.version.asc())
        .all()
    )


@router.get("/versions/{version_id}", response_model=RAGSourceVersionResponse)
def get_rag_version(version_id: str, request: Request, db: Session = Depends(get_db)):
    version = db.query(RAGSourceVersion).filter(RAGSourceVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="RAG source version not found")

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "RAG_SOURCE_VERSION_VIEWED"
    state["audit_entity_id"] = version.id
    state["audit_entity_type"] = "RAG_SOURCE_VERSION"

    return version


@router.get("/versions/{version_id}/diff")
def get_rag_version_diff(version_id: str, db: Session = Depends(get_db)):
    version = db.query(RAGSourceVersion).filter(RAGSourceVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="RAG source version not found")

    return {"diff": version.diff_from_prev}


@router.post(
    "/versions/{version_id}/submit",
    dependencies=[Depends(require_roles(Role.ADMIN, Role.AI_OWNER))],
)
def submit_rag_version(
    version_id: str,
    payload: VersionSubmitRequest,
    request: Request,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    version = db.query(RAGSourceVersion).filter(RAGSourceVersion.id == version_id).first()
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
    if change_status != "submitted":
        raise HTTPException(
            status_code=400,
            detail="Change request must be SUBMITTED before linking",
        )

    if version.change_request_id and str(version.change_request_id) != payload.change_request_id:
        raise HTTPException(status_code=400, detail="RAG version already linked")

    version.change_request_id = change_request.id
    version.status = RAGSourceStatus.SUBMITTED

    db.commit()
    db.refresh(version)

    state = request.scope.setdefault("state", {})
    state["audit_action"] = "RAG_SOURCE_VERSION_SUBMITTED"
    state["audit_entity_id"] = version.id
    state["audit_entity_type"] = "RAG_SOURCE_VERSION"

    return {
        "id": version.id,
        "status": getattr(version.status, "value", version.status),
        "change_request_id": version.change_request_id,
        "submitted_by": user.username,
    }
