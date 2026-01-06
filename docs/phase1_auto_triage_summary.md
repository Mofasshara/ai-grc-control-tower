# Phase 1 - Auto-Triage Summary

## 1. What Auto-Triage Does
The auto-triage engine analyzes every new incident and immediately suggests a severity, a likely root cause, and the correct owner (AI Owner or Compliance). It uses AI system risk level, incident type, drift signals, and recent incident history to make consistent, policy-driven recommendations.

## 2. How Humans Override
Humans remain fully responsible for final decisions. They can confirm or override the system's suggestion. If they override, they must provide a justification, which is stored in the audit log and included in evidence packs.

## 3. Why This Reduces Risk
Auto-triage reduces operational risk by ensuring that critical incidents (hallucinations, policy violations, high-risk systems) are immediately escalated to Compliance. It prevents delays, removes inconsistency, and ensures every incident is handled according to documented policy.

## 4. Why This Speeds Response
The system eliminates manual triage steps. As soon as an incident is created, it is assigned to the correct queue with a suggested root cause and severity. This accelerates investigation and reduces time-to-mitigation.

## 5. Evidence Collected
- Triage suggestion in Swagger (incident creation response).
- Queue results for Compliance and AI Owner.
- Audit log entries for triage suggestion and assignment.
