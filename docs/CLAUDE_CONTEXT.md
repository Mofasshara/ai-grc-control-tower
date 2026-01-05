# AI-GRC Control Tower - Claude Code Context

**Last Updated**: 2026-01-04
**Project Status**: Active Development - Week 6+
**Deployment**: Azure App Service (Switzerland North)

---

## 🎯 Project Overview

### Purpose
Production-grade, audit-ready AI Governance, Risk & Compliance Control Tower targeting Swiss banking (FINMA) and pharma (GxP/CSV/EMA/FDA) industries.

### Business Problem
Organizations deploying AI/GenAI systems need:
- **Regulator-first compliance**: Generate audit evidence packs on demand
- **AI risk management**: Track models, prompts, RAG sources across lifecycle
- **Incident & change tracking**: Full traceability of modifications
- **Role-based governance**: Auditors, compliance officers, AI owners, admins

### Target Users
1. **Auditors** (FINMA, GxP, internal): View-only access, download evidence packs
2. **Compliance Officers**: Approve changes, manage risks, generate reports
3. **AI System Owners**: Submit change requests, track incidents
4. **Admins**: Full system access, user management

### Portfolio Context
This is NOT a demo - it's a senior-level portfolio project for:
- Target roles: AI/GenAI Tech Lead, AI Product Manager (Switzerland)
- Industries: Swiss Banking, Pharma/Life Sciences
- Time commitment: 3 hours/day, 10-12 weeks
- Goal: Prove production-grade capabilities to recruiters

---

## 🏗️ Technical Architecture

### Tech Stack
- **Backend**: Python 3.14, FastAPI, SQLAlchemy, Alembic
- **Database**: Azure PostgreSQL Flexible Server (Switzerland North)
- **Authentication**: Azure Easy Auth (Azure AD) + JWT fallback
- **Deployment**: GitHub Actions → Azure App Service (Linux)
- **Infrastructure**: Azure (EU/Switzerland data residency)

### Key Components
```
backend/
├── main.py              # FastAPI app, health endpoint, audit middleware
├── database.py          # SQLAlchemy engine, Managed Identity support
├── models.py            # ORM models (AuditLog, AISystem, ChangeRequest, etc.)
├── security/
│   ├── auth.py         # Authentication (Easy Auth + JWT + mock mode)
│   └── roles.py        # Role-based access control (RBAC)
├── routers/
│   ├── ai_system.py    # AI system CRUD, lifecycle management
│   ├── change_request.py  # Change request workflow
│   ├── prompt.py       # Prompt versioning
│   ├── rag.py          # RAG source management
│   └── incidents.py    # Incident tracking
├── evidence/
│   └── generator.py    # Evidence pack generation (PDF/ZIP)
├── alembic/            # Database migrations
└── requirements.txt    # Python dependencies
```

### Current State (as of 2026-01-04)
- ✅ FastAPI backend with audit middleware
- ✅ PostgreSQL database with Alembic migrations
- ✅ Easy Auth (Azure AD) configured with /health exclusion
- ✅ Role-based access control (5 roles)
- ✅ Evidence pack generation (PDF with hashing)
- ✅ GitHub Actions CI/CD pipeline
- ✅ Azure App Service deployment (backend as app root)
- ⏳ Network hardening in progress (IP restrictions, firewall rules)

---

## 🔐 Authentication & Authorization

### Authentication Layers
1. **Easy Auth (Azure AD)** - Primary authentication layer
   - Enabled at App Service level
   - Redirects unauthenticated users to Azure AD login
   - Injects `X-MS-TOKEN-AAD-ID-TOKEN` header
   - **EXCLUDED PATHS**: `/health` (for monitoring)

2. **JWT Token Validation** - Fallback for direct API calls
   - Validates Bearer tokens from Authorization header
   - Extracts user claims (oid, preferred_username, roles)

3. **Mock Mode** - Local development only
   - Activated via `AUTH_MODE=mock` environment variable
   - Returns mock admin user
   - **NEVER use in production!**

