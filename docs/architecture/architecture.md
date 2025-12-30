# AI-GRC Architecture Notes

## Why the Backend is Authoritative
The FastAPI backend is the single source of truth for all AI governance operations. 
All metadata, change requests, approvals, incidents, and evidence generation 
requests must pass through the backend. This ensures:
- Centralized control
- Enforced validation rules
- Consistent audit logging
- No bypass of governance workflows

## Why Evidence is Immutable
Evidence is written to Azure Blob Storage using append-only, timestamped, 
and hashed artifacts. Once generated, evidence cannot be modified or deleted. 
This guarantees:
- Regulatory defensibility
- Chain-of-custody integrity
- Non-repudiation for audits
- Full traceability of all AI lifecycle events

## Why AI is Advisory Only
Azure OpenAI is used only for:
- Summaries
- Drafts
- Recommendations

It never makes final decisions. All outputs require:
- Human-in-the-loop review
- Compliance approval
- Logging and traceability

This ensures the system aligns with FINMA, GxP, and CSV expectations for 
controlled AI usage in regulated environments.

## Purpose of This Architecture
This architecture demonstrates:
- Clear separation of duties
- Strong governance boundaries
- Immutable evidence generation
- Controlled AI usage
- Enterprise-grade auditability

It proves systems thinking, not tool usage.
