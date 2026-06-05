# MSS Opp Split Review — dashboard

A shareable, no-install dashboard for the monthly **Opportunity Split Review**:
it pulls **last month's Closed/Won opportunities** live from Salesforce, flags
the ones with a **primary + coverage split** (the cases Sales Ops reviews by
hand), and lays them out so the analyst can decide who to retain before the
commission cutoff.

- **Shareable link** — hosted on GitHub Pages. Recipients need **no GitHub account**.
- **Live "Refresh from Salesforce" button** — data is fetched in the browser
  using the viewer's own Salesforce login (OAuth PKCE). **No server, no stored
  credentials, read-only.**
- **CSV export** for record-keeping.

## What it does

Each refresh:
1. Queries Closed/Won opps with a Close Date in the previous month.
2. Reads each opp's split members (excludes `Sam Hansen`, `Digital Renewals`).
3. **Flags** opps that have a role + its `… - Coverage` counterpart, or exactly
   two split members — the duplicate primary/coverage cases.
4. Shows close date, both reps, roles, split %/amount, and a blank **Retain?**
   field for the analyst to fill after checking the LOA / on/off-boarding ticket.

The retain decision stays manual by design — those effective dates live in
Sales Ops tickets the dashboard can't reach. See [`docs/SETUP.md`](docs/SETUP.md).

## Setup

Full steps in **[docs/SETUP.md](docs/SETUP.md)**:
1. Create a Salesforce Connected App (one time).
2. Paste your `consumerKey` + `loginUrl` into [`docs/config.js`](docs/config.js).
3. Enable GitHub Pages (Settings → Pages → `main` / `/docs`) → share the link.

## Project layout

```
docs/
  index.html   # the dashboard UI
  app.js       # OAuth + Salesforce query + 2-rep-split analysis + render
  config.js    # <- the only file you edit: your Salesforce details
  SETUP.md     # one-time setup guide
```

## Notes

- Pure static site — no build step, no dependencies.
- Adjust `closedWonStages` and `splitObject` in `config.js` to match your org.
