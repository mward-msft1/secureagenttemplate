# Configuration Reference

This document describes every environment variable recognised by the
secure-agent-template, the scope of each setting, and least-privilege
guidance.

---

## Variable reference

### Azure Identity (required)

| Variable | Required | Description |
|---|---|---|
| `AZURE_TENANT_ID` | ✅ | Azure AD / Entra tenant GUID |
| `AZURE_CLIENT_ID` | ✅ | Service principal (app registration) client ID |
| `AZURE_CLIENT_SECRET` | ✅ | Service principal client secret – rotate every 90 days |

### Purview (required)

| Variable | Required | Description |
|---|---|---|
| `PURVIEW_ENDPOINT` | ✅ | Fully qualified endpoint, e.g. `https://<name>.purview.azure.com` |
| `PURVIEW_ACCOUNT_NAME` | ✅ | Short Purview account name |

### Microsoft Graph / A365 (optional with defaults)

| Variable | Default | Description |
|---|---|---|
| `GRAPH_API_ENDPOINT` | `https://graph.microsoft.com/v1.0` | Graph base URL; override only for sovereign clouds |
| `GRAPH_SCOPES` | `https://graph.microsoft.com/.default` | Comma-separated OAuth scopes |

### Entra ID (optional with defaults)

| Variable | Default | Description |
|---|---|---|
| `AZURE_AUTHORITY_HOST` | `https://login.microsoftonline.com` | Auth authority; change for US Gov / China clouds |

### Runtime (optional with defaults)

| Variable | Default | Description |
|---|---|---|
| `LOG_LEVEL` | `INFO` | Python log level: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `LOG_JSON` | `false` | Emit structured JSON logs (recommended for production) |
| `LOG_MASK_SENSITIVE` | `true` | Redact sensitive fields in log output |
| `MOCK_SDK_CALLS` | `false` | Skip real Azure calls; return mock data (local dev only) |

---

## Local development vs production secret management

### Local development

1. Copy `.env.example` to `.env`.
2. Fill in real or test credentials.
3. `.env` is in `.gitignore`; **never commit it**.

### Production / CI

Do **not** use `.env` files in production. Instead:

- **Azure Key Vault + Managed Identity** (recommended):
  Use `DefaultAzureCredential` which automatically picks up Managed Identity
  in Azure-hosted environments (AKS, App Service, Azure Functions).
  Store secrets in Key Vault and reference them via environment variable
  injection or Key Vault references in App Service configuration.

- **GitHub Actions secrets** (for CI/CD):
  Store `AZURE_TENANT_ID`, `AZURE_CLIENT_ID`, `AZURE_CLIENT_SECRET` as
  repository secrets in GitHub.  Reference them in workflow files:
  ```yaml
  env:
    AZURE_TENANT_ID: ${{ secrets.AZURE_TENANT_ID }}
  ```

- **Kubernetes Secrets / External Secrets Operator**:
  Sync Key Vault secrets to Kubernetes Secrets and project them as
  environment variables into the pod.

---

## Least-privilege RBAC guidance

### Purview roles (assign at the Purview account or collection level)

| Role | Purpose |
|---|---|
| **Data Reader** | Read catalog entities, glossaries, lineage (read-only) |
| **Data Curator** | Create and edit catalog entities, classifications |
| **Data Source Admin** | Register data sources, trigger scans |
| **Collection Admin** | Manage collections and role assignments |

Assign only the role(s) your agent's use case requires.
Prefer collection-scoped assignments over account-level assignments.

### Microsoft Graph application permissions (admin-consent required)

| Permission | Purpose |
|---|---|
| `User.Read.All` | List or read all users |
| `Group.Read.All` | List groups and memberships |
| `Mail.Read` | Read mail metadata |
| `Sites.Read.All` | Read SharePoint sites |
| `Files.Read.All` | Read OneDrive / SharePoint files |
| `Directory.Read.All` | Read all directory objects (users, groups, apps) |

Do **not** grant `*.ReadWrite.All` permissions unless your agent must
modify data.

### Entra ID roles (via Azure RBAC or App role assignments)

| Role | Purpose |
|---|---|
| **Directory Readers** | Read all directory objects |
| **Global Reader** | Read-only access across all admin centres |

Avoid `Global Administrator` or `Directory Writers` unless strictly required.
