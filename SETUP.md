# Account Intelligence Dashboard — Team Setup

AI-powered account analysis for the APAC GTM team: combines Snowflake pipeline data with Gong call intelligence into one interactive dashboard.

This repo has **two ways to use it**, depending on what you need.

---

## 🟢 Option A — Just view the dashboard (no setup, 1 minute)

The dashboard is a **single self-contained HTML file** with all the data already baked in. You don't need Python, Snowflake, or anything else — just a browser.

1. **Download the repo** — click the green **Code → Download ZIP** button on GitHub, then unzip it. (Or `git clone` if you prefer — see below.)
2. **Open the dashboard** — double-click `account_intelligence_dashboard.html`. It opens in your browser.

That's it. Search any account, click it, and see ARR, health, products, opps, team notes, and Gong call intelligence.

> The data in the checked-in dashboard is a snapshot from when it was last generated (see the date in the file header). To pull fresh data, use Option B.

### Clone instead of ZIP

```bash
git clone https://github.com/justinemendez-svg/somethings.git
cd somethings
open account_intelligence_dashboard.html      # macOS
# or: start account_intelligence_dashboard.html   (Windows)
```

---

## 🔵 Option B — Regenerate with fresh data (for maintainers)

To pull **new** Snowflake + Gong data and rebuild the dashboard, you need the
internal **`gtm-ops-claude`** repo, because these scripts import its shared
connectors (`connections.snowflake`, `connections.gong`).

**This folder is normally a subfolder of `gtm-ops-claude`** (`gtm-ops-claude/ai_penetration_dashboard/`). The scripts add the parent repo to the Python path automatically:

```python
sys.path.insert(0, str(Path(__file__).parent.parent))   # finds the gtm-ops-claude connectors
```

### Steps

1. Get access to the internal `gtm-ops-claude` repo and complete its first-time
   setup (Python venv, `.env`, Snowflake Okta login). See that repo's `CLAUDE.md`.
2. Place this dashboard folder inside it (or keep it where it already lives).
3. From the dashboard folder, run:

   ```bash
   ./update_intelligence_dashboard.sh
   ```

   This will:
   - Fetch APAC accounts from Snowflake (~15 sec)
   - Analyze Gong calls, last 30 days (~1–2 min)
   - Regenerate `account_intelligence_dashboard.html`

4. Open the refreshed dashboard:

   ```bash
   open account_intelligence_dashboard.html
   ```

### Auto-refresh (optional)

```bash
./install_auto_refresh.sh      # refreshes every 8 hours via cron
./uninstall_auto_refresh.sh    # stop it
```

> Your computer must be on and awake for cron to run.

---

## What's in this repo

| File | Purpose |
|------|---------|
| `account_intelligence_dashboard.html` | **The dashboard** — open this. Self-contained, data embedded. |
| `fetch_account_intelligence.py` | Fetches Snowflake data + analyzes Gong calls (needs `gtm-ops-claude`). |
| `generate_account_intelligence_dashboard.py` | Builds the interactive HTML from the fetched data. |
| `update_intelligence_dashboard.sh` | One-command refresh (fetch → generate). |
| `install_auto_refresh.sh` / `uninstall_auto_refresh.sh` | Set up / remove the 8-hour cron refresh. |
| `ACCOUNT_INTELLIGENCE_README.md` | Full feature docs, roadmap, troubleshooting. |
| `QUICK_START_INTELLIGENCE.md` | Short quick-start. |
| `AUTO_REFRESH_GUIDE.md` | Details on the auto-refresh cron setup. |

---

## ⚠️ Confidentiality

This dashboard contains **internal Zendesk sales data** — customer ARR, SFDC
account IDs, competitive intel, and Gong call content. **Keep this repo private
and do not share outside the authorized APAC GTM team.**

---

Questions? Ping Justine Mendez.
