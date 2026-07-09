"""
Tests for the SDK adapters in mock mode.

All tests run with MOCK_SDK_CALLS=true so no real Azure credentials
or network access are required.
"""

from __future__ import annotations

import pytest


def _mock_settings(overrides: dict | None = None):
    """Return an AgentSettings instance in mock mode, via environment variables."""
    import os

    from src.config import AgentSettings

    env = {
        "AZURE_TENANT_ID": "test-tenant",
        "AZURE_CLIENT_ID": "test-client",
        "AZURE_CLIENT_SECRET": "test-secret",
        "PURVIEW_ENDPOINT": "https://test.purview.azure.com",
        "PURVIEW_ACCOUNT_NAME": "test-purview",
        "MOCK_SDK_CALLS": "true",
        **(overrides or {}),
    }
    # Temporarily inject env vars then restore originals
    old = {k: os.environ.get(k) for k in env}
    for k, v in env.items():
        os.environ[k] = v
    try:
        settings = AgentSettings(_env_file=None)  # type: ignore[call-arg]
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
    return settings


# ---------------------------------------------------------------------------
# PurviewAdapter
# ---------------------------------------------------------------------------

class TestPurviewAdapter:
    def test_list_data_sources_mock(self) -> None:
        from src.adapters.purview import PurviewAdapter

        adapter = PurviewAdapter(_mock_settings())
        sources = adapter.list_data_sources()
        assert isinstance(sources, list)
        assert sources[0]["mock"] is True

    def test_list_glossaries_mock(self) -> None:
        from src.adapters.purview import PurviewAdapter

        adapter = PurviewAdapter(_mock_settings())
        glossaries = adapter.list_glossaries()
        assert isinstance(glossaries, list)
        assert glossaries[0]["name"] == "MockGlossary"

    def test_get_entity_by_guid_mock(self) -> None:
        from src.adapters.purview import PurviewAdapter

        adapter = PurviewAdapter(_mock_settings())
        entity = adapter.get_entity_by_guid("test-guid-123")
        assert entity["guid"] == "test-guid-123"
        assert entity["mock"] is True


# ---------------------------------------------------------------------------
# A365Adapter
# ---------------------------------------------------------------------------

class TestA365Adapter:
    @pytest.mark.asyncio
    async def test_list_users_mock(self) -> None:
        from src.adapters.a365 import A365Adapter

        adapter = A365Adapter(_mock_settings())
        users = await adapter.list_users()
        assert isinstance(users, list)
        assert users[0]["mock"] is True

    @pytest.mark.asyncio
    async def test_get_user_mock(self) -> None:
        from src.adapters.a365 import A365Adapter

        adapter = A365Adapter(_mock_settings())
        user = await adapter.get_user("test@example.com")
        assert user["mock"] is True


# ---------------------------------------------------------------------------
# EntraAdapter
# ---------------------------------------------------------------------------

class TestEntraAdapter:
    @pytest.mark.asyncio
    async def test_list_groups_mock(self) -> None:
        from src.adapters.entra import EntraAdapter

        adapter = EntraAdapter(_mock_settings())
        groups = await adapter.list_groups()
        assert isinstance(groups, list)
        assert groups[0]["displayName"] == "MockGroup"

    @pytest.mark.asyncio
    async def test_list_users_mock(self) -> None:
        from src.adapters.entra import EntraAdapter

        adapter = EntraAdapter(_mock_settings())
        users = await adapter.list_users()
        assert isinstance(users, list)
        assert users[0]["displayName"] == "Mock User"

    def test_validate_token_not_implemented(self) -> None:
        from src.adapters.entra import EntraAdapter

        adapter = EntraAdapter(_mock_settings())
        with pytest.raises(NotImplementedError):
            adapter.validate_token("fake-token")


# ---------------------------------------------------------------------------
# AgentOrchestrator
# ---------------------------------------------------------------------------

class TestAgentOrchestrator:
    @pytest.mark.asyncio
    async def test_run_sample_flow_mock(self) -> None:
        from src.agent import AgentOrchestrator

        settings = _mock_settings()
        orchestrator = AgentOrchestrator(settings)
        result = await orchestrator.run_sample_flow()

        assert "entra_groups" in result
        assert "a365_users" in result
        assert "purview_data_sources" in result
        assert isinstance(result["entra_groups"], list)
        assert isinstance(result["a365_users"], list)
        assert isinstance(result["purview_data_sources"], list)
