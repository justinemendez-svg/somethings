# 🚀 Quick Start - AI Penetration Dashboard

## What You Just Created

An interactive HTML dashboard showing:
- **AI Product Penetration** for Mitch Young's APAC org
- **Account & Opportunity Data** with filters
- **Gong Conversation Analysis** integrated inline
- **Real-time Metrics** that update as you filter

## Open the Dashboard

```bash
cd ai_penetration_dashboard
open ai_penetration_dashboard.html
```

## Key Features to Try

### 1. **Metrics at the Top**
- 5 live metrics: Accounts, Opportunities, Total ARR, Pipeline ARR, Gong Calls
- Updates instantly when you apply filters

### 2. **Interactive Filters**
- Account Name, RVP, Market Segment, ARR Band
- Multi-select: Hold Cmd/Ctrl to select multiple
- Click "Reset Filters" to clear all

### 3. **AI-Powered Insights** 💡
- Green insight cards show key opportunities
- **Click any insight** to expand and see account list
- Direct Salesforce links for each account

### 4. **Gong Call Integration** 🎙️
- Blue indicators show call count (e.g., "🎙️ 3")
- **Click the indicator** to see full call history in a modal
- Shows: Title, Date, Duration, Participants

### 5. **Data Table**
- **Frozen columns**: First 4 columns stay visible when scrolling
- **Frozen header**: Column headers stay at top when scrolling
- **Clickable account names**: Open in Salesforce
- **Checkmarks** for AI products (Copilot, AAA, QA, Forethought)

## Current Demo Data

- **27 unique accounts** (Acme Tech, GlobalSoft, etc.)
- **35 opportunities** (mix of New Business, Renewal, Expansion)
- **11 opportunities with Gong calls** (30% penetration)
- **AI Product flags**: 30% have Copilot, 25% have AAA

## Refresh Data

### Demo Data (Static)
```bash
../venv/bin/python create_demo_data.py
```

### Production Data (Snowflake)
```bash
../venv/bin/python fetch_data.py
```

**Note**: Production requires access to Snowflake tables:
- `CLEANSED.SALESFORCE.ACCOUNT_SCD2`
- `CLEANSED.SALESFORCE.OPPORTUNITY_SCD2`
- `FUNCTIONAL.GTM_SALES_OPS.ROLE_ATTRIBUTES`

## Files

| File | Purpose |
|------|---------|
| `ai_penetration_dashboard.html` | **Main dashboard** - Open this! |
| `dashboard_data.json` | Data file (loaded by HTML) |
| `create_demo_data.py` | Generate demo data |
| `fetch_data.py` | Fetch real Snowflake data (requires access) |
| `generate_dashboard.py` | Regenerate HTML |
| `update_dashboard.sh` | Quick update script |

## Customization

### Change Filters
Edit `generate_dashboard.py`, search for "filter-group" section

### Add Metrics
Edit `generate_dashboard.py`, search for "metrics-grid"

### Modify Table Columns
Edit `generate_dashboard.py`, search for "<thead>" section

### Update Colors
Edit the `<style>` section:
- Primary accent: `#d1f470` (Zendesk lime green)
- Background: `#f9fafb`
- Text: `#03363d` (Licorice)

## Troubleshooting

### Dashboard shows no data
```bash
# Check data file exists
cat dashboard_data.json | head -20

# Regenerate
../venv/bin/python create_demo_data.py
```

### Filters not working
- Hard refresh browser: `Cmd+Shift+R` (Mac) or `Ctrl+Shift+F5` (Windows)
- Check browser console for errors (F12)

### Gong modal won't open
- Make sure you're clicking the blue 🎙️ indicator
- Check that `gongData` exists in `dashboard_data.json`

## Next Steps

1. **Share with team**: Send the HTML file + JSON file
2. **Connect to Snowflake**: Update `fetch_data.py` with your credentials
3. **Add more insights**: Edit `updateInsights()` in the HTML
4. **Export feature**: Add CSV download button
5. **Automate**: Set up daily cron job to refresh data

---

Built for Mitch Young's APAC team | Questions? Check README.md
