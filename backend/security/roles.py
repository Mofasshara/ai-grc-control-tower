from enum import Enum


class Role(str, Enum):
    ADMIN = "ADMIN"
    AI_OWNER = "AI_OWNER"
    COMPLIANCE = "COMPLIANCE"
    AUDITOR = "AUDITOR"
