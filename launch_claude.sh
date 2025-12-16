#!/bin/bash
#
# launch_claude.sh
# Purpose: Launch Claude Code with the BRAID Manager environment ready
# Usage:   ./launch_claude.sh
#

# Get the directory where this script is located (raid_manager/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Work from parent directory (project root with data/ folder)
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Check if venv exists
VENV_PATH="${SCRIPT_DIR}/.venv"
if [[ ! -d "${VENV_PATH}" ]]; then
    echo "Warning: Virtual environment not found at ${VENV_PATH}"
    echo "Run: cd raid_manager && python3 -m venv .venv && pip install -r requirements.txt"
    echo ""
fi

# Load .env if it exists (for API keys)
ENV_FILE="${PROJECT_DIR}/.env"
if [[ -f "${ENV_FILE}" ]]; then
    set -a
    source "${ENV_FILE}"
    set +a

    if [[ -n "${ANTHROPIC_API_KEY}" ]]; then
        KEY_HINT="${ANTHROPIC_API_KEY: -8}"
        echo "API key loaded (ending in ...${KEY_HINT})"
    fi
fi

echo "Working directory: ${PROJECT_DIR}"
echo "Starting Claude Code..."
echo ""

# Launch Claude Code
claude
