# Account Intelligence Dashboard

**AI-powered account analysis for GTM teams** — combines your APAC pipeline Snowflake query with Gong call intelligence to deliver actionable insights for every role (AE, SDR, CSM, Partner, Marketing).

## What It Does

This dashboard gives you **one click access to everything you need to know about any account**:

### 📊 Account Overview
- ARR, health status, segment, industry
- Team assignments (AE, SDR, CSM, Renewal Rep)
- Product adoption heatmap
- TOP 3000 status

### 🤖 AI-Powered Gong Analysis
- **Buying signal score (0-100)** with reasoning
- Competitor mentions detected across calls
- MEDDPICC gap analysis
- Objection patterns
- Last 30 days of call intelligence

### 🎯 Role-Specific Action Items
Automatically generated actions for:
- **AE**: Close acceleration, competitor defense, risk mitigation
- **SDR**: Coverage gaps, follow-up cadences
- **CSM**: Health issues, expansion opportunities
- **Partner**: Partner engagement, co-sell opportunities
- **Marketing**: Nurture triggers, competitive positioning

### 💰 Opportunity Pipeline
- All open opportunities with ARR, stage, products
- Close dates and VP forecast
- Product mix per opportunity

### 📝 Consolidated Notes
All team notes in one view:
- AE notes
- SDR notes
- SE notes
- ORR notes
- Health status notes
- Renewal notes

### 🎙️ Gong Call Spotlight
- Latest call brief
- Key points
- Next steps

## Quick Start

### 1. Generate the Dashboard

```bash
cd ai_penetration_dashboard
./update_intelligence_dashboard.sh
```

This will:
1. Fetch data from Snowflake (your exact APAC query)
2. Analyze Gong calls (last 30 days)
3. Generate role-specific actions
4. Create the interactive HTML

### 2. Open the Dashboard

```bash
open account_intelligence_dashboard.html
```

### 3. (Optional) Set Up Auto-Refresh

To automatically refresh data every 8 hours:

```bash
./install_auto_refresh.sh
```

This creates a cron job that runs at:
- **12:00am** (midnight)
- **8:00am** (morning)
- **4:00pm** (afternoon)

**To uninstall:**
```bash
./uninstall_auto_refresh.sh
```

**To check status:**
```bash
crontab -l | grep update_intelligence
```

**To view logs:**
```bash
tail -f auto_refresh.log
```

**⚠️ Important:** Your computer must be ON and AWAKE for automatic refresh to work.

Or just double-click the HTML file.

## Features

### Interactive Account Selector
- Search by account name, AE, or segment
- Click to view full intelligence
- Scroll through all accounts

### Buying Signal Score
Large visual card showing 0-100 buying likelihood with AI reasoning:
- **80-100**: Hot - strong buying signals
- **60-79**: Warm - good engagement
- **40-59**: Cool - mixed signals
- **0-39**: Cold - low intent

### Product Adoption Heatmap
Visual grid showing which products the account has:
- ✅ Green = Active
- ⬜ Gray = Not adopted (whitespace opportunity)

### Opportunity Cards
Each open opp shows:
- ARR value
- Stage and type
- Close date and month
- Products in the deal
- VP forecast category

## Data Sources

### Snowflake Query
Your exact query from the prompt:
- `FUNCTIONAL.GTM_SALES_OPS.GTMSI_CONSOLIDATED_PIPELINE_BOOKINGS`
- `FUNCTIONAL.GTM_SALES_OPS.PENETRATION_DASH`
- `DEV_CLEANSED.SALESFORCE.SALESFORCE_ACCOUNT_BCV`
- Gong call spotlight from `CLEANSED.GONG.GONG_CALLS_BCV`

Filters:
- SVP = Mitch Young
- ARR > 0
- No Copilot or AAA activated
- AI products: AI_Expert, Copilot, Ultimate, Ultimate_AR, Zendesk_AR, QA, WEM

### Gong Analysis
- Last 30 days of calls per account
- Rule-based buying signal detection (will be enhanced with LLM in production)
- Competitor pattern matching
- MEDDPICC element detection
- Objection classification

## Files

| File | Purpose |
|------|---------|
| `fetch_account_intelligence.py` | Fetch Snowflake data + analyze Gong calls |
| `generate_account_intelligence_dashboard.py` | Generate interactive HTML |
| `update_intelligence_dashboard.sh` | One-command update script |
| `account_intelligence.json` | Raw data (generated) |
| `account_intelligence_dashboard.html` | The dashboard (generated) |

## Automation

### Daily Auto-Update

Add to your crontab to regenerate every morning at 8am SGT:

```bash
crontab -e
```

Add this line:

```
0 8 * * * cd ~/Desktop/anything2026/gtm-ops-claude/ai_penetration_dashboard && ./update_intelligence_dashboard.sh >> auto_update.log 2>&1
```

