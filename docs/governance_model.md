# AI Governance Model

## Roles

### AI Owner
Accountable for the AI system's purpose, risk classification, and lifecycle.

### AI Engineer
Implements models, prompts, and RAG components.
Cannot deploy changes without approval.

### Compliance Officer
Reviews risks, approves changes, and validates evidence.

### Auditor
Read-only access to evidence, logs, and approvals.

### System Administrator
Manages platform configuration only.

## Purpose
Clear segregation of duties -- mandatory for regulators.

## Mandatory Control Points

1. AI system registration before use
2. Risk classification before activation
3. Approval required for:
   - Model changes
   - Prompt changes
   - RAG source changes
4. Incident logging for:
   - Hallucinations
   - Bias
   - Unsafe outputs
5. Evidence generation on demand

## Purpose
These become hard system requirements later.

## Evidence Requirements

The system must produce:
- AI inventory snapshot
- Change history with approvals
- Incident records with root cause analysis
- Timestamped and hashed artifacts
