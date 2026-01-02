from pydantic import BaseModel

from backend.schemas.ai_system import LifecycleStatus


class LifecycleUpdate(BaseModel):
    new_state: LifecycleStatus
    updated_by: str
