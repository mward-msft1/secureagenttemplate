"""
Tests for src/config.py

These tests verify that AgentSettings loads and validates environment
variables correctly without requiring real Azure credentials.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError


def _make_env(overrides: dict | None = None) -> dict:
    """Return a minimal valid set of environment variables."""
    base = {
        "AZURE_TENANT_ID": "test-tenant-id",
        "AZURE_CLIENT_ID": "test-client-id",
        "AZURE_CLIENT_SECRET": "test-secret",
        "PURVIEW_ENDPOINT": "https://test.purview.azure.com",
        "PURVIEW_ACCOUNT_NAME": "test-purview",
    }
    if overrides:
        base.update(overrides)
    return base


class TestAgentSettings:
    def test_loads_with_valid_env(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Settings should load successfully with all required variables set."""
        from src.config import AgentSettings

        for k, v in _make_env().items():
            monkeypatch.setenv(k, v)
        # Prevent loading from any .env file during tests
        settings = AgentSettings(_env_file=None)  # type: ignore[call-arg]
        assert settings.azure_tenant_id == "test-tenant-id"
        assert settings.purview_account_name == "test-purview"

    def test_defaults_applied(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Optional settings should have sensible defaults."""
        from src.config import AgentSettings

        for k, v in _make_env().items():
            monkeypatch.setenv(k, v)
        settings = AgentSettings(_env_file=None)  # type: ignore[call-arg]
        assert settings.log_level == "INFO"
        assert settings.mock_sdk_calls is False
        assert settings.log_json is False

    def test_missing_required_raises(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Missing a required field should raise ValidationError."""
        from src.config import AgentSettings

        env = _make_env()
        env.pop("AZURE_TENANT_ID")
        for k, v in env.items():
            monkeypatch.setenv(k, v)
        monkeypatch.delenv("AZURE_TENANT_ID", raising=False)
        with pytest.raises(ValidationError):
            AgentSettings(_env_file=None)  # type: ignore[call-arg]

    def test_graph_scopes_parsed_from_comma_string(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """GRAPH_SCOPES accepts a JSON-encoded list array."""
        from src.config import AgentSettings

        env = _make_env(
            {"GRAPH_SCOPES": '["https://graph.microsoft.com/.default","openid","profile"]'}
        )
        for k, v in env.items():
            monkeypatch.setenv(k, v)
        settings = AgentSettings(_env_file=None)  # type: ignore[call-arg]
        assert settings.graph_scopes == [
            "https://graph.microsoft.com/.default",
            "openid",
            "profile",
        ]

    def test_mock_sdk_calls_flag(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """MOCK_SDK_CALLS=true should be parsed as True."""
        from src.config import AgentSettings

        for k, v in _make_env({"MOCK_SDK_CALLS": "true"}).items():
            monkeypatch.setenv(k, v)
        settings = AgentSettings(_env_file=None)  # type: ignore[call-arg]
        assert settings.mock_sdk_calls is True
