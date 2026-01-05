# AI-GRC Control Tower User Manual (API-First)

This guide explains how to use each API endpoint step by step. It is written for someone new to the system.

## 0. Quick Start

### Base URL
- Local: `http://localhost:8000`
- Azure: `https://<your-app>.azurewebsites.net`

### Authentication (if enabled)
- Use Azure Entra ID via Easy Auth.
- For API tools (Postman/curl), include:
  - Header: `Authorization: Bearer <TOKEN>`

### Swagger UI
- Open: `http://localhost:8000/docs`

---

## 1. Health Check

### GET /health
Purpose: Verify the service is running.

Steps:
1) Open Swagger UI.
2) Find `GET /health`.
3) Click `Try it out` → `Execute`.
4) Expect: `{ "status": "ok" }`.

---

## 2. AI Systems

### POST /ai-systems/
Purpose: Create a new AI system record.

Steps:
1) Open Swagger UI.
2) Find `POST /ai-systems/`.
3) Click `Try it out`.
4) Fill the JSON body:
```json
{
  "name": "Fraud Engine",
  "business_purpose": "Detect fraudulent transactions",
  "intended_users": "Risk analysts",
  "risk_classification": "medium",
  "owner": "risk-team@company.com",
  "created_by": "you@company.com"
}
```
5) Click `Execute`.
6) Copy the returned `id` (AI system ID).

### GET /ai-systems/
Purpose: List all AI systems.

Steps:
1) Find `GET /ai-systems/`.
2) Click `Try it out` → `Execute`.
3) Review the list.

### GET /ai-systems/{system_id}
Purpose: Fetch a single AI system.

Steps:
1) Find `GET /ai-systems/{system_id}`.
2) Paste your AI system ID.
3) Click `Execute`.

### PATCH /ai-systems/{system_id}/lifecycle
Purpose: Move the AI system through lifecycle states.

Steps:
1) Find `PATCH /ai-systems/{system_id}/lifecycle`.
2) Provide the AI system ID.
3) Use a JSON body:
```json
{ "new_state": "submitted" }
```
4) Click `Execute`.
5) For `submitted → approved`, a Compliance role is required.

---

## 3. Change Requests

### POST /ai-systems/{system_id}/changes
Purpose: Create a change request.

Steps:
1) Find `POST /ai-systems/{system_id}/changes`.
2) Provide the AI system ID.
3) Use a JSON body:
```json
{
  "change_type": "prompt",
  "description": "Refine prompt to reduce false positives",
  "business_justification": "Improve accuracy while maintaining auditability",
  "impact_assessment": "May reduce alert volume by 10%",
  "rollback_plan": "Revert to previous prompt version",
  "requested_by": "you@company.com"
}
```
4) Click `Execute`.
5) Copy the `id` (change request ID).

### GET /changes
Purpose: List all change requests.

Steps:
1) Find `GET /changes`.
2) Click `Execute`.

### GET /changes/{change_id}
Purpose: Fetch a single change request.

Steps:
1) Find `GET /changes/{change_id}`.
2) Paste the change request ID.
3) Click `Execute`.

### POST /changes/{change_id}/approve
Purpose: Approve a change request (Admin/Compliance only).

Steps:
1) Find `POST /changes/{change_id}/approve`.
2) Paste the change request ID.
3) Click `Execute`.
4) Confirm response shows approved status.

### POST /changes/{change_id}/reject
Purpose: Reject a change request.

Steps:
1) Find `POST /changes/{change_id}/reject`.
2) Paste the change request ID.
3) Click `Execute`.

---

## 4. Prompt Governance

### POST /prompts/templates
Purpose: Create a prompt template.

Steps:
1) Find `POST /prompts/templates`.
2) Use JSON:
```json
{
  "name": "Fraud Explanation",
  "description": "Explain why a transaction is flagged"
}
```
3) Click `Execute` and copy the template ID.

