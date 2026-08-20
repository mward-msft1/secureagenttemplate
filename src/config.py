"""
config.py
---------
Centralised configuration loading and validation using pydantic-settings.

All settings are read from environment variables (or a .env file during
local development).  Never hardcode secrets; see .env.example for required
variables and docs/configuration.md for least-privilege guidance.
"""

from __future__ import annotations

from typing import Literal

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Validated, typed configuration for the entire agent."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Azure identity ────────────────────────────────────────────────────────
    azure_tenant_id: str = Field(..., description="Azure AD / Entra tenant ID")
    azure_client_id: str = Field(..., description="Service-principal client ID")
    azure_client_secret: str = Field(..., description="Service-principal client secret")

    # ── Purview ───────────────────────────────────────────────────────────────
    purview_endpoint: AnyHttpUrl = Field(
        ...,
        description="Purview account endpoint, e.g. https://<name>.purview.azure.com",
    )
    purview_account_name: str = Field(..., description="Purview account name")

    # ── Microsoft Graph / A365 ────────────────────────────────────────────────
    graph_api_endpoint: AnyHttpUrl = Field(
        default="https://graph.microsoft.com/v1.0",
        description="Microsoft Graph base URL",
    )
    # NOTE: pydantic-settings v2 requires JSON-encoded list values for list fields.
    # In .env, set this as: GRAPH_SCOPES=["https://graph.microsoft.com/.default"]
    # Or leave unset to use the default value.
    graph_scopes: list[str] = Field(
        default=["https://graph.microsoft.com/.default"],
        description="Graph permission scopes (JSON-encoded list in env var)",
    )

    # ── Entra ─────────────────────────────────────────────────────────────────
    azure_authority_host: AnyHttpUrl = Field(
        default="https://login.microsoftonline.com",
        description="Azure AD authority host (change for sovereign clouds)",
    )

    # ── Runtime ───────────────────────────────────────────────────────────────
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Python logging level",
    )
    log_json: bool = Field(
        default=False,
        description="Emit logs as JSON (recommended for production / SIEM ingestion)",
    )
    log_mask_sensitive: bool = Field(
        default=True,
        description="Redact sensitive field values from structured log output",
    )

    # ── Dev helpers ───────────────────────────────────────────────────────────
    mock_sdk_calls: bool = Field(
        default=False,
        description="Return mock responses instead of making real SDK calls",
    )

    @field_validator("graph_scopes", mode="before")
    @classmethod
    def _parse_scopes(cls, v: object) -> list[str]:
        """Accept either a comma-separated string or a JSON list string or a list."""
        if isinstance(v, str):
            # Try JSON first (pydantic-settings v2 standard format)
            import json as _json
            stripped = v.strip()
            if stripped.startswith("["):
                try:
                    return _json.loads(stripped)
                except ValueError:
                    pass
            # Fall back to comma-separated
            return [s.strip() for s in v.split(",") if s.strip()]
        return v  # type: ignore[return-value]


def load_settings() -> AgentSettings:
    """Load and validate settings, raising on any missing required variable."""
    return AgentSettings()  # type: ignore[call-arg]


def configure_logging(settings: AgentSettings) -> None:
    """Configure structlog (JSON or human-readable) based on settings."""
    import logging as _stdlib_logging

    import structlog

    level = _stdlib_logging.getLevelName(settings.log_level)
    _stdlib_logging.basicConfig(format="%(message)s", level=level)

    shared_processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]

    if settings.log_json:
        renderer: structlog.types.Processor = structlog.processors.JSONRenderer()
    else:
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=[*shared_processors, renderer],
        wrapper_class=structlog.make_filtering_bound_logger(level),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
