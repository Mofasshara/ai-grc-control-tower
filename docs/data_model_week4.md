# Week 4 Data Model -- Prompt & RAG Governance

## Entities

### prompt_template
Represents the logical prompt (e.g., "Fraud Detection Prompt").
Fields:
- id
- name
- description
- created_at

### prompt_version
Represents a specific version of a prompt.
Fields:
- id
- prompt_template_id (FK)
- version_number
- prompt_text
- metadata (JSON)
- change_request_id (nullable until submitted)
- created_at
- created_by
- is_active (boolean)

### rag_source
Represents a logical RAG source (e.g., "FINMA Circulars").
Fields:
- id
- name
- description
- created_at

### rag_source_version
Represents a specific version of a RAG source.
Fields:
- id
- rag_source_id (FK)
- version_number
- uri
- ingestion_config (JSON)
- change_request_id (nullable until submitted)
- created_at
- created_by
- is_active (boolean)

### ai_system_prompt_binding
Defines which prompt version is active for an AI system.
Fields:
- id
- ai_system_id (FK)
- prompt_version_id (FK)
- activated_at
- activated_by

### ai_system_rag_binding
Defines which RAG source versions are active for an AI system.
Fields:
- id
- ai_system_id (FK)
- rag_source_version_id (FK)
- activated_at
- activated_by

## Linkage Rules

- Each prompt_version must reference a change_request_id.
- Each rag_source_version must reference a change_request_id.
- change_request_id may be NULL while in DRAFT.
- change_request_id becomes REQUIRED when status = SUBMITTED or higher.
- A version cannot be activated unless:
  - change_request.status = APPROVED
  - audit log entry exists

## Rationale

### Why separate template vs version?
Templates define the logical artifact.
Versions define the actual governed content.

### Why binding tables?
AI systems may:
- Switch prompts over time
- Use multiple RAG sources
- Activate different versions per environment

Binding tables provide full traceability.

### Why change_request_id?
This enforces:
- Governance
- Approval
- Auditability
- Non-repudiation

### Why version_number?
Regulators expect explicit versioning, not timestamps alone.
