## One-Sentence Positioning
I built a regulator-first AI Governance, Risk & Compliance platform for banking and pharma that controls AI changes, tracks incidents and hallucinations, generates audit evidence, and runs on Azure.

# Portfolio Story: Three Pillars

## 1. Governance & Controls
- AI System Registry with lifecycle states (draft → approved → production)
- Change Control workflow for prompts, RAG sources, and model configs
- Role-Based Access Control enforcing segregation of duties (Admin, Compliance, Auditor, AI Owner)
- Manual release approval gate in GitHub Actions (human-in-the-loop)

## 2. Risk & Incident Management
- Incident tracking with severity, type, and hallucination tagging
- Risk metrics engine (hallucination rate, severity trends, change volatility)
- Drift detection signals (prompt/RAG drift, incident-correlated drift)
- Risk API endpoints (`/risk/summary`, `/risk/trends/incidents`, `/risk/drift`)

## 3. Evidence & Audit Readiness
- Evidence pack generator (ZIP with logs, approvals, hashes, traceability matrix)
- Immutable audit log (append-only, hashed, timestamped)
- Data governance policy (classification + retention: 7–10 years)
- Release approval metadata (who approved, when, version)

## Purpose (Simple)
Interviewers think in themes, not features. These three pillars make the project sound senior, structured, and intentional.
