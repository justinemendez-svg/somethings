# Auto-Refresh Setup Guide

## Overview

The Account Intelligence Dashboard can automatically refresh data every 8 hours using a cron job. This keeps your dashboard up-to-date without manual intervention.

## Quick Install

```bash
cd ai_penetration_dashboard
./install_auto_refresh.sh
```

Done! Data will now refresh automatically every 8 hours.

## Schedule

The dashboard refreshes at:
- **12:00am** (midnight) - Start of day data
- **8:00am** (morning) - Morning update
- **4:00pm** (afternoon) - End of day update

## What Happens During Auto-Refresh

1. **Fetches data from Snowflake** - All 3,000+ APAC accounts
2. **Analyzes Gong calls** - Buying signals, competitors, MEDDPICC
3. **Generates role actions** - AE, SDR, CSM, Partner, Marketing
4. **Updates HTML** - Fresh dashboard ready to view

**Duration:** ~3-5 minutes per refresh

## Checking Status

### Is auto-refresh installed?

```bash
crontab -l | grep update_intelligence
```

**Expected output:**
```
0 */8 * * * cd /path/to/ai_penetration_dashboard && ./update_intelligence_dashboard.sh >> auto_refresh.log 2>&1
```

**No output?** Auto-refresh is not installed.

### View recent logs

```bash
cd ai_penetration_dashboard
tail -20 auto_refresh.log
```

**Expected output:**
```
Fetching APAC pipeline data from Snowflake...
✓ Fetched 3243 rows
✓ Processed 3047 accounts
✓ Dashboard generated
```

### Watch live refresh

```bash
tail -f auto_refresh.log
```

Press `Ctrl+C` to stop watching.

## Uninstalling

```bash
./uninstall_auto_refresh.sh
```

This removes the cron job. The dashboard remains, but won't auto-update.

## Troubleshooting

### Auto-refresh not running

**Cause:** Computer was asleep or off during scheduled time.

**Solution:** Cron jobs only run when computer is ON and AWAKE. Consider:
- Adjusting Energy Saver settings to prevent sleep
- Running on a server instead of laptop
- Manually refreshing: `./update_intelligence_dashboard.sh`

### Check if last refresh succeeded

```bash
tail -1 auto_refresh.log
```

**Look for:**
- ✓ Success messages
- ✗ Error messages

### Re-run manually to test

```bash
./update_intelligence_dashboard.sh
```

If this works, cron will work (when computer is awake).

### Snowflake authentication failed

**Symptom:** Cron logs show "Okta login" messages

**Cause:** Snowflake token expired

**Solution:**
1. Manually run: `./update_intelligence_dashboard.sh`
2. Complete Okta login in browser
3. Token will be cached for future cron runs

### Check cron daemon is running

```bash
ps aux | grep cron
```

**Should see:** `cron` or `cron` daemon running

### Force a refresh now

```bash
./update_intelligence_dashboard.sh
```

Then check the dashboard - timestamp should be current.

## Advanced Configuration

### Change refresh frequency

**Edit cron schedule:**
```bash
crontab -e
```

**Change the schedule:**
- `0 */8 * * *` = Every 8 hours (current)
- `0 */6 * * *` = Every 6 hours
- `0 */4 * * *` = Every 4 hours
- `0 */12 * * *` = Every 12 hours (2x per day)
- `0 8 * * *` = Once daily at 8am

**Cron schedule format:**
```
* * * * *
│ │ │ │ │
│ │ │ │ └─── Day of week (0-7, 0 and 7 = Sunday)
│ │ │ └───── Month (1-12)
│ │ └─────── Day of month (1-31)
│ └───────── Hour (0-23)
└─────────── Minute (0-59)
```

### Multiple refresh times

To refresh at specific times (e.g., 8am, 12pm, 6pm):

```bash
crontab -e
```

Add multiple lines:
```
0 8 * * * cd /path/to/ai_penetration_dashboard && ./update_intelligence_dashboard.sh >> auto_refresh.log 2>&1
0 12 * * * cd /path/to/ai_penetration_dashboard && ./update_intelligence_dashboard.sh >> auto_refresh.log 2>&1
0 18 * * * cd /path/to/ai_penetration_dashboard && ./update_intelligence_dashboard.sh >> auto_refresh.log 2>&1
```

### Email notifications on completion

Add to cron job:
```bash
MAILTO=your.email@zendesk.com
0 */8 * * * cd /path/to/ai_penetration_dashboard && ./update_intelligence_dashboard.sh >> auto_refresh.log 2>&1
```

macOS may require postfix configuration for email to work.

### Rotate log file

Prevent log from growing too large:

```bash
# Keep only last 1000 lines
tail -1000 auto_refresh.log > auto_refresh.log.tmp && mv auto_refresh.log.tmp auto_refresh.log
```

Add this to a weekly cron:
```
0 0 * * 0 cd /path/to/ai_penetration_dashboard && tail -1000 auto_refresh.log > auto_refresh.log.tmp && mv auto_refresh.log.tmp auto_refresh.log
```

## Server Deployment (24/7 Refresh)

For always-on auto-refresh, deploy to a server:

### Option 1: AWS EC2 / Azure VM

1. Launch small instance (t2.micro is enough)
2. Install Python, dependencies
3. Clone repo
4. Set up cron
5. Dashboard URL via file share or S3/Azure Blob

### Option 2: macOS Server / Mac Mini

1. Keep Mac always on
2. Prevent sleep: System Preferences → Energy Saver → "Prevent computer from sleeping"
3. Install as above

### Option 3: GitHub Actions (Free)

Create `.github/workflows/refresh.yml`:
```yaml
name: Refresh Dashboard
on:
  schedule:
    - cron: '0 */8 * * *'
jobs:
  refresh:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Refresh data
        run: cd ai_penetration_dashboard && ./update_intelligence_dashboard.sh
      - name: Commit changes
        run: |
          git config user.name github-actions
          git add ai_penetration_dashboard/*.html
          git commit -m "Auto-refresh dashboard"
          git push
```

**Benefit:** Runs even when your laptop is off. View via GitHub Pages.

## Best Practices

1. **Check logs weekly** - Ensure refresh is working
2. **Monitor Snowflake** - Watch for query cost/performance
3. **Keep computer awake** during refresh times (if using local cron)
4. **Test after macOS updates** - Cron can sometimes break
5. **Backup dashboard** before major changes

## Files

- `install_auto_refresh.sh` - One-command installer
- `uninstall_auto_refresh.sh` - Remove auto-refresh
- `auto_refresh_setup.sh` - Manual setup instructions
- `auto_refresh.log` - Log file (created after first run)
- `update_intelligence_dashboard.sh` - Main refresh script

## Support

Questions? See `ACCOUNT_INTELLIGENCE_README.md` or ping Justine Mendez.
