import hashlib
import json
import logging
from datetime import datetime

from fastapi import FastAPI, Request
from sqlalchemy.orm import Session

from database import SessionLocal
from models import AuditLog
from routers.ai_system import router as ai_system_router

logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI-GRC Control Tower",
    description="Regulator-first AI governance platform",
    version="0.1.0",
)

app.include_router(ai_system_router)


def hash_payload(payload: dict) -> str:
    payload_str = json.dumps(payload, sort_keys=True, default=str)
    return hashlib.sha256(payload_str.encode("utf-8")).hexdigest()


@app.middleware("http")
async def audit_logging_middleware(request: Request, call_next):
    body_bytes = await request.body()
    try:
        body = json.loads(body_bytes.decode("utf-8")) if body_bytes else {}
    except json.JSONDecodeError:
        body = {"raw": body_bytes.decode("utf-8", errors="ignore")}

    async def receive():
        return {"type": "http.request", "body": body_bytes, "more_body": False}

    request_with_body = Request(request.scope, receive=receive)

    payload_hash = hash_payload(body)
    user_id = request.headers.get("x-user-id", "anonymous")
    method = request.method
    path = request.url.path

    response = await call_next(request_with_body)

    state = request.scope.get("state", {})
    action = state.get("audit_action", f"{method} {path}")
    entity_id = state.get("audit_entity_id")
    entity_type = state.get("audit_entity_type")

    db: Session = SessionLocal()
    try:
        log_entry = AuditLog(
            timestamp=datetime.utcnow(),
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            payload_hash=payload_hash,
        )
        db.add(log_entry)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Audit log insert failed")
    finally:
        db.close()

    return response


@app.get("/health")
def health():
    return {"status": "ok"}
