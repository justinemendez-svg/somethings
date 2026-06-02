# Quick Start: Account Intelligence Dashboard

## Generate the Dashboard (3 minutes)

```bash
cd ai_penetration_dashboard
./update_intelligence_dashboard.sh
```

This will:
1. Fetch all APAC accounts from Snowflake (~15 sec)
2. Analyze Gong calls (~1-2 min)
3. Generate HTML dashboard (~1 sec)

## Open the Dashboard

```bash
open account_intelligence_dashboard.html
```

Or just double-click the file.

## What You'll See

### Top Metrics Bar
- Total accounts count
- Total ARR across all accounts
- Open opportunities count
- Pipeline ARR

### Left Panel: Account List
- All accounts sorted by ARR
- Search box to filter by name, AE, or segment
- Click any account to view full intelligence

### Right Panel: Account Intelligence

When you select an account, you'll see:

1. **Account Overview** — ARR, health, segment, team assignments
2. **Buying Signal Score** — AI-powered 0-100 score with reasoning
3. **Role-Specific Actions** — Tailored for AE, SDR, CSM, Partner teams
4. **Product Adoption** — Visual heatmap showing which products they have
5. **Open Opportunities** — All opps with ARR, stage, close dates
6. **Team Notes** — Consolidated notes from AE, SDR, SE, ORR, CSM
7. **Gong Intelligence** — Latest call spotlight with key points and next steps

## Share the Dashboard

The HTML file is self-contained — email it, Slack it, or open on any device. No server, no auth, no dependencies.

## Regenerate with Fresh Data

```bash
./update_intelligence_dashboard.sh
```

Run this anytime to pull latest Snowflake data and Gong calls.

## Questions?

See `ACCOUNT_INTELLIGENCE_README.md` for full documentation.
