#!/usr/bin/env bash
# setup.sh – Bootstrap the development environment for secure-agent-template.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "==> Setting up secure-agent-template in ${REPO_ROOT}"

# ── Python version check ──────────────────────────────────────────────────────
PYTHON=$(command -v python3 || command -v python)
PY_VERSION=$("${PYTHON}" -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "==> Python version: ${PY_VERSION}"

# ── Virtual environment ───────────────────────────────────────────────────────
VENV_DIR="${REPO_ROOT}/.venv"
if [ ! -d "${VENV_DIR}" ]; then
  echo "==> Creating virtual environment at .venv ..."
  "${PYTHON}" -m venv "${VENV_DIR}"
fi

# shellcheck disable=SC1091
source "${VENV_DIR}/bin/activate"
echo "==> Virtual environment activated"

# ── Install dependencies ──────────────────────────────────────────────────────
echo "==> Installing dependencies ..."
pip install --quiet --upgrade pip
pip install --quiet -e "${REPO_ROOT}[dev]"

# ── Copy .env.example if .env is missing ─────────────────────────────────────
if [ ! -f "${REPO_ROOT}/.env" ]; then
  cp "${REPO_ROOT}/.env.example" "${REPO_ROOT}/.env"
  echo "==> Created .env from .env.example — fill in your Azure credentials."
else
  echo "==> .env already exists, skipping copy."
fi

echo ""
echo "==> Setup complete!"
echo "    Activate the environment:  source .venv/bin/activate"
echo "    Run the agent (mock mode): MOCK_SDK_CALLS=true python -m src.agent"
echo "    Run tests:                 pytest tests/ -v"
