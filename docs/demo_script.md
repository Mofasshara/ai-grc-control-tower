# Timed Demo Script (15 Minutes)

## Minute 0–2: Problem (regulators don’t trust AI)
"In regulated industries like banking and pharma, regulators don’t trust AI by default. They want proof: who changed it, who approved it, what went live, and whether incidents are tracked. Most AI projects show models — not governance. I built a regulator‑first AI Governance, Risk & Compliance platform that makes AI changes auditable, incidents accountable, and evidence retrievable on demand."

## Minute 2–5: Architecture & governance
"This platform runs on Azure App Service with a PostgreSQL backend. Identity is enforced through Microsoft Entra ID, and every action is logged immutably. Governance is built in: an AI system registry with lifecycle states, change control workflows for prompts/RAG/model configs, and role‑based access control for Admin, Compliance, Auditor, and AI Owner. The result is a system that enforces segregation of duties, not just documentation."

## Minute 5–8: Change + incident demo
"Let me show governance in action. First, a prompt change: every prompt has version history with timestamps, author, hash, and change request linkage. Changes are submitted by AI Owners, reviewed by Compliance, and only approved changes deploy — pipelines execute, humans approve. Now an incident: hallucinations are first‑class incident types with severity, impact area, and root‑cause analysis. We can show that an incident led to a corrective prompt change and a formal approval trail."

## Minute 8–12: Evidence pack generation
"Auditors don’t want screenshots — they want evidence packs. The system generates a ZIP evidence pack with audit logs, approvals, hashes, and a traceability matrix. That pack is stored immutably in Azure Blob Storage and can be requested per AI system. This gives auditors a reproducible snapshot of what was approved and what ran, years later."

## Minute 12–15: Risk monitoring
"Finally, risk monitoring. The platform exposes risk intelligence through APIs: `/risk/summary` for severity counts and hallucination rates, `/risk/trends/incidents` for trend analysis, and `/risk/drift` for prompt/RAG drift signals. This is a compliance cockpit — no UI needed. It shows whether risk is rising, whether prompts or RAG sources are unstable, and whether changes correlate with incidents."
