# Week 01 Summary — AI-GRC Control Tower

## Scope of Work

This week focused on establishing the compliance foundation for an AI-GRC control tower:
- Governance model and roles
- Architecture and system boundaries
- Immutable audit logging
- Evidence and documentation structure

---

## Implemented Controls

### 1. Governance and Roles

- **AI Owner:** Accountable for system purpose, risk classification, and lifecycle.
- **AI Engineer:** Implements models, prompts, and RAG components but cannot self-approve deployments.
- **Compliance Officer:** Reviews risks, approves changes, and validates evidence.
- **Auditor:** Read-only access to logs, evidence, and approvals.
- **System Administrator:** Manages platform configuration only.

**Why this matters:**  
This enforces segregation of duties and prevents one person from owning, changing, and approving the same AI system.

---

### 2. Technical Architecture

- **FastAPI Backend:** Single source of truth for all AI governance workflows.
- **PostgreSQL Database:** Stores AI inventory, prompts, change requests, approvals, incidents, and audit logs.
- **Azure Blob Storage:** Stores immutable evidence artifacts (snapshots, exports, documents).
- **Azure OpenAI:** Provides advisory-only AI capabilities (summaries, drafts) -- never final decisions.
- **Logging / Monitoring:** Centralized, append-only audit logging at the request level.

**Why this matters:**  
The architecture clearly separates:
- Decision logic (backend)
- Data storage (database)
- Evidence storage (blob)
- AI advisory capability (LLM)
- Audit visibility (logs)

---

### 3. Immutable Audit Logging

- Every API request goes through a middleware.
- The request payload is hashed (SHA-256).
- An entry is written into the `audit_logs` table with:
  - Timestamp (UTC)
  - User identifier
  - Action (HTTP method + path)
  - Optional entity type and entity ID
  - Payload hash

**No updates, no deletes** are performed against `audit_logs` by application code.

**Why this matters:**  
This creates a tamper-evident, append-only trail of all activity, which is critical for:
- Regulatory audits
- Incident investigations
- Internal reviews

---

### 4. Evidence Collected

Stored under: `evidence/week_01/`

- `01_github_repo.png` -- Repository structure and commit history.
- `02_readme_overview.png` -- High-level documentation and project description.
- `03_governance_roles.png` -- Defined roles and segregation of duties.
- `04_governance_controls_evidence.png` -- Governance controls and evidence expectations.
- `05_architecture_diagram.png` -- End-to-end system architecture.
- `06_swagger_ui.png` -- Live API documentation, proving the backend is running.

**Why this matters:**  
This is not just code; it is a reproducible, visual evidence package that demonstrates:
- Traceability
- Thoughtful design
- Compliance awareness

---

## Why Auditors Would Trust This

- **Clear Governance Model:** Responsibilities are defined, separated, and documented.
- **Controlled Architecture:** Every path to data and AI is routed through the backend, which enforces rules.
- **Append-only Audit Trail:** Actions are logged with hashes and timestamps, forming a verifiable history.
- **Evidence Readiness:** Screenshots and documentation show how the system is structured and operated.
- **Advisory-only AI:** AI helps generate content but does not bypass human approval or governance workflows.

This combination of design, implementation, and evidence aligns with expectations for regulated environments 
(e.g., finance, pharma, and other high-compliance sectors).

---

## Why Recruiters Would Care

- Demonstrates end-to-end ownership: architecture, governance, implementation, and evidence.
- Shows you understand not just "how to build APIs" but "how to build auditable systems".
- Proves you can think like:
  - An engineer,
  - A compliance partner,
  - And an auditor.

This is Week 01. The foundation is now in place for scalable, compliant AI governance.