### POST /prompts/templates/{template_id}/versions
Purpose: Create a new prompt version.

Steps:
1) Find `POST /prompts/templates/{template_id}/versions`.
2) Paste the template ID.
3) Use JSON:
```json
{
  "prompt_text": "Explain why this transaction was flagged:",
  "parameters_schema": { "type": "object" }
}
```
4) Click `Execute` and copy the version ID.

### POST /prompts/versions/{version_id}/submit
Purpose: Submit a prompt version for review.

Steps:
1) Find `POST /prompts/versions/{version_id}/submit`.
2) Paste the version ID.
3) Provide JSON:
```json
{ "change_request_id": "<CHANGE_ID>" }
```
4) Click `Execute`.

### POST /ai-systems/{system_id}/prompts/activate
Purpose: Activate a submitted prompt version.

Steps:
1) Find `POST /ai-systems/{system_id}/prompts/activate`.
2) Paste the AI system ID.
3) Use JSON:
```json
{
  "prompt_version_id": "<VERSION_ID>",
  "change_request_id": "<CHANGE_ID>"
}
```
4) Click `Execute`.

### GET /prompts/templates/{template_id}/versions
Purpose: View prompt version history.

Steps:
1) Find `GET /prompts/templates/{template_id}/versions`.
2) Paste the template ID.
3) Click `Execute`.

### GET /prompts/versions/{version_id}/diff
Purpose: View the diff between versions.

Steps:
1) Find `GET /prompts/versions/{version_id}/diff`.
2) Paste the version ID.
3) Click `Execute`.

---

## 5. RAG Governance

### POST /rag/sources
Purpose: Create a RAG source.

Steps:
1) Find `POST /rag/sources`.
2) Provide JSON:
```json
{
  "name": "Policy Library",
  "source_type": "document",
  "description": "Internal policy documents"
}
```
3) Click `Execute` and copy the RAG source ID.

### POST /rag/sources/{source_id}/versions
Purpose: Create a new RAG source version.

Steps:
1) Find `POST /rag/sources/{source_id}/versions`.
2) Paste the source ID.
3) Provide JSON (example):
```json
{
  "uri": "https://storage/account/policies.zip",
  "ingestion_config": { "chunk_size": 800 },
  "embedding_config": { "model": "text-embedding-3-large" }
}
```
4) Click `Execute` and copy the version ID.

### POST /rag/versions/{version_id}/submit
Purpose: Submit a RAG version for review.

Steps:
1) Find `POST /rag/versions/{version_id}/submit`.
2) Paste the version ID.
3) Provide JSON:
```json
{ "change_request_id": "<CHANGE_ID>" }
```
4) Click `Execute`.

### POST /ai-systems/{system_id}/rag/activate
Purpose: Activate a submitted RAG version.

Steps:
1) Find `POST /ai-systems/{system_id}/rag/activate`.
2) Paste the AI system ID.
3) Use JSON:
```json
{
  "rag_source_version_id": "<RAG_VERSION_ID>",
  "change_request_id": "<CHANGE_ID>"
}
```
4) Click `Execute`.

### GET /rag/sources/{source_id}/versions
Purpose: View RAG version history.

Steps:
1) Find `GET /rag/sources/{source_id}/versions`.
2) Paste the source ID.
3) Click `Execute`.

---

## 6. Incident Management

### POST /incidents/ai-systems/{ai_system_id}/incidents
Purpose: Report an AI incident (including hallucinations).

Steps:
1) Find `POST /incidents/ai-systems/{ai_system_id}/incidents`.
2) Paste the AI system ID.
3) Use JSON:
```json
{
  "incident_type": "Hallucination",
  "severity": "High",
  "impact_area": "Regulatory compliance",
  "description": "Model fabricated a compliance rule"
}
```
4) Click `Execute` and copy the incident ID.

### POST /incidents/{incident_id}/investigate
Purpose: Record investigation and root cause.

