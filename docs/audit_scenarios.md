# Audit Scenarios

## Audit Scenario #1 — Prompt Change Control
Auditor asks:
“How do you control prompt changes?”

### 1. Prompt Version History
Show that every prompt has:
- Version number
- Timestamp
- Author
- Hash
- Change description

Example narrative:
Here is the full version history for Prompt X.
Every change is versioned, timestamped, and linked to a change request.

### 2. Approved Change Request
Show the workflow:
- AI Owner submits change
- Compliance reviews
- Admin approves
- GitHub Actions deploys only after approval

Example narrative:
This prompt change was not deployed automatically.
It required human approval from Compliance before release.

### 3. Audit Log Entry
Show the append-only audit log:
- Who changed the prompt
- What changed
- When
- Hash of the payload

Example narrative:
The audit log shows the exact API call, user ID, and hashed payload.
Nothing can be deleted or modified.

### 4. Evidence Pack Entry
Show that the release evidence ZIP contains:
- Prompt version
- Change request
- Approval metadata
- Hash manifest

Example narrative:
This evidence pack proves the prompt version that went live,
who approved it, and the exact hash of the deployed artifact.

Purpose (simple)
This scenario shows governance in action, not theory.
It proves you can control AI changes — the #1 requirement in regulated AI.

## Audit Scenario #2 — Hallucination Incident Lifecycle
Auditor asks:
“Show me how you handle hallucinations.”

### 1. Hallucination Reported
Show:
- Incident created with type = HALLUCINATION
- Description of the hallucination
- AI system ID
- Timestamp

Example narrative:
A hallucination was reported by the AI Owner and logged as a regulated incident.

### 2. Severity Classified
Show:
- Severity = Medium / High
- Classification rationale
- Reviewer (Compliance)

Example narrative:
Compliance classified this hallucination as High severity due to customer impact.

### 3. Root Cause Identified
Show:
- Prompt version at time of incident
- RAG source version
- Recent changes
- Drift signals

Example narrative:
Root cause analysis shows the hallucination occurred after a prompt update.

### 4. Corrective Prompt Change Approved
Show:
- New prompt version created
- Change request submitted
- Compliance approval
- Deployment via GitHub Actions

Example narrative:
A corrective prompt update was proposed and approved through the change control workflow.

### 5. Evidence Trail Generated
Show:
- Incident record
- Root cause analysis
- Corrective change request
- Approval metadata
- Evidence pack ZIP

Example narrative:
The evidence pack contains the full incident lifecycle, including root cause and corrective actions.

Purpose (simple)
This scenario proves you can detect, classify, investigate, and correct hallucinations —
something almost no AI engineer can demonstrate.

## Audit Scenario #3 — Evidence Request for AI System X
Auditor asks:
“Give me all evidence for AI System X.”

### 1. Generate Evidence ZIP
Show:
- /evidence/generate?ai_system_id=X
- ZIP file created
- Stored in Azure Blob Storage
- Immutable

Example narrative:
The system generates a complete evidence pack for AI System X on demand.

### 2. Show Hashes
Inside the ZIP:
- SHA-256 hash manifest
- Hashes for:
  - Prompt versions
  - RAG sources
  - Change requests
  - Incidents
  - Audit logs

Example narrative:
Every artifact is hashed to ensure integrity and tamper detection.

### 3. Show Traceability Matrix
Include:
- AI system → prompts → RAG sources → incidents → changes → approvals → evidence

Example narrative:
This traceability matrix shows the full lineage of AI System X.

Purpose (simple)
This is exactly how real audits happen.
You show you can produce complete, tamper-proof evidence on demand.