### Role Mapping (Azure AD → App Roles)
```python
APP_ROLE_MAP = {
    "auditor": Role.AUDITOR,        # View-only, download evidence
    "compliance": Role.COMPLIANCE,  # Approve changes, manage risks
    "ai_owner": Role.AI_OWNER,      # Submit changes, track incidents
    "admin": Role.ADMIN             # Full access
}
```

### Security Event Logging
All authentication events logged to `audit_security.log`:
- `login_success`: User authenticated successfully
- `login_failed`: Invalid token or missing credentials
- `unauthorized_access`: User attempted forbidden action

---

## 🗄️ Database Configuration

### Connection Modes

#### Password Authentication (Current)
```bash
DATABASE_URL=postgresql://aigrcadmin:Dad1006*@ai-grc-postgres-dev.postgres.database.azure.com:5432/postgres?sslmode=require
MANAGED_IDENTITY_ENABLED=false
```

#### Managed Identity Authentication (Future)
```bash
DATABASE_URL=postgresql://aigrcadmin@ai-grc-postgres-dev.postgres.database.azure.com:5432/postgres?sslmode=require
MANAGED_IDENTITY_ENABLED=true
AZURE_PG_SCOPE=https://ossrdbms-aad.database.windows.net/.default
```

**NOTE**: Managed Identity requires:
1. System-assigned identity enabled on App Service
2. PostgreSQL user created for the Managed Identity principal
3. Proper permissions granted in PostgreSQL

### Database Security (Current)
- **Public Access**: Enabled (required for App Service connectivity)
- **Firewall Rules**:
  - `AllowAzureServices` (0.0.0.0) - Allows Azure services
  - 13 App Service outbound IP rules
  - Optional: Your workstation IP for debugging

---

## 🚀 Deployment Architecture

### GitHub Actions Workflow
**File**: `.github/workflows/main_ai-grc-api-dev.yml`

#### Build Stage
```yaml
working-directory: backend      # ← CRITICAL: Build from backend/
run: |
  python -m venv antenv
  source antenv/bin/activate
  pip install -r requirements.txt
```

#### Artifact Upload
```yaml
path: |
  backend/**                    # ← Upload backend folder contents
  !backend/antenv/**            # Exclude virtual environment
```

#### Deploy Stage
```yaml
package: backend                # ← Deploy backend as app root
```

**Result**: Backend folder deployed to `/home/site/wwwroot/` on Azure

### Azure App Service Configuration

#### Runtime
- **Linux FX Version**: `PYTHON|3.14`
- **Startup Command**: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`
- **Working Directory**: `/home/site/wwwroot/` (backend deployed here)

#### App Settings
```bash
# Database
DATABASE_URL=postgresql://aigrcadmin:Dad1006%2A@...
MANAGED_IDENTITY_ENABLED=false

# Authentication
AUTH_MODE=mock  # TODO: Remove before production!
AZURE_CLIENT_ID=318660b2-89c3-429c-9701-dad460fd08c9
AZURE_TENANT_ID=e81b3391-9450-4ff7-b799-760c4a52c82e

# Environment
ENV=dev
WEBSITES_PORT=8000
SCM_DO_BUILD_DURING_DEPLOYMENT=1  # Oryx build enabled

