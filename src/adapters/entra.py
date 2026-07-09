"""
adapters/entra.py
-----------------
Adapter for Microsoft Entra ID (formerly Azure Active Directory) directory
and identity operations.

Modern Entra ID operations are performed via the Microsoft Graph API (same
SDK used in a365.py).  This adapter focuses on identity-specific tasks:
  - Resolving users / groups / service principals
  - Checking and validating group membership
  - Listing app role assignments

Least-privilege application permissions required (examples):
  - Directory.Read.All       – read all directory objects
  - Group.Read.All           – read groups and memberships
  - Application.Read.All     – read service principals / app registrations
  - RoleManagement.Read.All  – read role assignments

Extension points
----------------
- For token validation / JWKS operations, extend `validate_token()`.
- For SCIM provisioning, add SCIM client calls alongside Graph.
- Swap ClientSecretCredential for ManagedIdentityCredential in production.

See docs/integrations/entra.md for full details.
"""

from __future__ import annotations

from typing import Any

import structlog

from src.config import AgentSettings

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Mock helpers
# ---------------------------------------------------------------------------

class _MockGroupMembers:
    """Represents the members of a single group."""

    async def get(self) -> dict[str, Any]:
        return {"value": [{"mock": True, "id": "mock-member-id"}]}


class _MockGroupsResource:
    """Represents the /groups collection on the mock Entra client."""

    async def get(self) -> dict[str, Any]:
        return {
            "value": [{"mock": True, "displayName": "MockGroup", "id": "mock-group-id"}]
        }

    def __call__(self, group_id: str) -> _MockGroupMembers:
        return _MockGroupMembers()


class _MockEntraUsersResource:
    """Represents the /users collection on the mock Entra client."""

    async def get(self) -> dict[str, Any]:
        return {
            "value": [{"mock": True, "displayName": "Mock User", "id": "mock-user-id"}]
        }


class _MockEntraClient:
    """Minimal stand-in used in local dev / tests."""

    def __init__(self) -> None:
        self.groups = _MockGroupsResource()
        self.users = _MockEntraUsersResource()


# ---------------------------------------------------------------------------
# EntraAdapter
# ---------------------------------------------------------------------------

class EntraAdapter:
    """
    Thin adapter for Microsoft Entra ID directory operations via Graph.

    Usage::

        adapter = EntraAdapter(settings)
        groups  = await adapter.list_groups()
        members = await adapter.list_group_members("group-object-id")
    """

    def __init__(self, settings: AgentSettings) -> None:
        self._settings = settings
        self._client = self._build_client()
        logger.info(
            "EntraAdapter initialised",
            tenant=settings.azure_tenant_id,
            mock=settings.mock_sdk_calls,
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _get_credential(self) -> Any:
        """Return an azure-identity credential scoped to the tenant."""
        from azure.identity import ClientSecretCredential

        return ClientSecretCredential(
            tenant_id=self._settings.azure_tenant_id,
            client_id=self._settings.azure_client_id,
            client_secret=self._settings.azure_client_secret,
            authority=str(self._settings.azure_authority_host),
        )

    def _build_client(self) -> Any:
        if self._settings.mock_sdk_calls:
            logger.debug("EntraAdapter: using mock client")
            return _MockEntraClient()

        from msgraph import GraphServiceClient  # type: ignore[import]

        return GraphServiceClient(
            credentials=self._get_credential(),
            scopes=self._settings.graph_scopes,
        )

    # ── Public API ────────────────────────────────────────────────────────────

    async def list_groups(self) -> list[dict[str, Any]]:
        """List all security/M365 groups in the tenant."""
        logger.info("Listing Entra groups")
        try:
            response = await self._client.groups.get()
            groups: list[dict[str, Any]] = response.get("value", [])
            logger.debug("Groups retrieved", count=len(groups))
            return groups
        except Exception as exc:
            logger.error("Failed to list Entra groups", error=str(exc))
            raise

    async def list_group_members(self, group_id: str) -> list[dict[str, Any]]:
        """List members of a specific group by its object ID."""
        logger.info("Listing group members", group_id=group_id)
        try:
            response = await self._client.groups(group_id).get()
            members: list[dict[str, Any]] = response.get("value", [])
            logger.debug("Group members retrieved", group_id=group_id, count=len(members))
            return members
        except Exception as exc:
            logger.error("Failed to list group members", group_id=group_id, error=str(exc))
            raise

    async def list_users(self) -> list[dict[str, Any]]:
        """List users in the tenant directory (delegates to Graph /users)."""
        logger.info("Listing Entra users")
        try:
            response = await self._client.users.get()
            users: list[dict[str, Any]] = response.get("value", [])
            logger.debug("Entra users retrieved", count=len(users))
            return users
        except Exception as exc:
            logger.error("Failed to list Entra users", error=str(exc))
            raise

    def validate_token(self, token: str) -> dict[str, Any]:
        """
        Validate a JWT access token issued by Entra ID.

        This is a placeholder that documents the expected extension point.
        In production, use a JWKS-based validator such as python-jose or
        msal's token-validation helpers to verify signature, audience, issuer,
        and expiry before trusting any claims.

        TODO: Implement JWKS fetch from:
          https://login.microsoftonline.com/{tenant_id}/discovery/v2.0/keys
        """
        raise NotImplementedError(
            "Token validation is not yet implemented. "
            "See the docstring for extension guidance."
        )
