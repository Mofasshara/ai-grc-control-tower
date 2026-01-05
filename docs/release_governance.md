# Release Governance Policy

## 1. Purpose of This Document
Release governance exists:
- To ensure every deployment is approved
- To ensure evidence is generated before going live
- To ensure traceability for auditors
- To enforce segregation of duties

This sets the tone for regulators and recruiters.

## 2. What Is a “Release”?
A release is any deployment of the AI-GRC backend or its governed components into a production-like environment.

Examples include:
- Backend API deployment
- Prompt version update
- RAG source update
- Model configuration change
- Policy or guardrail update

This ensures auditors know exactly what counts as a release event.

## 3. Release Approval Requirements
A release must be approved by a human with the Compliance or Admin role.

AI Owners cannot self-approve their own changes.

Automated pipelines cannot approve releases — they only execute them.

This enforces segregation of duties, a core audit principle.

## 4. When Evidence Must Be Generated
Evidence must be generated immediately before deployment, using:

Code
POST /evidence/generate

Evidence must include:
- AI inventory
- Change history
- Prompt & RAG versions
- Incidents
- Traceability matrix
- Hash manifest
- PDF summary

This ensures every release has a frozen snapshot.

## 5. Where Evidence Is Stored
Evidence packs are uploaded to Azure Blob Storage.

Container: evidence-packs

Naming convention:

Code
evidence_<release_version>_<timestamp>.zip

This ensures centralized, immutable storage.

## 6. How Releases Are Audited Later
Each release must have:
- Approval record
- Evidence pack
- Hash manifest
- GitHub commit SHA
- Deployment timestamp

Auditors can request:
- Evidence pack
- Traceability matrix
- Approval logs
- Security logs

This shows you understand audit lifecycle management.

## Release Roles (Segregation of Duties)

### 1. Release Owner
Usually:
- Admin or Compliance

Responsibilities:
- Approves releases
- Ensures evidence is generated
- Confirms risk classification
- Signs off on production deployment

This is the decision-maker.

### 2. Reviewer
Usually:
- Compliance
- Auditor (read-only)
- Senior AI Owner

Responsibilities:
- Reviews change requests
- Reviews evidence
- Ensures no conflicts of interest
- Validates traceability

This is the second pair of eyes.

### 3. Automated Pipeline
This is your GitHub Actions workflow.

Responsibilities:
- Executes deployment
- Generates evidence (trigger only)
- Uploads evidence to Blob Storage
- Creates GitHub Release (optional)

Important:
The pipeline cannot approve anything.
It only executes what humans have approved.

This is a core audit requirement.

## Simple explanation
This document answers the auditor’s favorite question:
“Who decided this version was allowed to go live?”

You’re defining the rules, not the code — and that’s exactly what regulators expect.
