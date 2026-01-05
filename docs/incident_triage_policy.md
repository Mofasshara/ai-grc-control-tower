# Incident Triage Policy

## 1. Purpose
The purpose of this triage policy is to ensure consistent, repeatable, and regulator-aligned classification of AI incidents. Triage decisions must not depend on individual judgment or mood. They must follow a documented, auditable playbook.

## 2. Inputs Used for Triage
The triage process uses system inputs already available in the platform:
- AI System Risk Level (low / medium / high / critical)
- Incident Type (Hallucination, Policy violation, Incorrect factual output, Bias / fairness issue, Unsafe recommendation)
- Incident History (repeated incidents per AI system)
- Drift Signals (prompt drift, RAG drift, incident‑correlated drift)
- Change Volatility (approved changes in last 30 days)
- Severity Scale (Low → Medium → High)

## 3. Core Triage Rules (Simple, Deterministic)

Condition | Suggested Severity | Routing | Rationale
--- | --- | --- | ---
AI system risk = High or Critical AND incident type = Hallucination | High | Compliance | High‑risk system + hallucination = major regulatory concern
Incident type = Policy violation | High | Compliance | Policy breaches must be escalated
Incident type = Incorrect factual output AND AI system risk = Low | Low | AI Owner | Low‑risk system + minor error = operational issue
Repeated incidents (>3 for the same AI system) | Increase severity by 1 level | Compliance | Indicates instability or drift
Drift flag = True AND incident type = Hallucination | High | Compliance | Drift‑linked hallucinations are high‑risk
Severity = High AND change volatility > 10 in 30 days | High | Compliance | High volatility + high severity requires escalation

These rules are simple, explainable, and aligned with the current backend logic.

## 4. Severity Escalation Logic
Severity levels escalate in the following order:
Low → Medium → High

If a rule increases severity by 1 level, it moves to the next level in this sequence.

## 5. Routing Rules
- AI Owner → Low severity, operational issues
- Compliance → High severity, hallucinations, policy violations, drift‑linked incidents
- Admin → Only for system‑level issues
- Auditor → Read‑only, cannot triage

## 6. Human‑in‑the‑Loop Triage Rule

System Recommendation
The system automatically suggests a severity and routing based on the triage rules defined above. These recommendations are generated using incident type, AI system risk level, drift signals, change volatility, and incident history.

Human Override Allowed
Human reviewers (AI Owner or Compliance) may override the system’s suggested severity or routing.

Override Requirements
If an override occurs, the reviewer must provide a written justification. This justification is stored in the audit log and included in the evidence pack.

Why This Matters
This ensures that humans remain accountable for triage decisions, while the system provides consistency and guidance. This aligns with FINMA, GxP, and EU AI Act expectations for human oversight.

## Simple explanation
The system suggests.
Humans decide.
Overrides require justification.
Auditors love this.
