import hashlib
import json
from datetime import datetime

from fastapi import FastAPI, Request
from sqlalchemy.orm import Session

from database import SessionLocal
from models import AuditLog

app = FastAPI(
    title="AI-GRC Control Tower",
    description="Regulator-first AI governance platform",
    version="0.1.0",
)


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

    request = Request(request.scope, receive=receive)

    payload_hash = hash_payload(body)
    user_id = request.headers.get("x-user-id", "anonymous")
    action = f"{request.method} {request.url.path}"
    entity_type = None
    entity_id = None

    response = await call_next(request)

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
    finally:
        db.close()

    return response


@app.get("/health")
def health():
    return {"status": "ok"}
