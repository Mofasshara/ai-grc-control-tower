# Week 04 Summary -- Prompt & RAG Governance

## Overview
Week 4 implemented full governance for prompts and RAG sources:
- Versioning
- Diffs
- Hash integrity
- Change control integration
- Activation gates
- Time-bounded bindings
- Audit logging

## Key Controls

### 1. No prompt/RAG change without approved change request
All versions must be linked to a change request.
Activation requires APPROVED status.

### 2. Active versions are time-bounded
Binding tables record:
- active_from
- active_to
- activated_by
- change_request_id

This enables full reconstruction of AI behavior at any point in time.

### 3. Hashes enable integrity verification
Each version stores a SHA-256 hash of:
- prompt text or URI
- ingestion config
- embedding config

This ensures tamper-evident traceability.

## Evidence Collected
Stored in `/evidence/week_04/`:
- Prompt version list
- RAG version list
- Unified diffs
- Change request approvals
- Activation events
- Audit log entries

## Conclusion
Week 4 delivered regulator-grade governance for all AI behavior-shaping artifacts.
Prompts and RAG sources are now fully controlled, versioned, approved, and auditable.