Steps:
1) Find `POST /incidents/{incident_id}/investigate`.
2) Paste the incident ID.
3) Use JSON:
```json
{
  "root_cause_category": "Prompt design",
  "root_cause_description": "Outdated prompt version"
}
```
4) Click `Execute`.

### POST /incidents/{incident_id}/corrective-action
Purpose: Link a corrective change and resolve.

Steps:
1) Find `POST /incidents/{incident_id}/corrective-action`.
2) Paste the incident ID.
3) Use JSON:
```json
{ "change_request_id": "<CHANGE_ID>" }
```
4) Click `Execute`.

### GET /incidents/
Purpose: List incidents.

Steps:
1) Find `GET /incidents/`.
2) Click `Execute`.

### GET /incidents/{incident_id}
Purpose: View a specific incident.

Steps:
1) Find `GET /incidents/{incident_id}`.
2) Paste the incident ID.
3) Click `Execute`.

---

## 7. Evidence Packs

### POST /evidence/generate
Purpose: Generate a release evidence pack.

Steps:
1) Find `POST /evidence/generate`.
2) Click `Execute`.
3) Download the returned ZIP or note its storage path.

---

## 8. Risk Monitoring

### GET /risk/summary
Purpose: Executive risk snapshot.

Steps:
1) Find `GET /risk/summary`.
2) Click `Execute`.
3) Review severity counts, hallucination rates, volatility, flags.

### GET /risk/trends/incidents
Purpose: Risk trends.

Steps:
1) Find `GET /risk/trends/incidents`.
2) Click `Execute`.
3) Review hallucinations per week, severity trend, repeated incidents.

### GET /risk/drift
Purpose: Drift signals.

Steps:
1) Find `GET /risk/drift`.
2) Click `Execute`.
3) Review prompt drift, RAG drift, incident‑correlated drift.

---

## 9. Prompt & RAG Version Lookup

### GET /prompts/versions/{version_id}
Purpose: View a prompt version.

Steps:
1) Find `GET /prompts/versions/{version_id}`.
2) Paste the version ID.
3) Click `Execute`.

### GET /rag/versions/{version_id}
Purpose: View a RAG source version.

Steps:
1) Find `GET /rag/versions/{version_id}`.
2) Paste the version ID.
3) Click `Execute`.

---

## 10. Tips for New Users
- Start by creating an AI system, then a change request.
- Create a prompt version and submit it to a change request.
- Approve the change request, then activate the prompt.
- Report an incident and link a corrective change request.
- Generate an evidence pack and check risk endpoints.

---

## 11. Status Workflows (What Moves to What)

### AI System Lifecycle Status
Statuses:
- draft
- submitted
- approved
- active
- retired

Allowed transitions:
draft → submitted → approved → active → retired

Notes:
- Only Compliance can approve submitted systems.

### Change Request Status
Statuses:
- draft
- submitted
- approved
- implemented
- rejected

Allowed transitions:
draft → submitted → approved → implemented
draft → submitted → rejected

### Prompt Version Status
Statuses:
- DRAFT
- SUBMITTED
- ACTIVE
- RETIRED

Typical flow:
DRAFT → SUBMITTED → ACTIVE → RETIRED

Notes:
- A prompt version must be SUBMITTED and linked to an approved change request before activation.

### RAG Source Version Status
Statuses:
- DRAFT
- SUBMITTED
- ACTIVE
- RETIRED

Typical flow:
DRAFT → SUBMITTED → ACTIVE → RETIRED

Notes:
- A RAG version must be SUBMITTED and linked to an approved change request before activation.

### Incident Status
Statuses:
- OPEN
- UNDER_INVESTIGATION
- RESOLVED
- CLOSED

Typical flow:
OPEN → UNDER_INVESTIGATION → RESOLVED → CLOSED

Notes:
- Corrective changes are linked before an incident is marked RESOLVED.
