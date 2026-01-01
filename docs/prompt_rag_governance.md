# Prompt & RAG Governance

## Prompt Governance
Prompts are governed artifacts. Any change requires:
- New version creation
- Reason + impact
- Approval (via Change Request)
- Audit logging

### Why Prompt Governance Matters

Prompts directly influence model behavior. Uncontrolled prompt changes can:
- Introduce bias
- Alter decision logic
- Break compliance expectations
- Create untraceable behavior changes

Therefore, prompts must be versioned, reviewed, approved, and logged.

## RAG Governance
RAG sources and ingestion configs are governed artifacts. Any change requires:
- New version creation
- Reason + impact
- Approval (via Change Request)
- Audit logging

### Why RAG Governance Matters

RAG sources determine what knowledge the model retrieves.
Changes to RAG sources can:
- Introduce outdated or incorrect information
- Add unapproved documents
- Modify risk scoring logic
- Create compliance violations

Therefore, RAG sources and ingestion configurations must be governed artifacts.

## Mandatory Traceability
AI System -> Prompt Version -> RAG Source Version -> Change Request -> Approval -> Audit Log

### Why Traceability Is Mandatory

Regulators require full lineage:
- Which prompt version was active?
- Which RAG source version was active?
- Which change request approved it?
- Who approved it?
- When was it activated?

This ensures accountability and prevents shadow changes.

## Activation Rule
A prompt/RAG version can only be marked ACTIVE if linked to an APPROVED change request.

### Why Activation Requires Approval

A prompt or RAG version cannot be ACTIVE unless:
- A change request exists
- It has been reviewed
- It has been approved
- It has been logged

This prevents unauthorized or accidental activation of unapproved versions.

## Scope

This policy applies to:
- All AI systems registered in the AI-GRC Control Tower
- All prompt templates and prompt versions
- All RAG sources and ingestion configurations
- All environments (dev/test/prod)

## Roles & Responsibilities

### AI Owner
- Defines prompt/RAG requirements
- Submits change requests

### AI Engineer
- Implements new versions
- Provides technical impact assessment

### Compliance
- Reviews high-risk changes
- Approves activation for regulated systems

### Auditor
- Reviews traceability and evidence
