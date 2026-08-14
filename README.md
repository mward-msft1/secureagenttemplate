# Secure Agent Template

> A production-minded, customer-ready starter for AI agents that integrate
> **Microsoft Purview**, **Microsoft 365 (A365 / Graph API)**, and
> **Microsoft Entra ID** using the official Azure Python SDKs.

---

## Table of Contents

1. [What This Template Is For](#what-this-template-is-for)
2. [Architecture Overview](#architecture-overview)
3. [Prerequisites](#prerequisites)
4. [Setup Steps](#setup-steps)
5. [How to Run Locally](#how-to-run-locally)
6. [How to Add New Tools / Skills / Plugins](#how-to-add-new-tools--skills--plugins)
7. [Security Considerations](#security-considerations)
8. [Troubleshooting](#troubleshooting)
9. [SDK Auto-Update Mechanism](#sdk-auto-update-mechanism)
10. [Contributing](#contributing)

---

## What This Template Is For

This repository gives your team a clean, opinionated starting point for
building AI agents that need to:

- **Govern data** via [Microsoft Purview](https://learn.microsoft.com/purview/)
  (catalog, scanning, lineage, classification).
- **Interact with Microsoft 365** workloads (users, groups, mail, SharePoint,
  Teams) through the
  [Microsoft Graph API](https://learn.microsoft.com/graph/overview).
- **Manage or validate identities** using
  [Microsoft Entra ID](https://learn.microsoft.com/entra/fundamentals/)
  (directory objects, groups, role assignments, token validation).

Clone it, fill in your Azure credentials, and extend the adapter modules
with the specific Graph resources or Purview operations your scenario requires.

---

## Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│                  AgentOrchestrator                        │
│  (src/agent.py)                                           │
│                                                           │
│  ┌──────────────┐  ┌───────────────┐  ┌───────────────┐  │
│  │ PurviewAdapter│  │  A365Adapter  │  │  EntraAdapter │  │
│  │(src/adapters/ │  │(src/adapters/ │  │(src/adapters/ │  │
│  │  purview.py)  │  │   a365.py)    │  │   entra.py)   │  │
│  └──────┬───────┘  └───────┬───────┘  └───────┬───────┘  │
└─────────┼─────────────────┼──────────────────┼───────────┘
          │                 │                  │
          ▼                 ▼                  ▼
  Purview Catalog /   Microsoft Graph    Microsoft Graph
  Scanning SDKs       (M365 resources)   (Entra resources)
```

All three adapters share a single `AgentSettings` object (loaded from
environment variables) and a shared `azure-identity` credential chain.

---

## Prerequisites

| Requirement | Version / Notes |
|---|---|
| Python | 3.11 or later |
| pip | Latest recommended |
| Azure subscription | With Purview account provisioned |
| App registration | Service principal with required permissions (see below) |
| Microsoft 365 tenant | For Graph/A365 operations |

### Required Azure permissions for the service principal

| Service | Minimum Role / Permission |
|---|---|
| Purview | Data Reader (catalog read-only) or Data Curator (read/write) |
| Microsoft Graph | User.Read.All, Group.Read.All, Sites.Read.All (adjust to your needs) |
| Entra ID | Directory.Read.All, RoleManagement.Read.All |

> **Least-privilege principle:** Grant only the permissions your specific use
> case requires. The table above lists the minimum for the sample flow.

---

## Setup Steps

### 1. Clone the repository

```bash
git clone https://github.com/mward-msft1/secureagenttemplate.git
cd secureagenttemplate
```

### 2. Create a virtual environment and install dependencies

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Or install as a package in editable mode:
pip install -e ".[dev]"
```

### 3. Configure environment variables

```bash
cp .env.example .env
# Edit .env and fill in your Azure credentials and endpoints.
# NEVER commit .env to source control – it is in .gitignore.
```

See [docs/configuration.md](docs/configuration.md) for a detailed
description of every variable and least-privilege guidance.

### 4. Verify the installation

```bash
python -m pytest tests/ -v
```

All tests run in **mock mode** by default and require no Azure credentials.

---

## How to Run Locally

```bash
# Activate your virtual environment first
source .venv/bin/activate

# Run the sample agent flow (real SDK calls, requires .env to be populated)
python -m src.agent

# Run with mock SDK calls (no Azure credentials required)
MOCK_SDK_CALLS=true python -m src.agent

# Using the installed console script
run-agent
```

The sample flow:
1. Lists Entra groups in your tenant.
2. Lists Microsoft 365 users via the Graph API.
3. Lists registered Purview data sources.

---

## How to Add New Tools / Skills / Plugins

### Adding a new adapter method

Open the relevant adapter file (`src/adapters/purview.py`,
`src/adapters/a365.py`, or `src/adapters/entra.py`) and add a new method
following the existing patterns:

```python
def get_my_resource(self, resource_id: str) -> dict:
    logger.info("Fetching resource", id=resource_id)
    try:
        result = self._client.<sdk_call>(resource_id)
        return result
    except Exception as exc:
        logger.error("Failed to fetch resource", id=resource_id, error=str(exc))
        raise
```

Add a corresponding mock in the `_Mock*Client` class at the top of the file
and a test in `tests/test_adapters.py`.

### Integrating with an agent framework

`AgentOrchestrator` is framework-agnostic. To use it with popular frameworks:

**LangChain:**
```python
from langchain.tools import tool
from src.agent import AgentOrchestrator
from src.config import load_settings

orchestrator = AgentOrchestrator(load_settings())

@tool
async def list_purview_sources() -> str:
    sources = orchestrator.purview.list_data_sources()
    return str(sources)
```

**Semantic Kernel:**
```python
import semantic_kernel as sk
from src.adapters.purview import PurviewAdapter
from src.config import load_settings

kernel = sk.Kernel()
# Register PurviewAdapter methods as native functions
```

---

## Security Considerations

### Token handling
- Credentials are loaded exclusively from environment variables.
- Use **Azure Key Vault** + **Managed Identity** in production instead of
  storing secrets in `.env` files.
- Tokens obtained via `azure-identity` are cached and refreshed automatically;
  do not log or persist them manually.

### RBAC
- Create a dedicated service principal for this agent with the minimum
  required permissions (see Prerequisites above).
- Scope Purview roles to specific collections rather than the root account
  where possible.
- For Graph, prefer application permissions with admin consent over delegated
  permissions unless user-context is required.

### Secret rotation
- Rotate `AZURE_CLIENT_SECRET` regularly (90-day maximum recommended).
- Use `azure-identity`'s `ManagedIdentityCredential` (no secret) for
  workloads running in Azure (AKS, App Service, Azure Functions).

### PII / sensitive data logging
- `LOG_MASK_SENSITIVE=true` (the default) instructs the logging layer to
  redact known sensitive fields.
- Never log full token strings, client secrets, or personally identifiable
  information (email, phone, national IDs) in production log streams.
- Use Azure Monitor / Microsoft Sentinel for production log aggregation;
  apply data-masking rules at the pipeline level.

### Supply chain
- Pin dependency versions in `requirements.txt` for reproducible builds.
- Run `pip-audit` or Dependabot to detect known vulnerabilities in
  dependencies.
- The `sdk-watch` GitHub Actions workflow automatically tracks new SDK
  versions and opens a PR when updates are available.

---

## Troubleshooting

| Symptom | Likely cause | Resolution |
|---|---|---|
| `ValidationError: field required` | Missing env var | Check `.env` against `.env.example`; ensure all required fields are set |
| `ClientAuthenticationError` | Wrong credentials | Verify `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` |
| `HttpResponseError 403` | Insufficient permissions | Review the Required Azure Permissions table above |
| `ModuleNotFoundError: azure.purview.catalog` | Dependencies not installed | Run `pip install -r requirements.txt` |
| Graph calls return empty `value` | Insufficient Graph permission | Add the required permission in the App Registration → API permissions |
| Tests fail with `ImportError` | Missing dev dependencies | Run `pip install -e ".[dev]"` |

---

## SDK Auto-Update Mechanism

A scheduled GitHub Actions workflow (`.github/workflows/sdk-watch.yml`) runs
daily and:

1. Checks PyPI for the latest versions of `azure-purview-catalog`,
   `msgraph-sdk`, and `azure-identity`.
2. Compares with the tracked versions in `sdk-versions.json`.
3. If any version has changed, updates `sdk-versions.json` and
   `docs/sdk-updates.md`, then opens a pull request.

You can also run the checker locally:

```bash
python scripts/check_sdk_updates.py
```

See [docs/sdk-updates.md](docs/sdk-updates.md) for update history.

---

## Contributing

1. Create a feature branch from `main`.
2. Add or update tests in `tests/`.
3. Run `pytest tests/ -v` to confirm everything passes.
4. Open a pull request with a clear description of the change.

---

## Engineering Reference (Internal)

This section contains internal engineering guidance for contributors and delivery teams.

### Engineering objectives

1. **Composable adapter architecture** for Purview/A365/Entra integrations.
2. **Secure-by-default auth and config** (no embedded secrets, principle of least privilege).
3. **Operational readiness** (structured logs, deterministic error handling, CI automation).
4. **SDK drift management** (automated update checks + PR-based update flow).
5. **Customer handoff quality** (clear extension points and override mechanics).

---

### Adapter contract

Each SDK adapter implements a consistent pattern:

- Constructor receives `AgentSettings`; builds the SDK client (or mock).
- Methods are granular (one operation per method) with structured logging on entry and error.
- All public methods use typed return values (`dict[str, Any]` or `list[dict[str, Any]]`).
- Errors are re-raised after logging; callers decide on retry strategy.

---

### Error handling strategy

Normalize all failures — log with `logger.error(...)`, include `error=str(exc)`, and re-raise.
Callers or framework layers map adapter errors to domain errors as needed.

Suggested taxonomy for wrapping exceptions:
- `AuthError` — `ClientAuthenticationError` from azure-identity
- `PermissionError` — HTTP 403 from Graph / Purview
- `ValidationError` — bad config / missing env vars
- `ExternalServiceError` — non-retryable SDK errors
- `TransientDependencyError` — 429 / 503 / network timeout

---

### CI/CD expectations

Minimum CI steps:
1. `pip install -e ".[dev]"`
2. `ruff check src/ tests/`
3. `python -m pytest tests/ -v`

---

### Security requirements checklist

- [ ] No secrets committed to source control.
- [ ] `.env.example` contains placeholders only.
- [ ] Scopes/roles documented and least-privilege validated.
- [ ] Token and PII redaction tested.
- [ ] Dependency update policy defined (`pip-audit` / Dependabot).

### Customer handoff checklist

Before sending to a customer:

- [ ] Replace placeholder setup commands with runtime-specific commands.
- [ ] Confirm adapter methods map to customer use cases.
- [ ] Confirm Entra app registration instructions are accurate.
- [ ] Validate required permissions and consent path.
- [ ] Validate SDK update workflow runs in customer fork/org.
- [ ] Add organization-specific compliance statements.

---

### Contribution standards

- Keep adapter APIs backward compatible where possible.
- Prefer additive changes and feature flags over breaking changes.
- Require tests for auth scope resolution, error normalization, and update checker parsing.
- Every integration change must update the matching `docs/integrations/*.md`.
