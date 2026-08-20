#!/usr/bin/env bash
# run.sh – Run the secure-agent-template sample flow.
#
# Usage:
#   ./scripts/run.sh           # real SDK calls (requires .env with valid credentials)
#   MOCK_SDK_CALLS=true ./scripts/run.sh   # mock mode (no Azure credentials needed)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# Activate virtual environment if present
VENV_ACTIVATE="${REPO_ROOT}/.venv/bin/activate"
if [ -f "${VENV_ACTIVATE}" ]; then
  # shellcheck disable=SC1090
  source "${VENV_ACTIVATE}"
fi

echo "==> Starting agent (MOCK_SDK_CALLS=${MOCK_SDK_CALLS:-false}) ..."
cd "${REPO_ROOT}"
python -m src.agent
