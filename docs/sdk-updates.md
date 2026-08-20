# SDK Update History

This file is updated automatically by the
[sdk-watch](./../.github/workflows/sdk-watch.yml) GitHub Actions workflow
whenever a new version of a tracked SDK is detected.

It can also be updated manually by running:

```bash
python scripts/check_sdk_updates.py
```

---

## How to interpret this file

Each entry in the **Changelog** section below records:

- **Date** – when the update was detected (UTC, YYYY-MM-DD).
- **Package** – the Python package name on PyPI.
- **Previous version** – the last version recorded in `sdk-versions.json`
  before this update.
- **New version** – the version now available on PyPI.
- **Release URL** – link to the PyPI release or changelog.

Review the linked changelog before merging the auto-generated PR to check for
breaking changes or deprecations that may affect your agent code.

---

## Changelog

| Date | Package | Previous | New | Release URL |
|---|---|---|---|---|
<!-- sdk-watch: new rows inserted after this line -->
| 2026-07-09 | `azure-purview-catalog` | `none` | `1.0.0b4` | [PyPI](https://pypi.org/project/azure-purview-catalog/1.0.0b4/) |
| 2026-07-09 | `azure-purview-scanning` | `none` | `1.0.0b2` | [PyPI](https://pypi.org/project/azure-purview-scanning/1.0.0b2/) |
| 2026-07-09 | `msgraph-sdk` | `none` | `1.58.0` | [PyPI](https://pypi.org/project/msgraph-sdk/1.58.0/) |
| 2026-07-09 | `azure-identity` | `none` | `1.25.3` | [PyPI](https://pypi.org/project/azure-identity/1.25.3/) |
