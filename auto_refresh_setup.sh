#!/bin/bash
# Auto-refresh setup for Account Intelligence Dashboard
# Run this script to set up automatic refresh every 8 hours

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="$SCRIPT_DIR/auto_refresh.log"

echo "=========================================="
echo "Auto-Refresh Setup"
echo "Account Intelligence Dashboard"
echo "=========================================="
echo ""

# Create log file if it doesn't exist
touch "$LOG_FILE"

# Get the absolute path to the update script
UPDATE_SCRIPT="$SCRIPT_DIR/update_intelligence_dashboard.sh"

# Create the cron job command
CRON_CMD="0 */8 * * * cd $SCRIPT_DIR && $UPDATE_SCRIPT >> $LOG_FILE 2>&1"

echo "This will add a cron job to refresh data every 8 hours."
echo ""
echo "Schedule: 12am, 8am, 4pm daily"
echo "Log file: $LOG_FILE"
echo ""
echo "Cron job command:"
echo "$CRON_CMD"
echo ""
echo "To install, run:"
echo ""
echo "  (crontab -l 2>/dev/null; echo '$CRON_CMD') | crontab -"
echo ""
echo "To verify:"
echo "  crontab -l | grep 'update_intelligence_dashboard'"
echo ""
echo "To remove later:"
echo "  crontab -l | grep -v 'update_intelligence_dashboard' | crontab -"
echo ""
echo "Note: Your computer must be ON and AWAKE for cron to run."
echo "=========================================="
