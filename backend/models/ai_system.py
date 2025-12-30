import enum
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from . import Base, generate_uuid


class RiskClassification(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class LifecycleStatus(str, enum.Enum):
    draft = "draft"
    active = "active"
    deprecated = "deprecated"
    retired = "retired"


class AISystem(Base):
    __tablename__ = "ai_systems"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    business_purpose: Mapped[str] = mapped_column(Text, nullable=False)
    intended_users: Mapped[str] = mapped_column(Text, nullable=False)
    risk_classification: Mapped[RiskClassification] = mapped_column(Enum(RiskClassification), nullable=False)
    owner: Mapped[str] = mapped_column(String(255), nullable=False)
    lifecycle_status: Mapped[LifecycleStatus] = mapped_column(
        Enum(LifecycleStatus),
        nullable=False,
        default=LifecycleStatus.draft,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_by: Mapped[str] = mapped_column(String(255), nullable=False)
