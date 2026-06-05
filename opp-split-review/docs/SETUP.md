# Setup — MSS Opp Split Review dashboard

This is a one-time setup (~5–10 minutes). After it's done, anyone you share the
link with who has a Salesforce login can use the **Refresh from Salesforce**
button. No server, no install, nothing stored anywhere — the data is fetched
live in their browser using their own Salesforce session.

---

## Step 1 — Create a Salesforce Connected App

You (or a Salesforce admin) do this once.

1. In Salesforce: **Setup → App Manager → New Connected App**.
2. Name it e.g. `Opp Split Review Dashboard`. Add a contact email.
3. Tick **Enable OAuth Settings**.
4. **Callback URL** — this is the page's address. Use BOTH while testing:
   - `https://<your-github-username>.github.io/<repo-name>/` (the live link)
   - `http://localhost:8000/` (for local testing)
5. **OAuth Scopes** — add:
   - *Manage user data via APIs (api)*
   - *Perform requests at any time (refresh_token, offline_access)*
6. **Enable PKCE** (Require Proof Key for Code Exchange). Leave
   *Require Secret for Web Server Flow* **unchecked** — this app has no secret.
7. Save. Open the app → **Manage Consumer Details** → copy the **Consumer Key**.

> The Consumer Key is **not a secret**. It is safe to commit and serve publicly.

---

## Step 2 — Fill in `config.js`

Open `docs/config.js` and set:

- `loginUrl` — your Salesforce domain, e.g.
  `https://yourcompany.my.salesforce.com` (or the `--sandbox` URL for a sandbox).
- `consumerKey` — paste the Consumer Key from Step 1.
- `closedWonStages` — match your org's exact Stage value(s), e.g.
  `["Closed Won"]` or `["08 - Closed Won"]`.
- `splitObject` — `"OpportunitySplit"` (has %/amount) or
  `"OpportunityTeamMember"` (roles only). Most commission reviews use the former.

`excludeNames` already excludes `Sam Hansen` and `Digital Renewals` per the
original report.

---

## Step 3 — Publish with GitHub Pages (the shareable link)

1. Push this repo to GitHub (see the repo's top-level `README.md`).
2. On GitHub: **Settings → Pages**.
3. **Source:** Deploy from a branch → **Branch:** `main` → **Folder:** `/docs`.
4. Save. After a minute your link is:
   `https://<your-github-username>.github.io/<repo-name>/`
5. Share that link. Recipients click **Refresh from Salesforce**, sign in with
   their own Salesforce account, and see last month's review worklist.

---

## How the analysis works

- Pulls every **Closed/Won** opportunity with a **Close Date in last month**.
- Reads each opp's split members (excluding the configured names).
- **Flags** an opp when it has a **primary + coverage** pair of roles
  (a role and its `… - Coverage` counterpart), or when exactly **2 members**
  share the split — the cases Sales Ops reviews by hand today.
- For each flagged opp it shows close date, both reps, roles, and split
  %/amount side by side, plus a blank **"Retain?"** field for the analyst to
  fill after checking the LOA / on/off-boarding ticket (effective date vs close
  date). Export everything to CSV with one click.

> The retain decision stays manual on purpose: the effective dates live in
> Sales Ops tickets the dashboard can't reach. It surfaces exactly what needs a
> human eyeball, sorted so duplicates are obvious.

---

## Local testing (optional)

```bash
cd docs
python3 -m http.server 8000
# open http://localhost:8000/
```

Make sure `http://localhost:8000/` is one of the Connected App callback URLs.
