import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID

from . import Base


def generate_uuid():
    return str(uuid.uuid4())


class IncidentType(str, enum.Enum):
    HALLUCINATION = "Hallucination"
    INCORRECT_OUTPUT = "Incorrect factual output"
    POLICY_VIOLATION = "Policy violation"
    BIAS = "Bias / fairness issue"
    UNSAFE_RECOMMENDATION = "Unsafe recommendation"


class IncidentSeverity(str, enum.Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ImpactArea(str, enum.Enum):
    REGULATORY = "Regulatory compliance"
    CUSTOMER = "Customer impact"
    PATIENT = "Patient safety"
    FINANCIAL = "Financial risk"
    REPUTATIONAL = "Reputational risk"


class IncidentStatus(str, enum.Enum):
    OPEN = "OPEN"
    UNDER_INVESTIGATION = "UNDER_INVESTIGATION"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class RootCauseCategory(str, enum.Enum):
    PROMPT_DESIGN = "Prompt design"
    RAG_DATA_ISSUE = "RAG data issue"
    MODEL_LIMITATION = "Model limitation"
    USER_MISUSE = "User misuse"
    UNKNOWN = "Unknown"


class AIIncident(Base):
    __tablename__ = "ai_incidents"

    id = Column(UUID(as_uuid=False), primary_key=True, default=generate_uuid)

    ai_system_id = Column(
        UUID(as_uuid=False),
        ForeignKey("ai_systems.id"),
        nullable=False,
    )

    incident_type = Column(Enum(IncidentType), nullable=False)

    description = Column(Text, nullable=False)

    contains_personal_data = Column(Boolean, default=False, nullable=False)

    severity = Column(Enum(IncidentSeverity), nullable=False)

    impact_area = Column(Enum(ImpactArea), nullable=False)

    detected_by = Column(String, nullable=False)

    detection_date = Column(DateTime, default=datetime.utcnow, nullable=False)

    status = Column(Enum(IncidentStatus), default=IncidentStatus.OPEN, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String, nullable=False)
    root_cause_category = Column(
        Enum(
            RootCauseCategory,
            values_callable=lambda enum_cls: [e.value for e in enum_cls],
            create_type=False,
        ),
        nullable=True,
    )
    root_cause_description = Column(Text, nullable=True)
    corrective_change_request_id = Column(
        UUID(as_uuid=False),
        ForeignKey("change_requests.id"),
        nullable=True,
    )
