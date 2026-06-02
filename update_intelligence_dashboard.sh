#!/bin/bash
set -e

echo "==================================="
echo "Account Intelligence Dashboard"
echo "==================================="
echo ""

# Get the directory where this script lives
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
REPO_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Activate venv from repo root
source "$REPO_ROOT/venv/bin/activate"

# Change to dashboard directory
cd "$SCRIPT_DIR"

echo "Step 1/2: Fetching data from Snowflake + Gong..."
python3 fetch_account_intelligence.py

echo ""
echo "Step 2/2: Generating HTML dashboard..."
python3 generate_account_intelligence_dashboard.py

echo ""
echo "✓ Done!"
echo ""
echo "Open dashboard: open account_intelligence_dashboard.html"