# Monitoring
APPLICATIONINSIGHTS_CONNECTION_STRING=...
APPINSIGHTS_INSTRUMENTATIONKEY=...
WEBSITE_HTTPLOGGING_RETENTION_DAYS=3
```

#### Easy Auth Configuration
```json
{
  "platform": {"enabled": true},
  "globalValidation": {
    "requireAuthentication": true,
    "unauthenticatedClientAction": "RedirectToLoginPage",
    "redirectToProvider": "azureActiveDirectory",
    "excludedPaths": ["/health"]
  },
  "identityProviders": {
    "azureActiveDirectory": {
      "enabled": true,
      "registration": {
        "clientId": "318660b2-89c3-429c-9701-dad460fd08c9",
        "openIdIssuer": "https://sts.windows.net/e81b3391-9450-4ff7-b799-760c4a52c82e/v2.0"
      }
    }
  }
}
```

---

## ⚠️ CRITICAL CONSTRAINTS (DO NOT BREAK!)

### 1. Startup Command
```bash
# MUST BE EXACTLY THIS:
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# DO NOT use:
# cd backend && python -m uvicorn main:app  # ← Wrong! Backend is already root
# python main.py                            # ← Wrong! Must use uvicorn
```

**Why**: Backend folder is deployed as `/home/site/wwwroot/`, so main.py is at root level.

### 2. GitHub Workflow Structure
```yaml
# MUST HAVE:
- working-directory: backend      # Build from backend/
- path: backend/**                # Upload backend contents
- package: backend                # Deploy backend as root

# DO NOT:
# - Upload entire repo (path: .)
# - Build from project root
# - Deploy without package parameter
```

**Why**: Maintains local/Azure environment parity and ensures proper dependency installation.

### 3. Easy Auth
```bash
# NEVER disable Easy Auth in production
# ALWAYS keep /health excluded for monitoring
# ALWAYS test with actual Azure AD users before go-live
```

**Why**: Required for FINMA/GxP compliance audit trail.

### 4. Database Migrations
```python
# ALWAYS run migrations on startup (main.py)
# NEVER disable automatic migrations
# ALWAYS use Alembic for schema changes
```

**Why**: Ensures database schema consistency across deployments.

### 5. Audit Logging
```python
# NEVER disable audit middleware
# ALWAYS log to AuditLog table
# ALWAYS include: timestamp, user_id, action, entity, payload_hash
```

**Why**: Core compliance requirement - must prove "who did what when".

---

## 🧪 Testing Procedures

### Local Testing (Before Deployment)
```bash
# 1. Navigate to backend folder
cd backend

# 2. Activate virtual environment
source .venv/bin/activate  # or: python -m venv .venv && source .venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables
export AUTH_MODE=mock
export DATABASE_URL=postgresql://...
export MANAGED_IDENTITY_ENABLED=false

# 5. Start the application
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 6. Test health endpoint (new terminal)
curl http://localhost:8000/health
# Expected: {"status":"ok"}

# 7. Stop the application
pkill -f uvicorn
```

### Pre-Deployment Checklist
- [ ] Local startup command works: `cd backend && python -m uvicorn main:app`
- [ ] Health endpoint returns `{"status":"ok"}`
- [ ] Database migrations run successfully
- [ ] No import errors or missing dependencies
- [ ] GitHub workflow syntax is valid
- [ ] Environment variables are set correctly

### Post-Deployment Verification
```bash
# 1. Wait 3-5 minutes for deployment to complete

# 2. Check health endpoint
curl https://ai-grc-api-dev-h7dchcdad7c6bmdh.switzerlandnorth-01.azurewebsites.net/health

# Expected: {"status":"ok"}
# If 503: Check GitHub Actions logs
# If Application Error: Check Azure App Service logs

# 3. Download and check logs if needed
az webapp log download \
  --name ai-grc-api-dev \
  --resource-group rg-ai-grc-dev \
  --log-file /tmp/app_logs.zip
```

---

## 🐛 Common Issues & Fixes

### Issue 1: Exit Code 127 ("command not found")
**Symptom**: App fails to start with exit code 127 in logs

**Root Cause**: GitHub workflow deploying entire repo instead of backend folder

**Fix**: Ensure workflow has:
```yaml
working-directory: backend
path: backend/**
package: backend
```

**Verification**: Check deployed files at `/home/site/wwwroot/` should contain main.py at root level

---

### Issue 2: Application Error / HTTP 503
**Symptom**: Health endpoint returns Application Error page or 503

**Possible Causes**:
1. **Easy Auth blocking /health**: Add `/health` to `excludedPaths`
2. **Database connection failure**: Check PostgreSQL firewall rules
3. **Missing dependencies**: Verify `requirements.txt` is complete
4. **Startup command wrong**: Verify it matches exactly

**Debug Steps**:
```bash
# 1. Check app status
az webapp show --name ai-grc-api-dev --resource-group rg-ai-grc-dev \
  --query "{state:state, availabilityState:availabilityState}"

# 2. Check startup command
az webapp config show --name ai-grc-api-dev --resource-group rg-ai-grc-dev \
  --query "appCommandLine"

# 3. Download logs
az webapp log download --name ai-grc-api-dev --resource-group rg-ai-grc-dev \
  --log-file /tmp/debug_logs.zip

# 4. Check for exit codes in logs
unzip -q /tmp/debug_logs.zip
grep -r "exit code" tmp/debug_logs/LogFiles/
```

---

### Issue 3: Database Connection Timeout
**Symptom**: App starts but times out connecting to PostgreSQL

**Root Cause**: PostgreSQL firewall blocking App Service outbound IPs

**Fix**: Add firewall rules for all App Service outbound IPs
```bash
# Get outbound IPs
az webapp show --name ai-grc-api-dev --resource-group rg-ai-grc-dev \
  --query "outboundIpAddresses" -o tsv

# Add each IP to PostgreSQL firewall
az postgres flexible-server firewall-rule create \
  --resource-group rg-ai-grc-dev \
  --name ai-grc-postgres-dev \
  --rule-name "webapp-<IP>" \
  --start-ip-address "<IP>" \
  --end-ip-address "<IP>"
```

---

## 📝 Recent Changes & Fixes

### 2026-01-04: GitHub Workflow Fix
**Issue**: Entire repo deployed instead of backend folder, causing exit code 127

**Fix**:
- Added `working-directory: backend` to build step
- Changed artifact upload from `.` to `backend/**`
- Added `package: backend` to deploy step
- Added explicit `path: .` to download artifact step

**Commits**:
- `0f1ebd5`: Fix GitHub Actions workflow to deploy backend folder as app root
- `3465ef9`: Fix artifact download path for deployment

---

### 2026-01-04: Easy Auth /health Exclusion
**Issue**: Health endpoint blocked by authentication, causing monitoring failures

**Fix**: Added `/health` to Easy Auth `excludedPaths`

**Configuration**:
```bash
az webapp auth update --name ai-grc-api-dev --resource-group rg-ai-grc-dev \
  --excluded-paths "/health"
```

---

### 2026-01-05: PostgreSQL Network Hardening (Partial Success)
**Goal**: Restrict PostgreSQL access to only Azure App Service

**Implemented**:
- ✅ Removed dangerous `temp-allow-all` rule (0.0.0.1-255.255.255.254) - eliminated public internet access
- ✅ Kept `AllowAzureServices` rule (0.0.0.0)
- ✅ Kept individual App Service outbound IP rules (13 IPs)

**Lessons Learned**:
- **CRITICAL**: AllowAzureServices (0.0.0.0) alone is NOT sufficient for App Service → PostgreSQL connectivity
- Individual outbound IP firewall rules are REQUIRED for Azure App Service to connect to PostgreSQL Flexible Server
- Removing these rules causes immediate app failure (database connection timeout)

**Not Implemented** (requires infrastructure changes):
- ❌ App Service IP restrictions - would break Easy Auth (Azure AD callbacks come from Microsoft IPs)
- ❌ Disable PostgreSQL public access - requires VNet integration + Private Endpoint

**Current Security Posture**:
- PostgreSQL: Accessible ONLY from Azure services (no public internet access)
- App Service: Protected by Easy Auth (Azure AD authentication required)
- Database: Password authentication (Managed Identity not yet configured)

**Next Steps for Full Hardening**:
1. Set up VNet integration for App Service
2. Create Private Endpoint for PostgreSQL
3. Disable PostgreSQL public access
4. Enable Managed Identity authentication (remove password)

---

## 🔜 Planned Improvements

### Security Hardening (TODO)
1. **App Service Network Restrictions**
   - IP whitelist for authorized users only
   - VNet integration for private connectivity
   - Private endpoints for Azure services

2. **PostgreSQL Security**
   - Disable public access
   - Enable Managed Identity authentication
   - Private Link for database connectivity
   - Remove password-based authentication

3. **Secrets Management**
   - Move from app settings to Azure Key Vault
   - Use Managed Identity to access Key Vault
   - Rotate secrets regularly

### Monitoring & Observability (TODO)
1. **Application Insights**
   - Custom metrics for API endpoints
   - Dependency tracking (database, external APIs)
   - Performance profiling

2. **Alerts**
   - Health endpoint failures
   - Authentication failures spike
   - Database connection errors
   - High latency warnings

### Documentation (TODO)
1. **API Documentation**
   - OpenAPI/Swagger UI at `/docs`
   - Authentication flow examples
   - Role-based endpoint matrix

2. **Runbooks**
   - Incident response procedures
   - Database migration rollback
   - Emergency access procedures

---

## 💡 Development Guidelines

### When Adding New Features
1. **Check existing patterns** in routers/ for consistency
2. **Add audit logging** for all state changes
3. **Implement RBAC** using `@require_roles()` decorator
4. **Write migrations** using Alembic for schema changes
5. **Update this document** with new constraints or patterns

### When Changing Infrastructure
1. **Document current state** before making changes
2. **Test locally first** if possible
3. **Have rollback plan** ready
4. **Update GitHub workflow** if deployment changes
5. **Verify health endpoint** after deployment

### When Debugging Issues
1. **Check logs first**: Azure App Service logs, GitHub Actions logs
2. **Verify environment**: App settings, firewall rules, Easy Auth config
3. **Compare with working state**: Git history, previous deployments
4. **Test locally**: Reproduce issue in local environment if possible
5. **Document solution**: Update this file with issue + fix

---

## 🎯 Success Metrics (Portfolio Goals)

### Technical Excellence
- ✅ Production-grade FastAPI application
- ✅ Complete audit trail (who, what, when)
- ✅ Role-based access control
- ✅ Automated CI/CD pipeline
- ⏳ Network security hardening
- ⏳ Managed Identity authentication
- ⏳ Evidence pack generation with cryptographic hashing

### Recruiter-Facing Proof
- ✅ GitHub repository with clean commit history
- ✅ Working demo endpoint (health check)
- ⏳ Evidence pack samples (redacted)
- ⏳ Architecture diagrams
- ⏳ Demo video (10 minutes)
- ⏳ LinkedIn case study post

### Compliance Readiness
- ✅ Audit logging to database
- ✅ Authentication with Azure AD
- ✅ Role-based access control
- ⏳ Evidence pack generation with timestamps
- ⏳ Traceability matrix
- ⏳ Data retention policy implementation

---

## 📞 Quick Reference

### Azure Resources
- **Resource Group**: `rg-ai-grc-dev`
- **App Service**: `ai-grc-api-dev`
- **PostgreSQL**: `ai-grc-postgres-dev`
- **Region**: Switzerland North
- **Subscription**: 6e9d96f2-cbae-46e1-8317-9f87d809279c

### Endpoints
- **Health**: `https://ai-grc-api-dev-h7dchcdad7c6bmdh.switzerlandnorth-01.azurewebsites.net/health`
- **API Docs**: `https://ai-grc-api-dev-h7dchcdad7c6bmdh.switzerlandnorth-01.azurewebsites.net/docs`
- **SCM/Kudu**: `https://ai-grc-api-dev-h7dchcdad7c6bmdh.scm.switzerlandnorth-01.azurewebsites.net`

### Key Commands
```bash
# Restart app
az webapp restart --name ai-grc-api-dev --resource-group rg-ai-grc-dev

# Download logs
az webapp log download --name ai-grc-api-dev --resource-group rg-ai-grc-dev --log-file /tmp/logs.zip

# Check app settings
az webapp config appsettings list --name ai-grc-api-dev --resource-group rg-ai-grc-dev

# Check PostgreSQL firewall
az postgres flexible-server firewall-rule list --resource-group rg-ai-grc-dev --name ai-grc-postgres-dev
```

---

**Document Maintenance**: Update this file whenever you:
- Add new features or endpoints
- Change deployment configuration
- Fix critical issues
- Update dependencies or infrastructure
- Learn something important about the system

**Last Review**: 2026-01-04 by Claude Code (Sonnet 4.5)
