"""
adapters/a365.py
----------------
Adapter for Microsoft 365 services via the Microsoft Graph API.

"A365" (Azure / Microsoft 365) operations are accessed through the
Microsoft Graph Python SDK (msgraph-sdk).  This adapter demonstrates
common patterns: listing users, reading mail metadata, and accessing
SharePoint/OneDrive sites.

Note: "A365 SDK" is not an official Microsoft product name. This template
interprets it as the Microsoft 365 platform, accessed via the Microsoft
Graph API – the authoritative, unified entry point for M365 workloads.
If your workload requires a specific M365 service (Teams, Exchange Online
management, etc.) you can extend this adapter accordingly.

Least-privilege application permissions required (examples):
  - User.Read.All          – list/read users
  - Mail.Read              – read mail metadata
  - Sites.Read.All         – read SharePoint/OneDrive sites
  - Files.Read.All         – read files

Extension points
----------------
- Add methods below for the Graph resources your agent needs.
- For delegated (user-context) permissions, swap the credential for an
  InteractiveBrowserCredential or OnBehalfOfCredential.

See docs/integrations/a365.md for full details.
"""

from __future__ import annotations

from typing import Any

import structlog

from src.config import AgentSettings

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

class _MockSingleUser:
    """Represents a single user resource on the mock Graph client."""

    async def get(self) -> dict[str, Any]:
        return {"mock": True, "displayName": "Mock User", "mail": "mock@example.com"}


class _MockUsersResource:
    """Represents the /users collection on the mock Graph client."""

    async def get(self) -> dict[str, Any]:
        return {
            "value": [
                {"mock": True, "displayName": "Mock User", "mail": "mock@example.com"}
            ]
        }

    def __call__(self, user_id: str) -> _MockSingleUser:
        return _MockSingleUser()


class _MockSitesResource:
    """Represents the /sites collection on the mock Graph client."""

    async def get(self) -> dict[str, Any]:
        return {"value": [{"mock": True, "name": "MockSite", "id": "mock-site-id"}]}


class _MockGraphClient:
    """Minimal stand-in for the Graph SDK client used in local dev / tests."""

    def __init__(self) -> None:
        self.users = _MockUsersResource()
        self.sites = _MockSitesResource()


# ---------------------------------------------------------------------------
# A365Adapter
# ---------------------------------------------------------------------------

class A365Adapter:
    """
    Thin adapter over the Microsoft Graph SDK for M365 operations.

    Usage::

        adapter = A365Adapter(settings)
        users   = await adapter.list_users()
        user    = await adapter.get_user("user@contoso.com")
    """

    def __init__(self, settings: AgentSettings) -> None:
        self._settings = settings
        self._client = self._build_client()
        logger.info(
            "A365Adapter initialised",
            endpoint=str(settings.graph_api_endpoint),
            mock=settings.mock_sdk_calls,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _get_credential(self) -> Any:
        """Return an azure-identity credential for Graph authentication."""
        from azure.identity import ClientSecretCredential

        return ClientSecretCredential(
            tenant_id=self._settings.azure_tenant_id,
            client_id=self._settings.azure_client_id,
            client_secret=self._settings.azure_client_secret,
            authority=str(self._settings.azure_authority_host),
        )

    def _build_client(self) -> Any:
        if self._settings.mock_sdk_calls:
            logger.debug("A365Adapter: using mock Graph client")
            return _MockGraphClient()

        # azure-identity TokenCredential → Graph SDK adapter
        from azure.identity import ClientSecretCredential
        from msgraph import GraphServiceClient  # type: ignore[import]

        credential = ClientSecretCredential(
            tenant_id=self._settings.azure_tenant_id,
            client_id=self._settings.azure_client_id,
            client_secret=self._settings.azure_client_secret,
            authority=str(self._settings.azure_authority_host),
        )
        return GraphServiceClient(
            credentials=credential,
            scopes=self._settings.graph_scopes,
        )

    # ── Public API ────────────────────────────────────────────────────────────

    async def list_users(self, top: int = 25) -> list[dict[str, Any]]:
        """List up to `top` users in the tenant directory."""
        logger.info("Listing M365 users", top=top)
        try:
            # The Graph SDK returns an OData collection; convert to plain dicts.
            response = await self._client.users.get()
            users: list[dict[str, Any]] = response.get("value", [])
            logger.debug("Users retrieved", count=len(users))
            return users
        except Exception as exc:
            logger.error("Failed to list M365 users", error=str(exc))
            raise

    async def get_user(self, user_id_or_upn: str) -> dict[str, Any]:
        """Retrieve a single user by object ID or UPN."""
        logger.info("Fetching M365 user", user=user_id_or_upn)
        try:
            result: dict[str, Any] = await self._client.users(user_id_or_upn).get()
            logger.debug("User retrieved", display_name=result.get("displayName"))
            return result
        except Exception as exc:
            logger.error("Failed to fetch M365 user", user=user_id_or_upn, error=str(exc))
            raise

    async def list_sites(self) -> list[dict[str, Any]]:
        """List SharePoint sites accessible to the service principal."""
        logger.info("Listing SharePoint sites")
        try:
            # TODO: Extend with pagination using @odata.nextLink for large tenants.
            response = await self._client.sites.get()
            sites: list[dict[str, Any]] = response.get("value", [])
            logger.debug("Sites retrieved", count=len(sites))
            return sites
        except Exception as exc:
            logger.error("Failed to list SharePoint sites", error=str(exc))
            raise
