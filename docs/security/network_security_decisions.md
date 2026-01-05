# Network Security Decisions – AI-GRC Control Tower

## App Service Network Access
- App Service is publicly accessible
- Azure AD Easy Auth is enforced
- IP restrictions are NOT enabled

Reason:
IP restrictions would block:
- Azure AD authentication callbacks
- GitHub Actions deployments
- Azure health probes

Mitigation:
- Identity-first access control (Entra ID)
- Role-based authorization
- Full audit logging

Simple explanation

This answers the auditor’s question:

“Why is this public?”

With a justified, defensible answer.

## PostgreSQL Network Access

Current state:
- Public access enabled (temporary)
- Wide-open firewall rules removed
- Access limited to:
  - Azure services
  - Explicit App Service outbound IPs

Known limitation:
- App Service outbound IPs can change

Planned remediation:
- VNet integration
- Private Endpoint
- Disable public access entirely

