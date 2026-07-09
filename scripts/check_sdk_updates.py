#!/usr/bin/env python3
"""
check_sdk_updates.py
--------------------
Checks PyPI for new versions of the tracked SDKs defined in sdk-versions.json.

Usage
-----
  # Run directly
  python scripts/check_sdk_updates.py

  # Output a machine-readable exit code
  # Exit 0 → no changes  |  Exit 1 → one or more SDKs have a new version

The script:
  1. Reads sdk-versions.json from the repo root.
  2. Fetches the latest version from PyPI for each tracked package.
  3. Compares with the tracked version.
  4. If any version changed:
     - Updates sdk-versions.json in-place.
     - Appends a new row to docs/sdk-updates.md.
  5. Prints a summary to stdout.
  6. Exits with code 1 if any SDK was updated (useful in CI to trigger PR).

Dependencies: httpx (listed in requirements.txt)
"""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import httpx

# ── Paths ─────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).parent.parent
SDK_VERSIONS_FILE = REPO_ROOT / "sdk-versions.json"
SDK_UPDATES_DOC = REPO_ROOT / "docs" / "sdk-updates.md"

PYPI_TIMEOUT = 15  # seconds


def fetch_latest_pypi_version(package: str) -> str | None:
    """Return the latest stable version string from PyPI, or None on error."""
    url = f"https://pypi.org/pypi/{package}/json"
    try:
        response = httpx.get(url, timeout=PYPI_TIMEOUT, follow_redirects=True)
        response.raise_for_status()
        data: dict = response.json()
        return str(data["info"]["version"])
    except httpx.HTTPError as exc:
        print(f"[WARN] HTTP error fetching {package}: {exc}", file=sys.stderr)
        return None
    except (KeyError, ValueError) as exc:
        print(f"[WARN] Unexpected PyPI response for {package}: {exc}", file=sys.stderr)
        return None


def append_sdk_updates_doc(
    updates: list[dict[str, str]],
) -> None:
    """Insert new rows into the sdk-updates.md changelog table."""
    if not updates:
        return

    content = SDK_UPDATES_DOC.read_text(encoding="utf-8")
    marker = "<!-- sdk-watch: new rows inserted after this line -->"
    if marker not in content:
        print(f"[WARN] Marker not found in {SDK_UPDATES_DOC}; skipping doc update.")
        return

    new_rows = "\n".join(
        f"| {u['date']} | `{u['package']}` | `{u['previous']}` | `{u['new']}` "
        f"| [PyPI](https://pypi.org/project/{u['package']}/{u['new']}/) |"
        for u in updates
    )
    updated_content = content.replace(
        marker,
        f"{marker}\n{new_rows}",
    )
    SDK_UPDATES_DOC.write_text(updated_content, encoding="utf-8")


def main() -> int:
    """Return 0 if no changes, 1 if any SDK was updated."""
    data: dict = json.loads(SDK_VERSIONS_FILE.read_text(encoding="utf-8"))
    now_iso = datetime.now(UTC).strftime("%Y-%m-%d")

    updates: list[dict[str, str]] = []
    any_changed = False

    for name, info in data["sdks"].items():
        package = info["pypi_package"]
        tracked = info.get("current_version")
        print(f"Checking {package} (tracked: {tracked or 'none'}) ...", end=" ")

        latest = fetch_latest_pypi_version(package)
        if latest is None:
            print("SKIP (fetch failed)")
            continue

        if latest == tracked:
            print(f"up-to-date ({latest})")
            continue

        print(f"UPDATE {tracked or 'none'} → {latest}")
        updates.append(
            {
                "date": now_iso,
                "package": package,
                "previous": tracked or "none",
                "new": latest,
            }
        )
        data["sdks"][name]["current_version"] = latest
        data["sdks"][name]["last_updated"] = now_iso
        any_changed = True

    data["last_checked"] = now_iso

    # Write sdk-versions.json
    SDK_VERSIONS_FILE.write_text(
        json.dumps(data, indent=2) + "\n",
        encoding="utf-8",
    )

    # Append to sdk-updates.md
    if updates:
        append_sdk_updates_doc(updates)

    # Summary
    if any_changed:
        print(f"\n✅ {len(updates)} SDK(s) updated. See sdk-versions.json and docs/sdk-updates.md.")
    else:
        print("\n✅ All SDKs are up-to-date.")

    return 1 if any_changed else 0


if __name__ == "__main__":
    sys.exit(main())
