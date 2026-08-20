"""
adapters/purview.py
-------------------
Adapter for Microsoft Purview (Unified Data Governance).

Wraps the azure-purview-catalog and azure-purview-scanning SDKs.
All calls require an authenticated credential object from azure-identity.

Least-privilege roles required:
  - Data Source Admin (for scanning operations)
  - Data Curator   (for catalog read/write)
  - Data Reader    (for read-only catalog access)

Extension points
----------------
- Override `_get_credential()` to swap DefaultAzureCredential for a
  different credential type (e.g. ManagedIdentityCredential for AKS).
- Add methods to `PurviewAdapter` for the specific Purview APIs you need.
  The existing methods serve as documented patterns to follow.

See docs/integrations/purview.md for full details.
"""

from __future__ import annotations

from typing import Any

import structlog

from src.config import AgentSettings

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Mock helpers (used when settings.mock_sdk_calls is True)
# ---------------------------------------------------------------------------

class _MockPurviewCatalogClient:
    """Minimal stand-in for PurviewCatalogClient used in local dev / tests."""

    def __init__(self, endpoint: str, **_: Any) -> None:
        self._endpoint = endpoint

    class entity:  # noqa: N801 – mirrors SDK attribute naming
        @staticmethod
        def get_by_guid(guid: str) -> dict[str, Any]:
            return {"mock": True, "guid": guid, "typeName": "MockAsset"}

    class glossary:  # noqa: N801
        @staticmethod
        def list_glossaries(**_: Any) -> list[dict[str, Any]]:
            return [{"mock": True, "name": "MockGlossary"}]


class _MockPurviewScanningClient:
    """Minimal stand-in for PurviewScanningClient used in local dev / tests."""

    def __init__(self, endpoint: str, **_: Any) -> None:
        self._endpoint = endpoint

    class data_sources:  # noqa: N801
        @staticmethod
        def list_all() -> list[dict[str, Any]]:
            return [{"mock": True, "name": "MockDataSource"}]


# ---------------------------------------------------------------------------
# PurviewAdapter
# ---------------------------------------------------------------------------

class PurviewAdapter:
    """
    Thin adapter over the Microsoft Purview catalog and scanning SDKs.

    Usage::

        adapter = PurviewAdapter(settings)
        entity  = adapter.get_entity_by_guid("some-guid")
        sources = adapter.list_data_sources()
    """

    def __init__(self, settings: AgentSettings) -> None:
        self._settings = settings
        self._catalog_client = self._build_catalog_client()
        self._scanning_client = self._build_scanning_client()
        logger.info(
            "PurviewAdapter initialised",
            endpoint=str(settings.purview_endpoint),
            mock=settings.mock_sdk_calls,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _get_credential(self) -> Any:
        """Return an azure-identity credential for Purview authentication."""
        from azure.identity import ClientSecretCredential

        return ClientSecretCredential(
            tenant_id=self._settings.azure_tenant_id,
            client_id=self._settings.azure_client_id,
            client_secret=self._settings.azure_client_secret,
            authority=str(self._settings.azure_authority_host),
        )

    def _build_catalog_client(self) -> Any:
        endpoint = str(self._settings.purview_endpoint)
        if self._settings.mock_sdk_calls:
            logger.debug("PurviewAdapter: using mock catalog client")
            return _MockPurviewCatalogClient(endpoint)

        # TODO: Replace with azure-purview-catalog once GA SDK is stable,
        # or use the unified azure.purview.datamap package if available.
        from azure.purview.catalog import PurviewCatalogClient  # type: ignore[import]

        return PurviewCatalogClient(
            endpoint=endpoint,
            credential=self._get_credential(),
        )

    def _build_scanning_client(self) -> Any:
        endpoint = str(self._settings.purview_endpoint)
        if self._settings.mock_sdk_calls:
            logger.debug("PurviewAdapter: using mock scanning client")
            return _MockPurviewScanningClient(endpoint)

        from azure.purview.scanning import PurviewScanningClient  # type: ignore[import]

        return PurviewScanningClient(
            endpoint=endpoint,
            credential=self._get_credential(),
        )

    # ── Public API ────────────────────────────────────────────────────────────

    def get_entity_by_guid(self, guid: str) -> dict[str, Any]:
        """Retrieve a catalog entity by its GUID."""
        logger.info("Fetching Purview entity", guid=guid)
        try:
            result: dict[str, Any] = self._catalog_client.entity.get_by_guid(guid)
            logger.debug("Entity retrieved", guid=guid, type=result.get("typeName"))
            return result
        except Exception as exc:
            logger.error("Failed to retrieve Purview entity", guid=guid, error=str(exc))
            raise

    def list_glossaries(self) -> list[dict[str, Any]]:
        """List all glossaries in the Purview catalog."""
        logger.info("Listing Purview glossaries")
        try:
            result: list[dict[str, Any]] = list(
                self._catalog_client.glossary.list_glossaries()
            )
            logger.debug("Glossaries retrieved", count=len(result))
            return result
        except Exception as exc:
            logger.error("Failed to list Purview glossaries", error=str(exc))
            raise

    def list_data_sources(self) -> list[dict[str, Any]]:
        """List all registered scanning data sources."""
        logger.info("Listing Purview data sources")
        try:
            result: list[dict[str, Any]] = list(
                self._scanning_client.data_sources.list_all()
            )
            logger.debug("Data sources retrieved", count=len(result))
            return result
        except Exception as exc:
            logger.error("Failed to list Purview data sources", error=str(exc))
            raise
