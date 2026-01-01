# Week 03 Summary -- Change Management & Approval Workflow

## Overview

Week 3 focused on implementing a regulator-grade change management workflow for AI systems, including:
- Change request creation
- Mandatory justification fields
- Approval workflow
- Lifecycle enforcement
- Implementation gates
- Audit logging for every action

This ensures that no AI system can change behavior without proper governance.

---

## Example Change Scenarios

Two realistic scenarios were created:

### 1. Prompt Change (Medium Risk)
- Improved prompt clarity for sentiment classification
- Medium operational impact
- Approved by AI Owner / Admin

### 2. RAG Source Change (High Risk)
- Added new FINMA regulatory documents to RAG index
- High compliance impact
- Approved by Compliance only

These demonstrate risk-based governance in action.

---

## Evidence Collected (Stored in /evidence/week_03)

- `01_change_creation.png` -- Change request creation
- `02_prompt_change_approval.png` -- Approval workflow for medium-risk change
- `03_rag_change_approval.png` -- Compliance approval for high-risk change
- `04_audit_logs.png` -- Full audit trail with state hashes
- `05_ai_system_linkage.png` -- AI system updated after implementation

---

## Why Uncontrolled AI Changes Are a Regulatory Risk

Uncontrolled changes can:
- Introduce bias
- Break compliance rules
- Alter model behavior without oversight
- Create untraceable decision paths
- Lead to financial or patient harm
- Violate FINMA, GxP, and CSV requirements

Regulators require:
- Change justification
- Impact assessment
- Approval by accountable roles
- Full traceability
- Evidence of implementation

---

## How This System Prevents Those Risks

The AI-GRC Control Tower enforces:
- Mandatory justification fields
- Role-based approvals
- Lifecycle transitions (Draft -> Submitted -> Approved -> Implemented)
- Implementation gates (no shadow changes)
- Append-only audit logging
- State hashing for tamper evidence
- AI system metadata updates on implementation

This creates a complete, tamper-evident chain of custody for every AI change.

---

## Conclusion

Week 3 delivered a fully functional, regulator-ready change management workflow with:
- Realistic demo scenarios
- Full audit trail
- Risk-based approvals
- Evidence suitable for auditors and recruiters

This completes the foundation for AI governance and prepares the system for prompt governance, RAG governance, and incident workflows in Week 4.
