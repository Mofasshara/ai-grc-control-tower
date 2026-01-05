# Data Governance Policy

## 1. Purpose
This document defines the data classes used in the AI-GRC Control Tower and establishes retention rules aligned with FINMA, GxP, and general audit expectations. Not all data carries the same regulatory weight; therefore, classification ensures appropriate protection, retention, and auditability.

## 2. Data Classification Levels

### A. Metadata (Low Risk)
Examples:
- AI system names
- Prompt version numbers
- RAG source identifiers
- Timestamps
- Non-sensitive configuration values

Why low risk:
- Contains no personal data
- No operational or regulatory sensitivity
- Used for indexing and linking only

Controls:
- Standard access controls
- No special retention requirements

### B. Logs (Medium Risk)
Examples:
- API access logs
- Audit logs
- Change logs
- System events

Why medium risk:
- May contain user IDs or system identifiers
- Required for audit trails
- Must be tamper-proof

Controls:
- Append-only
- Integrity protection
- 7-year retention

### C. Evidence Packs (Regulated)
Examples:
- Release evidence ZIPs
- Hash manifests
- Traceability matrices
- Approval metadata
- PDF summaries

Why regulated:
- Required for audits
- Must be immutable
- Must be retained long-term
- Supports regulatory investigations

Controls:
- Stored in secure Blob Storage
- Versioned
- Immutable
- 7–10 year retention

### D. Incident Data (Regulated)
Examples:
- Hallucination reports
- Bias incidents
- Safety incidents
- Severity classifications
- Root-cause analysis

Why regulated:
- Directly tied to AI risk
- Required for compliance reporting
- Must be available for regulators

Controls:
- Strict RBAC
- 7-year retention
- Must be linked to evidence packs

## Simple explanation
Not all data is equal.
Regulators care deeply about audit logs, incidents, and evidence packs, but not about simple metadata.

## 3. Data Retention Requirements

Data Type | Retention Requirement | Rationale
--- | --- | ---
Audit logs | 7 years | Required for financial & GxP audits
Evidence packs | 7–10 years | Supports regulatory investigations & release traceability
Prompt versions | Lifecycle of the AI system | Needed for reproducibility & drift analysis
Incidents | 7 years | Required for risk reporting & compliance reviews

## 4. Retention Rationale (Explain to Auditors)

Audit Logs — 7 Years
Matches FINMA and GxP expectations

Required for traceability of decisions

Must be immutable

Evidence Packs — 7–10 Years
Releases must be reproducible

Investigations may occur years later

Evidence must remain accessible

Prompt Versions — Lifecycle
Needed to reproduce model behavior

Supports drift analysis

Required for AI explainability

Incidents — 7 Years
Required for risk trend analysis

Supports regulatory reporting

Must be linked to change history

## 5. Privacy Controls and GDPR Awareness

### Personal Data Marker
The field `contains_personal_data` indicates whether a record includes personal data subject to GDPR. This flag enables future privacy workflows without violating audit retention requirements.

**Purpose:**
In regulated industries (banking, pharmaceuticals), audit evidence **must be retained** for compliance purposes, even when GDPR "right to deletion" requests occur. This creates a conflict between GDPR Article 17 (right to erasure) and regulatory retention requirements.

**Resolution:**
The `contains_personal_data` flag implements a **marker-based approach** that:
1. ✅ **Identifies** which records contain personal data
2. ✅ **Enables** future privacy workflows (pseudonymization, anonymization)
3. ✅ **Preserves** audit integrity and regulatory compliance
4. ✅ **Does NOT** delete regulated evidence (compliant with FDA, EMA, FINMA retention requirements)

**Implementation:**
- **AI Incidents** (`ai_incidents.contains_personal_data`): Boolean flag, default `false`
- **Change Requests** (`change_requests.contains_personal_data`): Boolean flag, default `false`

When personal data (names, emails, IP addresses) is present in descriptions, set this flag to `true`.

**Future Privacy Workflows:**
- Data Subject Access Requests (DSAR) automation
- Pseudonymization of flagged records
- Privacy impact assessments
- Restricted access to sensitive data

This approach shows **GDPR awareness** while maintaining **regulatory compliance** with audit retention laws.
