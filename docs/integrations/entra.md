# Microsoft Entra ID Integration

This document covers the authentication model, client initialisation pattern,
and extension points for the `EntraAdapter` in `src/adapters/entra.py`.

---

## Overview

[Microsoft Entra ID](https://learn.microsoft.com/entra/fundamentals/)
(formerly Azure Active Directory) is Microsoft's cloud identity and access
management service.

This adapter covers directory operations performed via the Microsoft Graph API:
- User and group management
- Application / service principal queries
- Role assignment inspection
- Token validation (extensible placeholder)

---

## Authentication model

Entra ID itself is the identity provider that issues tokens for all other
services.  The adapter uses a **service principal** (app registration) with
the client-credentials flow to authenticate against the Graph API to then
*read* directory objects:

```
Entra Tenant
  └── App Registration (service principal)
        ├── Client ID + Client Secret  → ClientSecretCredential
        └── API permissions (Directory.Read.All, Group.Read.All, ...)
              → GraphServiceClient → /users, /groups, /servicePrincipals
```

For production workloads running in Azure, prefer `ManagedIdentityCredential`
(no secret) over `ClientSecretCredential`.

---

## Required Azure permissions

| Permission | Type | Purpose |
|---|---|---|
| `Directory.Read.All` | Application | Read all directory objects |
| `Group.Read.All` | Application | Read groups and memberships |
| `User.Read.All` | Application | Read user objects |
| `Application.Read.All` | Application | Read service principals, app registrations |
| `RoleManagement.Read.All` | Application | Read role assignments |

All application permissions require **admin consent** from a Global
Administrator.

---

## Client initialisation pattern

The `EntraAdapter` shares the same `GraphServiceClient` pattern as
`A365Adapter` because both use the Microsoft Graph API:

```python
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient

credential = ClientSecretCredential(
    tenant_id=settings.azure_tenant_id,
    client_id=settings.azure_client_id,
    client_secret=settings.azure_client_secret,
)

graph_client = GraphServiceClient(
    credentials=credential,
    scopes=["https://graph.microsoft.com/.default"],
)
```

---

## Extension points

### Reading service principals

```python
service_principals = await graph_client.service_principals.get()
```

### Checking role assignments

```python
role_assignments = await graph_client.role_management.directory \
    .role_assignments.get()
```

### Token validation (JWT)

The `validate_token()` method is currently a `NotImplementedError` placeholder.
To implement it:

1. Fetch the tenant's JWKS:
   ```
   GET https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys
   ```
2. Verify signature, `iss`, `aud`, `exp`, and `nbf` claims.
3. Recommended library: [`python-jose`](https://python-jose.readthedocs.io/)
   or [`msal`](https://msal-python.readthedocs.io/).

```python
from jose import jwt

def validate_token(token: str, jwks: dict, audience: str, issuer: str) -> dict:
    return jwt.decode(token, jwks, algorithms=["RS256"],
                      audience=audience, issuer=issuer)
```

### Conditional Access / Named Locations

Query Conditional Access policies and named locations via:
```python
ca_policies = await graph_client.identity.conditional_access.policies.get()
```

---

## Notes on sovereign clouds

Change `AZURE_AUTHORITY_HOST` for non-public clouds:

| Cloud | Authority host |
|---|---|
| Public | `https://login.microsoftonline.com` |
| US Government | `https://login.microsoftonline.us` |
| China (21Vianet) | `https://login.chinacloudapi.cn` |
| Germany | `https://login.microsoftonline.de` |

---

## SDK version tracking

The current tracked version of `azure-identity` is recorded in
[`sdk-versions.json`](../../sdk-versions.json) and updated automatically by
the [sdk-watch workflow](../../.github/workflows/sdk-watch.yml).

**PyPI:** https://pypi.org/project/azure-identity/  
**Docs:** https://learn.microsoft.com/python/api/overview/azure/identity-readme