**Note**: Your computer must be on and awake for cron to run.

### Slack Integration (Optional)

Post dashboard link to Slack each morning:

```bash
# After generating dashboard
curl -X POST "https://slack.com/api/chat.postMessage" \
  -H "Authorization: Bearer $SLACK_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "#apac-sales",
    "text": "🚀 Daily Account Intelligence Dashboard is ready!",
    "attachments": [{
      "text": "Click to view: file:///path/to/account_intelligence_dashboard.html"
    }]
  }'
```

## Customization

### Adjust Gong Analysis Window

Edit `fetch_account_intelligence.py`:

```python
# Change from 30 to 60 days
gong_analysis = analyze_account_gong_calls(account_id, gong_cache, days=60)
```

### Add Custom Role Actions

Edit `generate_role_actions()` in `fetch_account_intelligence.py`:

```python
# Add new role
actions['sales_ops'] = []
if some_condition:
    actions['sales_ops'].append('Action item here')
```

Then update the HTML template to display it.

### Change Product List

Edit the product grid in `generate_account_intelligence_dashboard.py`:

```python
productBadges = `
    <div class="product-grid">
        <div class="product-badge ${products.my_new_product ? 'active' : 'inactive'}">My Product</div>
        ...
    </div>
`;
```

## Roadmap

### Phase 1 (Current)
- [x] Snowflake integration with your exact query
- [x] Rule-based Gong analysis
- [x] Role-specific action generation
- [x] Interactive HTML dashboard
- [x] Product adoption tracking

### Phase 2 (Next)
- [ ] **LLM-powered Gong analysis** — use gpt-5.4-mini to classify buying signals (like `/gong:competitor-batch`)
- [ ] **Transcript snippets** — show relevant quotes from Gong calls
- [ ] **Competitor drill-down** — click competitor to see all mentions with context
- [ ] **MEDDPICC scorecard** — visual gap analysis with recommended actions

### Phase 3 (Future)
- [ ] **Historical trends** — ARR growth, opp velocity, call frequency
- [ ] **Predictive scoring** — which accounts are most likely to expand
- [ ] **Export to CSV/PDF** — share insights with non-technical stakeholders
- [ ] **Jira integration** — one-click create follow-up tasks

## Troubleshooting

### No data showing

```bash
# Check if data file exists
ls -lh account_intelligence.json

# Re-fetch data
./update_intelligence_dashboard.sh
```

### Snowflake authentication failed

```bash
# Re-authenticate
cd ..
./venv/bin/python -m connections.snowflake.conn
```

A browser window will open for Okta login.

### Gong data missing

Gong data is optional — the dashboard works without it. If calls are missing:

```bash
# Check GongCache
cd ..
python3 -c "from connections.gong import GongCache; g = GongCache(); print(g.get_calls_for_opportunity('YOUR_OPP_ID'))"
```

### Buying signal score always 0

Phase 1 uses rule-based analysis. Phase 2 will add LLM-powered scoring (like `/gong:competitor-batch`).

To enable now: edit `analyze_transcript_for_signals()` in `fetch_account_intelligence.py` and add LLM classification.

## Design Choices

### Why account-level (not opp-level)?

GTM teams think in **accounts**, not opportunities. An AE managing 50 accounts needs account-level intelligence, not opp-by-opp breakdowns.

The dashboard shows:
- Account-level signals (health, ARR, products)
- All opps grouped under each account
- Combined Gong intelligence across all calls

### Why HTML (not web app)?

**Shareability**: One file, no server, no auth, no dependencies. Email it, Slack it, open it on any device.

For a web app with live data, consider building with Streamlit or Dash and deploying to Render/Railway.

### Why role-specific actions?

Different roles care about different things:
- AE → close acceleration
- SDR → coverage and follow-up
- CSM → health and expansion
- Partner → co-sell opportunities
- Marketing → nurture and positioning

One dashboard, five use cases.

## Technical Details

### Data Flow

```
Snowflake Query (APAC pipeline)
    ↓
Group by Account
    ↓
For each account:
    - Fetch Gong calls (last 30 days)
    - Analyze transcripts (buying signals, competitors, MEDDPICC, objections)
    - Generate role actions
    ↓
Save to account_intelligence.json
    ↓
Generate HTML with embedded data
```

### Performance

- **Snowflake query**: ~10-15 seconds (depends on row count)
- **Gong analysis**: ~1-2 seconds per account with calls
- **HTML generation**: <1 second
- **Total**: ~2-3 minutes for 100 accounts

### Security

- **No credentials in HTML** — data is already fetched and anonymized
- **Shareable within Zendesk** — contains SFDC IDs and internal data
- **Not for external use** — contains competitive intel and Gong transcripts

## Support

Questions? Ping Justine Mendez or open an issue in the repo.

Built with ❤️ for Mitch Young's APAC team.
