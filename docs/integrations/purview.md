# Microsoft Purview Integration

This document covers the authentication model, client initialisation pattern,
and extension points for the `PurviewAdapter` in `src/adapters/purview.py`.

---

## Overview

[Microsoft Purview](https://learn.microsoft.com/purview/) is Microsoft's
unified data-governance platform.  This adapter covers two main sub-services:

| Sub-service | SDK package | Purpose |
|---|---|---|
| **Purview Catalog** | `azure-purview-catalog` | Search, read, and write catalog entities, glossaries, classifications, lineage |
| **Purview Scanning** | `azure-purview-scanning` | Register data sources, create and trigger scans |

---

## Authentication model

Purview uses OAuth 2.0 client-credentials flow with Azure AD / Entra ID.

```
App Registration (service principal)
    → ClientSecretCredential (azure-identity)
        → Token audience: https://purview.azure.com/.default
            → PurviewCatalogClient / PurviewScanningClient
```

The `PurviewAdapter` instantiates a `ClientSecretCredential` from the
configured tenant ID, client ID, and client secret.  In production, replace
this with `ManagedIdentityCredential` or `DefaultAzureCredential` to
eliminate secrets entirely.

---

## Required Azure permissions

Assign the following roles at the **Purview account** or **collection** level
(Azure Portal → Microsoft Purview → your account → Data Map → Collections →
Role assignments):

| Role | Required for |
|---|---|
| Data Reader | Read catalog entities, glossaries, lineage |
| Data Curator | Create/edit entities, apply classifications |
| Data Source Admin | Register data sources, trigger scans |

---

## Client initialisation pattern

```python
from azure.identity import ClientSecretCredential
from azure.purview.catalog import PurviewCatalogClient
from azure.purview.scanning import PurviewScanningClient

credential = ClientSecretCredential(
    tenant_id=settings.azure_tenant_id,
    client_id=settings.azure_client_id,
    client_secret=settings.azure_client_secret,
)

catalog_client = PurviewCatalogClient(
    endpoint="https://<account>.purview.azure.com",
    credential=credential,
)

scanning_client = PurviewScanningClient(
    endpoint="https://<account>.purview.azure.com",
    credential=credential,
)
```

---

## Extension points

### Adding catalog operations

The `PurviewCatalogClient` exposes operations grouped by resource:

```python
# Search entities
results = catalog_client.discovery.query({"keywords": "sales"})

# Get lineage
lineage = catalog_client.lineage.get_lineage_graph(guid="<entity-guid>")

# Apply a classification
catalog_client.entity.add_classification(
    classification={"typeName": "MICROSOFT.FINANCIAL.CREDIT_CARD_NUMBER"},
    entity_guids=["<guid1>", "<guid2>"],
)
```

### Adding scanning operations

```python
# Register a data source
scanning_client.data_sources.create_or_update(
    data_source_name="my-adls",
    body={
        "kind": "AdlsGen2",
        "properties": {"endpoint": "https://myadls.dfs.core.windows.net"},
    },
)

# Trigger a scan
scanning_client.scans.run_scan(
    data_source_name="my-adls",
    scan_name="my-scan",
    body={},
)
```

### Using a different credential type

Override `_get_credential()` in a subclass:

```python
class ProductionPurviewAdapter(PurviewAdapter):
    def _get_credential(self):
        from azure.identity import ManagedIdentityCredential
        return ManagedIdentityCredential()
```

---

## SDK version tracking

The current tracked version of `azure-purview-catalog` is recorded in
[`sdk-versions.json`](../../sdk-versions.json) and updated automatically by
the [sdk-watch workflow](../../.github/workflows/sdk-watch.yml).

**PyPI:** https://pypi.org/project/azure-purview-catalog/  
**Docs:** https://learn.microsoft.com/python/api/overview/azure/purview
