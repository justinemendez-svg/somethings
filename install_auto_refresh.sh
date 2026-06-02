#!/bin/bash
# One-command installer for auto-refresh (every 8 hours)

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
LOG_FILE="$SCRIPT_DIR/auto_refresh.log"
UPDATE_SCRIPT="$SCRIPT_DIR/update_intelligence_dashboard.sh"

echo "=========================================="
echo "Installing Auto-Refresh (Every 8 Hours)"
echo "=========================================="
echo ""

# Create log file
touch "$LOG_FILE"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "update_intelligence_dashboard.sh"; then
    echo "⚠️  Auto-refresh already installed!"
    echo ""
    echo "Current schedule:"
    crontab -l | grep "update_intelligence_dashboard.sh"
    echo ""
    echo "To reinstall, first remove with:"
    echo "  crontab -l | grep -v 'update_intelligence_dashboard' | crontab -"
    exit 1
fi

# Add cron job
CRON_CMD="0 */8 * * * cd $SCRIPT_DIR && $UPDATE_SCRIPT >> $LOG_FILE 2>&1"
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo "✓ Auto-refresh installed!"
echo ""
echo "Schedule: Every 8 hours (12am, 8am, 4pm)"
echo "Next runs: 12:00am, 8:00am, 4:00pm"
echo "Log file: $LOG_FILE"
echo ""
echo "To check status:"
echo "  crontab -l | grep update_intelligence"
echo ""
echo "To view logs:"
echo "  tail -f $LOG_FILE"
echo ""
echo "To uninstall:"
echo "  crontab -l | grep -v 'update_intelligence_dashboard' | crontab -"
echo ""
echo "⚠️  Important: Your computer must be ON and AWAKE for cron to run!"
echo "=========================================="
