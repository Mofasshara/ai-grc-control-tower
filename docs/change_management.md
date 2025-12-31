# AI Change Management Policy

All changes to AI systems must be controlled, reviewed, and approved.

## Change Types
- Model version change
- Prompt change
- RAG data source change
- Configuration change

### Model Version Change
Any update to the underlying model (LLM, ML model, fine-tuned model, etc.).

### Prompt Change
Any modification to system prompts, user prompts, or prompt templates.

### RAG Data Source Change
Any update to documents, embeddings, chunking strategy, or retrieval logic.

### Configuration Change
Any modification to parameters, thresholds, routing logic, or system settings.
This removes ambiguity -- auditors hate ambiguity.

## Mandatory Fields
- Change description
- Business justification
- Impact assessment
- Rollback plan

### Why These Fields Are Mandatory

- **Change description** -- ensures clarity and prevents undocumented modifications.
- **Business justification** -- ensures the change aligns with organizational goals.
- **Impact assessment** -- ensures risks are understood before implementation.
- **Rollback plan** -- ensures safe recovery if the change introduces issues.

These fields are required for all AI system changes in regulated environments.

## Approval Rules
- All changes require approval
- High-risk AI systems require Compliance approval

### Why Approvals Are Required

All AI changes must be reviewed to prevent:
- Unauthorized modifications
- Bias introduction
- Model drift
- Compliance violations
- Safety risks

High-risk AI systems require Compliance approval due to their potential impact on:
- Customers
- Patients
- Financial stability
- Regulatory exposure

## API Endpoints (Current Implementation)
- POST /ai-systems/{id}/changes
- GET /changes
- GET /changes/{id}

## Purpose of This Policy

This policy ensures that all modifications to AI systems are:
- Documented
- Reviewed
- Risk-assessed
- Approved by the appropriate roles
- Traceable for audit purposes

Regulators expect a formal change-management policy before any technical implementation. 
This document provides the justification for every control implemented in the AI-GRC platform.
This is important because auditors always ask:

"Where is the policy that justifies this workflow?"

Now you have it.

## Change Lifecycle States

Draft -> Submitted -> Approved -> Implemented -> Rejected

### Draft
The change is being prepared. No review has occurred.

### Submitted
The change is ready for review. Mandatory fields must be completed.

### Approved
The change has been reviewed and authorized by the required roles.

### Implemented
The change has been deployed to the system.

### Rejected
The change was reviewed but not approved due to risk, incomplete information, or misalignment with business goals.

### Purpose of Lifecycle Control

Lifecycle control ensures:
- No unauthorized changes
- No skipping approval steps
- Full traceability from request to implementation
- Clear accountability for each stage
- Compliance with FINMA, GxP, and CSV expectations

Lifecycle enforcement is mandatory in regulated environments.
