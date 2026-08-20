"""
agent.py
--------
Orchestration layer for the secure-agent-template.

This module wires together the three SDK adapters (Purview, A365, Entra) and
exposes a single `AgentOrchestrator` class that demonstrates how to compose
them into a cohesive agent request flow.

The sample execution path in `run_sample_flow()` shows:
  1. Auth / credential bootstrap  (config → credentials)
  2. Entra identity lookup        (validate caller / resolve group membership)
  3. A365 Graph query             (list users / sites)
  4. Purview data-governance call (fetch catalog entity or data sources)

Extend `AgentOrchestrator` with your own methods, or use the adapters
directly in an agent framework (LangChain, Semantic Kernel, AutoGen, etc.).
"""

from __future__ import annotations

import asyncio
from typing import Any

import structlog

from src.adapters.a365 import A365Adapter
from src.adapters.entra import EntraAdapter
from src.adapters.purview import PurviewAdapter
from src.config import AgentSettings, configure_logging, load_settings

logger = structlog.get_logger(__name__)


class AgentOrchestrator:
    """
    Top-level orchestrator that coordinates Purview, A365, and Entra adapters.

    Usage::

        settings     = load_settings()
        orchestrator = AgentOrchestrator(settings)
        result       = await orchestrator.run_sample_flow()
    """

    def __init__(self, settings: AgentSettings) -> None:
        self._settings = settings
        self.purview = PurviewAdapter(settings)
        self.a365 = A365Adapter(settings)
        self.entra = EntraAdapter(settings)
        logger.info("AgentOrchestrator ready", mock=settings.mock_sdk_calls)

    async def run_sample_flow(self) -> dict[str, Any]:
        """
        Demonstrate a single request routed through auth + all three adapters.

        Returns a dictionary with results from each adapter.  In a real agent
        you would replace these with business-logic calls.
        """
        logger.info("Starting sample agent flow")

        results: dict[str, Any] = {}

        # ── Step 1: Entra – resolve tenant groups ─────────────────────────────
        logger.info("Step 1/3 – Entra: listing groups")
        groups = await self.entra.list_groups()
        results["entra_groups"] = groups
        logger.info("Entra groups retrieved", count=len(groups))

        # ── Step 2: A365 – list tenant users ─────────────────────────────────
        logger.info("Step 2/3 – A365: listing users")
        users = await self.a365.list_users()
        results["a365_users"] = users
        logger.info("A365 users retrieved", count=len(users))

        # ── Step 3: Purview – list registered data sources ────────────────────
        logger.info("Step 3/3 – Purview: listing data sources")
        sources = self.purview.list_data_sources()
        results["purview_data_sources"] = sources
        logger.info("Purview data sources retrieved", count=len(sources))

        logger.info("Sample flow complete", steps=3)
        return results

    async def get_asset_with_owner(self, asset_guid: str) -> dict[str, Any]:
        """
        Example composed operation: fetch a Purview entity and resolve its
        owner's identity via Entra.

        TODO: Map the asset's 'contacts.Owner' field to an Entra user object.
        """
        logger.info("Fetching asset with owner", guid=asset_guid)
        entity = self.purview.get_entity_by_guid(asset_guid)

        # Placeholder – extract owner UPN from entity attributes.
        owner_upn = entity.get("attributes", {}).get("userDescription", "")
        owner: dict[str, Any] = {}
        if owner_upn:
            try:
                users = await self.entra.list_users()
                owner = next((u for u in users if u.get("mail") == owner_upn), {})
            except Exception as exc:
                logger.warning("Could not resolve asset owner", upn=owner_upn, error=str(exc))

        return {"entity": entity, "owner": owner}


async def _async_main() -> None:
    settings = load_settings()
    configure_logging(settings)
    orchestrator = AgentOrchestrator(settings)
    result = await orchestrator.run_sample_flow()
    logger.info("Flow result", result=result)


def main() -> None:
    """Entry-point used by the `run-agent` console script."""
    asyncio.run(_async_main())


if __name__ == "__main__":
    main()
