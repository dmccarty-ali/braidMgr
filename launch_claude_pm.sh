#!/bin/bash
#
# launch_claude_pm.sh
# Purpose: Launch Claude Code in PM-friendly mode (less technical, pre-approved operations)
# Usage:   ./launch_claude_pm.sh
#

# Get the directory where this script is located (raid_manager/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Work from parent directory (project root with data/ folder)
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

# Load .env if it exists (for API keys)
ENV_FILE="${PROJECT_DIR}/.env"
if [[ -f "${ENV_FILE}" ]]; then
    set -a
    source "${ENV_FILE}"
    set +a
fi

echo "BRAID Manager - PM Mode"
echo "======================="
echo ""
echo "Available commands:"
echo "  /raid-meeting-update  - Process meeting notes into BRAID updates"
echo "  /raid-active          - Show open items"
echo "  /raid-summary         - Project health summary"
echo ""

# Launch Claude Code with pre-approved tools for BRAID operations
claude --allowedTools "Read" \
       --allowedTools "Write(data/*)" \
       --allowedTools "Edit(data/*)" \
       --allowedTools "Bash(raid_manager/.venv/bin/python:*)" \
       --allowedTools "Bash(cat:*)" \
       --allowedTools "Bash(ls:*)" \
       --allowedTools "Bash(grep:*)"
