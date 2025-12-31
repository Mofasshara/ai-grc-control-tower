# Week 02 Summary -- AI-GRC Control Tower

## Overview

Week 2 focused on building a regulator-ready AI System Registry with:
- Mandatory metadata
- Risk classification
- Ownership
- Lifecycle controls
- Audit logging

This registry is the foundation for all downstream governance workflows.

---

## Demo Data Created

Three AI systems were created to demonstrate the registry:

1. **Low-risk** -- Document Classifier
2. **Medium-risk** -- Customer Support Assistant
3. **High-risk** -- Fraud Detection Engine

These represent typical categories in banking and pharma environments.

---

## Evidence Collected (Stored in /evidence/week_02)

- `01_swagger_ui.png` -- Live API documentation
- `02_ai_system_list.png` -- Registry with 3 risk levels
- `03_audit_logs.png` -- Append-only audit trail
- `04_db_schema.png` -- Database structure with enums and constraints

---

## Why This Registry Satisfies Governance Expectations

### 1. Mandatory Metadata
Every AI system must include:
- Business purpose
- Intended users
- Owner
- Risk classification
- Created_by

This aligns with:
- FINMA expectations for AI accountability
- GxP requirements for system ownership
- CSV expectations for traceability

### 2. Controlled Vocabularies (Enums)
Risk classification and lifecycle status use enums:
- Prevents free-text errors
- Enforces consistent categories
- Enables automated risk-based controls

### 3. Auditability
Every action:
- Is logged
- Includes a payload hash
- Includes a timestamp
- Is append-only

This satisfies:
- Audit trail requirements
- Non-repudiation
- Evidence integrity

---

## How Risk Classification Drives Controls Later

Risk classification determines:
- Required approvals
- Required testing
- Required monitoring
- Required documentation
- Required lifecycle gates

Examples:
- **High-risk** systems require Compliance approval
- **Medium-risk** systems require enhanced monitoring
- **Low-risk** systems follow simplified workflows

This sets the stage for:
- Change control
- Incident management
- Model monitoring
- Evidence pack generation

---

## Conclusion

Week 2 delivered a fully functional, auditable AI System Registry with:
- Real demo data
- Strong governance foundations
- Risk-based categorization
- Evidence suitable for auditors and recruiters

This registry is now ready to support change control, lifecycle management, and incident workflows in Week 3 and beyond.
