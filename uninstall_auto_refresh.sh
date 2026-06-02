#!/bin/bash
# Uninstall auto-refresh

echo "=========================================="
echo "Uninstalling Auto-Refresh"
echo "=========================================="
echo ""

# Check if cron job exists
if ! crontab -l 2>/dev/null | grep -q "update_intelligence_dashboard.sh"; then
    echo "ℹ️  Auto-refresh not installed (no cron job found)"
    exit 0
fi

echo "Current cron job:"
crontab -l | grep "update_intelligence_dashboard.sh"
echo ""
echo "Removing..."

# Remove cron job
crontab -l | grep -v 'update_intelligence_dashboard' | crontab -

echo ""
echo "✓ Auto-refresh uninstalled!"
echo ""
echo "To verify:"
echo "  crontab -l"
echo ""
echo "To reinstall:"
echo "  ./install_auto_refresh.sh"
echo "=========================================="
