# Critical Tests

## 1. Purpose
This document defines the mandatory governance tests that must pass before any release can be approved or deployed. These tests protect the integrity, safety, and auditability of the AI-GRC platform.

## 2. Critical Test Categories

### A. /health Endpoint Test
Purpose:
- Ensures the API is alive
- Ensures dependencies (DB, Key Vault, Storage) are reachable
- Ensures no broken deployments reach production

Test description:

Code
GET /health must return 200 OK.

### B. Change Approval Workflow Test
Purpose:
- Ensures the approval workflow is functioning
- Ensures segregation of duties
- Ensures no unauthorized changes can be deployed

Test description:

Code
POST /changes/{id}/approve must enforce RBAC and return correct status codes.

### C. Incident Creation Test
Purpose:
- Ensures incidents can be logged
- Ensures the audit trail is intact
- Ensures safety-related events are captured

Test description:

Code
POST /incidents/create must succeed and write to the audit log.

### D. Evidence Generation Test
Purpose:
- Ensures evidence packs can be generated
- Ensures traceability and auditability
- Ensures the release pipeline can freeze the system state

Test description:

Code
POST /evidence/generate must return a valid ZIP with all required files.

## 3. Blocking Rule

Code
If any critical test fails, the release pipeline must stop immediately. No deployment is allowed.

## Simple explanation
Not all tests are equal.
These four tests protect governance, auditability, and risk controls.
If they fail, the release must never proceed.
