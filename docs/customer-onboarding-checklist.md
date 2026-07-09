# Customer Onboarding Checklist (Copy/Paste)

Use this checklist during customer onboarding to quickly stand up governed first-party and third-party agents with Entra, Purview, and A365 integration.

---

## 1) Tenant + Environment Intake (Copy/Paste)

**Customer name:**  
**Tenant ID:**  
**Environment:** Dev / Test / Prod  
**Primary region:**  
**Data residency requirements:**  
**Compliance baseline:** (e.g., ISO, SOC, HIPAA, GDPR, internal policy)  
**Security contact:**  
**Operations contact:**  
**Incident contact:**  

---

## 2) Agent Registration Intake (First-Party and Third-Party)

### Agent identity
- [ ] Agent name
- [ ] Agent owner team
- [ ] Agent support owner
- [ ] Business purpose / use case
- [ ] Agent classification: **First-party / Third-party / Marketplace**
- [ ] Criticality: Low / Medium / High

### Third-party specifics (required when applicable)
- [ ] Vendor name
- [ ] Vendor service URL(s)
- [ ] Vendor trust documentation received (security whitepaper, SOC report, etc.)
- [ ] Contractual controls validated (data processing terms, breach notification, retention)
- [ ] Model/provider details captured (if AI model is vendor-hosted)
- [ ] Sub-processor list reviewed
- [ ] Cross-border data transfer review completed

---

## 3) Entra Governance Setup

### App registration / service principal
- [ ] Create dedicated app registration per agent (no shared app across unrelated agents)
- [ ] Create service principal in tenant
- [ ] Assign owner(s) to app registration
- [ ] Store app metadata in CMDB/inventory

### Authentication model
- [ ] Preferred: Managed identity / workload identity federation
- [ ] If client secret used, set short rotation window and expiry alerts
- [ ] Certificate-based auth configured where supported
- [ ] Token lifetime/refresh strategy validated

### Permission governance
- [ ] Required API permissions documented by operation
- [ ] Least-privilege scopes only
- [ ] Admin consent approval workflow completed
- [ ] Privileged role assignments reviewed and time-bound
- [ ] Access reviews scheduled

### Conditional access / access control
- [ ] Conditional Access policies applied to app/service principal where supported
- [ ] Named locations/network controls validated
- [ ] Break-glass path documented and tested

---

## 4) Purview Governance Setup

### Data map and catalog alignment
- [ ] Data sources used by agent identified
- [ ] Collections and access boundaries defined
- [ ] Data owners/stewards identified

### Classification and sensitivity
- [ ] Required sensitivity labels identified
- [ ] Required classification tags identified
- [ ] Policy for restricted/sensitive classes documented
- [ ] Test queries confirm correct classifications visible to agent

### Lineage and auditability
- [ ] Lineage requirements defined (source → transformation → output)
- [ ] Agent-generated assets/outputs discoverable in governance process
- [ ] Retention and evidence requirements documented

---

## 5) A365 Integration Controls

- [ ] Runtime endpoints allowlisted
- [ ] Tool/plugin execution policy defined (allowed tools only)
- [ ] Notification and event routing controls configured
- [ ] Session/activity correlation IDs enabled
- [ ] Safety filters and prompt guardrails enabled
- [ ] Fallback/timeout/retry behavior configured

---

## 6) Third-Party Agent Governance Controls (Required)

Use this section for any non-native or external agent integration.

### Approval gate
- [ ] Third-party agent risk review completed
- [ ] Security architecture review approved
- [ ] Legal/procurement review complete
- [ ] Data protection impact review complete (if required)

### Data boundary controls
- [ ] Explicit list of data the agent can access
- [ ] Explicit list of data the agent cannot access
- [ ] Redaction policy enforced before outbound calls
- [ ] PII/secrets/token stripping verified
- [ ] Content filtering policy applied to inputs and outputs

### Identity + trust controls
- [ ] Third-party calls authenticated with dedicated credential
- [ ] Credentials isolated per environment and per agent
- [ ] Outbound destination allowlist enforced
- [ ] mTLS/signature verification enabled where supported
- [ ] Replay protection / nonce / timestamp checks applied (if supported)

### Monitoring + kill switch
- [ ] Third-party agent events logged with correlation ID
- [ ] Security alerts defined for abnormal behavior
- [ ] Cost/usage thresholds configured
- [ ] Immediate disable/kill switch documented and tested
- [ ] Incident runbook includes vendor escalation contacts

### Ongoing assurance
- [ ] Quarterly permission revalidation scheduled
- [ ] Quarterly vendor trust posture review scheduled
- [ ] SDK/API version drift review enabled
- [ ] Evidence artifacts stored for audit

---

## 7) Required Environment Variables (Quick Fill)

```dotenv
# Core
AGENT_NAME=
AGENT_ENV=dev
LOG_LEVEL=info
LOG_FORMAT=json
REQUEST_TIMEOUT_MS=30000

# Entra
ENTRA_TENANT_ID=
ENTRA_CLIENT_ID=
ENTRA_CLIENT_SECRET=
ENTRA_AUTHORITY_HOST=https://login.microsoftonline.com
GRAPH_BASE_URL=https://graph.microsoft.com/v1.0
GRAPH_SCOPES=https://graph.microsoft.com/.default

# Purview
PURVIEW_ENABLED=true
PURVIEW_ENDPOINT=
PURVIEW_API_VERSION=2023-09-01
PURVIEW_SCOPES=https://purview.azure.net/.default

# A365
A365_ENABLED=true
A365_SDK_LANGUAGE=dotnet
A365_SDK_PACKAGE_PREFIX=Microsoft.Agents.A365
A365_SDK_SOURCE=

# Security
SECURITY_REDACT_PII=true
SECURITY_REDACT_TOKENS=true
SECURITY_BLOCK_UNSCOPED_CALLS=true

# Third-party governance (recommended additions)
THIRDPARTY_AGENT_ENABLED=false
THIRDPARTY_AGENT_NAME=
THIRDPARTY_AGENT_VENDOR=
THIRDPARTY_AGENT_BASE_URL=
THIRDPARTY_AGENT_ALLOWED_OPERATIONS=
THIRDPARTY_AGENT_DATA_ALLOWLIST=
THIRDPARTY_AGENT_DATA_DENYLIST=
THIRDPARTY_AGENT_EGRESS_ALLOWLIST=
THIRDPARTY_AGENT_TIMEOUT_MS=20000
THIRDPARTY_AGENT_RETRY_MAX=2
THIRDPARTY_AGENT_KILL_SWITCH=true
```

---

## 8) Pre-Go-Live Validation

- [ ] Unit tests passed
- [ ] Integration tests passed in non-prod tenant
- [ ] Permission tests confirm least privilege
- [ ] Redaction tests confirm no secrets/PII leakage in logs
- [ ] Third-party denylist tests passed
- [ ] Kill switch tested
- [ ] Monitoring dashboards and alerts live
- [ ] Runbooks approved by Security + Operations

---

## 9) Operational Handoff

- [ ] Support team trained
- [ ] Escalation matrix published
- [ ] SLA/SLO agreed
- [ ] Rotation schedule for secrets/certs in place
- [ ] Monthly governance review meeting scheduled

---

## 10) Copy/Paste Customer Sign-Off

**We confirm the following before production enablement:**
- least-privilege permissions are implemented,
- third-party agent controls are enabled and tested,
- sensitive data protections are enforced,
- monitoring and incident response are operational.

**Customer approver:**  
**Security approver:**  
**Platform approver:**  
**Date:**  
