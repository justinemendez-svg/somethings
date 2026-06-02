# AI Product Penetration Dashboard - APAC

Interactive HTML dashboard displaying AI product penetration data for Mitch Young's APAC organization, with integrated Gong conversation analysis.

## Features

### 📊 Core Dashboard
- **Account & Opportunity Data**: Pulls from Snowflake's CLEANSED.SALESFORCE tables
- **AI Product Tracking**: Copilot, AAA, QA, Forethought, Ultimate flags
- **Real-time Filtering**: Account, RVP, Market Segment, ARR Band
- **Live Metrics**: Accounts, Opportunities, Total ARR, Pipeline ARR, Gong Calls
- **Frozen Columns**: First 4 columns (RVP, FLM, AE, Account) stay visible when scrolling

### 🎙️ Gong Integration
- **Call Indicators**: Shows call count for opportunities with Gong data
- **Click to Analyze**: Click Gong indicators to see full call history
- **Call Details**: Date, duration, participants for each recorded call
- **Modal View**: Clean popup interface for Gong conversation analysis

### 💡 AI-Powered Insights
- **Auto-generated insights**: Top accounts without Copilot, active opps with calls
- **Clickable expansions**: Click insight to see full account list
- **Direct Salesforce links**: One-click access to account records

## Quick Start

### 1. Fetch Data
```bash
./update_dashboard.sh
```

This will:
1. Pull data from Snowflake (accounts, opps, AI products)
2. Fetch Gong call data for all opportunities
3. Generate the interactive HTML dashboard

### 2. Open Dashboard
```bash
open ai_penetration_dashboard.html
```

## Files

- **ai_penetration_dashboard.html** - The interactive dashboard (open in browser)
- **dashboard_data.json** - Latest data from Snowflake + Gong
- **fetch_data.py** - Python script to fetch data
- **generate_dashboard.py** - Generates HTML from template
- **update_dashboard.sh** - Quick update script

## Data Sources

### Snowflake Query
```sql
-- Pulls from:
- cleansed.salesforce.account_scd2
- cleansed.salesforce.opportunity_scd2
- cleansed.salesforce.user_scd2
- functional.gtm_sales_ops.role_attributes

-- Filters:
- RVP = 'Mitch Young'
- Open opportunities only (not closed, not stage 00/01)
- Account flags: has_copilot_c, has_aaa_c, has_qa_c, has_forethought_c
```

### Gong Data
- **Source**: `connections.gong.GongCache`
- **Data**: Call title, date, duration, participant count
- **Linked by**: Opportunity ID

## Dashboard Features

### Filters (Multi-select)
- Account Name
- RVP
- Market Segment
- ARR Band (< $10K, $10K-$50K, $50K-$100K, $100K-$500K, $500K+)

### Metrics (Live Updates)
- **Accounts**: Unique account count
- **Opportunities**: Unique opportunity count
- **Total ARR**: Sum of account ARR
- **Pipeline ARR**: Sum of opportunity ARR
- **Gong Calls**: Count of opps with recorded calls

### Table Columns
1. RVP
2. FLM
3. AE
4. Account Name (clickable → Salesforce)
5. Market Segment
6. Account ARR
7. TOP 3K (checkmark)
8. Has Copilot? (checkmark)
9. Has AAA? (checkmark)
10. Has QA? (checkmark)
11. Has Forethought? (checkmark)
12. Opportunity Name
13. Stage
14. Type
15. Opp ARR
16. Close Date
17. VP Forecast
18. **Gong Calls** (🎙️ indicator with count)

### Gong Modal
Click any Gong indicator (🎙️) to see:
- Total call count
- Full call history
- Per-call details: Title, Date, Duration, Participants
- Chronological order (newest first)

## Design

- **Zendesk Branding**: Inter font, Licorice/Coconut colors, #D1F470 accent
- **Responsive**: Works on laptop screens, optimized for 13-15" displays
- **Currency Format**: Smart notation (1.2K, 10.5M, 2.3B)
- **Compact Layout**: 13px base font, tight spacing for max data density
- **Frozen UI**: Header + first 4 columns stay visible during scroll

## Automation (Optional)

To enable daily auto-updates at 8am SGT (4pm PST):

```bash
# Add to crontab
0 8 * * * cd ~/path/to/ai_penetration_dashboard && ./update_dashboard.sh >> auto_update.log 2>&1
```

**Note**: Computer must be on and awake for cron to run.

## Requirements

- Python 3.11+ with venv
- Snowflake connection (Okta SSO)
- Salesforce CLI authenticated
- Gong cache populated (via `connections.gong`)

## Troubleshooting

### No data showing
```bash
# Check data file exists and has content
cat dashboard_data.json | head -20

# Re-fetch data
./update_dashboard.sh
```

### Gong calls not appearing
- Gong data only shows for opportunities with recorded calls
- Check `gongData` in dashboard_data.json
- Verify `connections.gong.GongCache` has data

### Filters not working
- Hard refresh browser (Cmd+Shift+R)
- Check browser console for JavaScript errors
- Verify dashboard_data.json is valid JSON

## Future Enhancements

- [ ] Export to CSV
- [ ] Date range filters
- [ ] Gong transcript snippets
- [ ] Competitor mentions from Gong
- [ ] AI sentiment analysis
- [ ] Historical trend charts

---

Built with ❤️ for Mitch Young's APAC team
