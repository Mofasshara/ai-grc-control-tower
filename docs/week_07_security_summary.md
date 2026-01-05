# Week 7 – Security & Access Control Summary

## Identity & Access
- All users authenticate via Microsoft Entra ID
- Role-based access enforced in application
- No anonymous access permitted

## Network Security
- Database access restricted to Azure services + app IPs
- App Service protected by identity, not IP allowlists

## Secrets Management
- Secrets stored in Azure Key Vault
- App accesses secrets via Managed Identity

## Auditability
- Security-relevant actions logged immutably

Simple explanation

This is what a risk or compliance officer wants to read — not code.

## Deferred Controls

The following controls are planned but not yet implemented:
- VNet integration
- Private Endpoint for PostgreSQL
- Managed Identity DB authentication

Reason:
- Requires App Service Premium tier
- Cost and architecture change justified only after MVP validation

Risk Mitigation:
- Identity-first security
- Narrow firewall rules
- Full audit logging

Target implementation: Week 9+
