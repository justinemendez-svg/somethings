/* ============================================================================
 * MSS Opp Split Review — app logic
 * Runs entirely in the browser. Uses Salesforce OAuth 2.0 PKCE (no secret,
 * no server). Pulls last month's Closed/Won opps + their split members,
 * flags opps that have a primary + coverage pair, and renders a worklist.
 * ========================================================================== */
(function () {
  "use strict";

  const CFG = window.OPP_SPLIT_CONFIG;
  const $ = (id) => document.getElementById(id);
  const TOKEN_KEY = "ossr_token";
  const PKCE_KEY = "ossr_pkce_verifier";

  let STATE = { rows: [], instanceUrl: null, period: null };

  // ---- tiny helpers ---------------------------------------------------------
  const fmtMoney = (n) =>
    n == null ? "—" : n.toLocaleString(undefined, { style: "currency", currency: "USD", maximumFractionDigits: 0 });
  const fmtDate = (s) => (s ? new Date(s + "T00:00:00").toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" }) : "—");
  const esc = (s) => String(s == null ? "" : s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  function setStatus(msg, isErr) {
    const el = $("status");
    el.innerHTML = msg;
    el.classList.remove("hidden");
    el.classList.toggle("err", !!isErr);
  }

  // ---- last-month date range ------------------------------------------------
  function lastMonthRange() {
    const now = new Date();
    const start = new Date(now.getFullYear(), now.getMonth() - 1, 1);
    const end = new Date(now.getFullYear(), now.getMonth(), 0); // last day prev month
    const iso = (d) => d.toISOString().slice(0, 10);
    const label = start.toLocaleDateString(undefined, { month: "long", year: "numeric" });
    return { start: iso(start), end: iso(end), label };
  }

  // ---- OAuth 2.0 PKCE --------------------------------------------------------
  async function sha256(str) {
    const buf = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(str));
    return btoa(String.fromCharCode(...new Uint8Array(buf))).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
  }
  function randStr(len) {
    const a = new Uint8Array(len);
    crypto.getRandomValues(a);
    return Array.from(a, (b) => ("0" + (b & 0xff).toString(16)).slice(-2)).join("");
  }

  async function beginLogin() {
    const verifier = randStr(48);
    sessionStorage.setItem(PKCE_KEY, verifier);
    const challenge = await sha256(verifier);
    const p = new URLSearchParams({
      response_type: "code",
      client_id: CFG.consumerKey,
      redirect_uri: CFG.redirectUri,
      scope: "api refresh_token",
      code_challenge: challenge,
      code_challenge_method: "S256",
    });
    window.location.href = `${CFG.loginUrl}/services/oauth2/authorize?${p.toString()}`;
  }

  async function completeLoginIfReturning() {
    const params = new URLSearchParams(window.location.search);
    const code = params.get("code");
    if (!code) return false;
    const verifier = sessionStorage.getItem(PKCE_KEY);
    history.replaceState({}, "", CFG.redirectUri); // clean ?code= from URL
    if (!verifier) return false;

    const body = new URLSearchParams({
      grant_type: "authorization_code",
      code,
      client_id: CFG.consumerKey,
      redirect_uri: CFG.redirectUri,
      code_verifier: verifier,
    });
    const res = await fetch(`${CFG.loginUrl}/services/oauth2/token`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body,
    });
    if (!res.ok) throw new Error("Token exchange failed: " + (await res.text()));
    const tok = await res.json();
    sessionStorage.setItem(TOKEN_KEY, JSON.stringify(tok));
    return true;
  }

  function getToken() {
    const raw = sessionStorage.getItem(TOKEN_KEY);
    return raw ? JSON.parse(raw) : null;
  }
  function signOut() {
    sessionStorage.removeItem(TOKEN_KEY);
    location.reload();
  }

  // ---- Salesforce query ------------------------------------------------------
  async function soql(instanceUrl, accessToken, query) {
    const url = `${instanceUrl}/services/data/${CFG.apiVersion}/query?q=${encodeURIComponent(query)}`;
    const out = [];
    let next = url;
    while (next) {
      const res = await fetch(next.startsWith("http") ? next : instanceUrl + next, {
        headers: { Authorization: "Bearer " + accessToken },
      });
      if (!res.ok) throw new Error("Salesforce query failed: " + (await res.text()));
      const j = await res.json();
      out.push(...j.records);
      next = j.done ? null : j.nextRecordsUrl;
    }
    return out;
  }

  function buildQuery(range) {
    const stages = CFG.closedWonStages.map((s) => `'${s.replace(/'/g, "\\'")}'`).join(",");
    // Pull opps in range, with their split members + roles via the child relationship.
    // OpportunitySplit child relationship is "OpportunitySplits"; team members "OpportunityTeamMembers".
    const child =
      CFG.splitObject === "OpportunityTeamMember"
        ? `(SELECT Id, TeamMemberRole, User.Name FROM OpportunityTeamMembers)`
        : `(SELECT Id, SplitPercentage, SplitAmount, SplitOwnerName, SplitType.MasterLabel FROM OpportunitySplits)`;
    return (
      `SELECT Id, Name, CloseDate, Amount, StageName, Account.Name, ${child} ` +
      `FROM Opportunity ` +
      `WHERE StageName IN (${stages}) ` +
      `AND CloseDate >= ${range.start} AND CloseDate <= ${range.end} ` +
      `ORDER BY CloseDate DESC`
    );
  }

  // ---- analysis: flag primary + coverage pairs ------------------------------
  function analyze(records) {
    const rows = records.map((opp) => {
      const childKey = CFG.splitObject === "OpportunityTeamMember" ? "OpportunityTeamMembers" : "OpportunitySplits";
      const raw = (opp[childKey] && opp[childKey].records) || [];
      const members = raw
        .map((m) => {
          if (CFG.splitObject === "OpportunityTeamMember") {
            return { name: m.User && m.User.Name, role: m.TeamMemberRole, pct: null, amount: null };
          }
          return {
            name: m.SplitOwnerName,
            role: m.SplitType && m.SplitType.MasterLabel,
            pct: m.SplitPercentage,
            amount: m.SplitAmount,
          };
        })
        .filter((m) => m.name && !CFG.excludeNames.includes(m.name));

      // A "2-rep" review case: a role and its " - Coverage" counterpart both present.
      const roles = members.map((m) => (m.role || "").trim());
      let hasPair = false;
      for (const r of roles) {
        if (r.endsWith(CFG.coverageSuffix)) {
          const base = r.slice(0, -CFG.coverageSuffix.length).trim();
          if (roles.some((x) => x === base)) hasPair = true;
        }
      }
      // Fallback signal Jane uses: exactly 2 split members on one opp.
      const twoMembers = members.length === 2;

      return {
        id: opp.Id,
        name: opp.Name,
        account: opp.Account && opp.Account.Name,
        closeDate: opp.CloseDate,
        amount: opp.Amount,
        stage: opp.StageName,
        members,
        splitCount: members.length,
        flagged: hasPair || twoMembers,
        flagReason: hasPair ? "primary + coverage" : twoMembers ? "2 split members" : "",
      };
    });
    return rows;
  }

  // ---- render ----------------------------------------------------------------
  let sortKey = "closeDate", sortDir = -1;

  function render() {
    const q = $("search").value.trim().toLowerCase();
    const onlyFlagged = $("onlyFlagged").checked;

    let rows = STATE.rows.slice();
    if (onlyFlagged) rows = rows.filter((r) => r.flagged);
    if (q) {
      rows = rows.filter((r) =>
        [r.name, r.account, ...r.members.map((m) => m.name)].join(" ").toLowerCase().includes(q)
      );
    }
    rows.sort((a, b) => {
      let x = a[sortKey], y = b[sortKey];
      if (x == null) x = ""; if (y == null) y = "";
      return (x < y ? -1 : x > y ? 1 : 0) * sortDir;
    });

    const tbody = $("tbody");
    tbody.innerHTML = rows
      .map((r) => {
        const reps = r.members
          .map(
            (m) =>
              `<span class="rep">${esc(m.name)}<span class="role"> — ${esc(m.role || "no role")}` +
              (m.pct != null ? ` · ${m.pct}%` : "") +
              (m.amount != null ? ` · ${fmtMoney(m.amount)}` : "") +
              `</span></span>`
          )
          .join("");
        const roleChip = r.flagged
          ? `<span class="chip warn">${esc(r.flagReason)}</span>`
          : `<span class="chip ok">ok</span>`;
        return (
          `<tr class="${r.flagged ? "flagged" : ""}">` +
          `<td>${esc(r.name)}</td>` +
          `<td>${esc(r.account)}</td>` +
          `<td>${fmtDate(r.closeDate)}</td>` +
          `<td>${fmtMoney(r.amount)}</td>` +
          `<td>${reps}</td>` +
          `<td>${roleChip}</td>` +
          `<td class="decide"><input type="text" placeholder="who to retain…" data-id="${esc(r.id)}" /></td>` +
          `</tr>`
        );
      })
      .join("");

    $("emptyRows").classList.toggle("hidden", rows.length > 0);

    // summary cards
    const flagged = STATE.rows.filter((r) => r.flagged);
    const totalAmt = STATE.rows.reduce((s, r) => s + (r.amount || 0), 0);
    $("cTotal").textContent = STATE.rows.length;
    $("cFlagged").textContent = flagged.length;
    $("cAmount").textContent = fmtMoney(totalAmt);
    $("cPeriod").textContent = STATE.period ? STATE.period.label : "—";
  }

  function toCSV() {
    const head = ["Opportunity", "Account", "Close Date", "Amount", "Stage", "Flagged", "Reason", "Split Member", "Role", "Split %", "Split Amount"];
    const lines = [head.join(",")];
    const cell = (v) => `"${String(v == null ? "" : v).replace(/"/g, '""')}"`;
    for (const r of STATE.rows) {
      if (!r.members.length) lines.push([r.name, r.account, r.closeDate, r.amount, r.stage, r.flagged, r.flagReason, "", "", "", ""].map(cell).join(","));
      for (const m of r.members) {
        lines.push([r.name, r.account, r.closeDate, r.amount, r.stage, r.flagged, r.flagReason, m.name, m.role, m.pct, m.amount].map(cell).join(","));
      }
    }
    const blob = new Blob([lines.join("\n")], { type: "text/csv" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = `opp-split-review-${STATE.period ? STATE.period.label.replace(/\s/g, "-") : "export"}.csv`;
    a.click();
  }

  // ---- main flow -------------------------------------------------------------
  async function refresh() {
    if (CFG.consumerKey.includes("PASTE_")) {
      showSetupBanner();
      return;
    }
    const tok = getToken();
    if (!tok) {
      setStatus("Redirecting to Salesforce sign-in…");
      await beginLogin();
      return;
    }
    try {
      $("refreshBtn").disabled = true;
      setStatus("Querying Salesforce…");
      const range = lastMonthRange();
      STATE.period = range;
      const records = await soql(tok.instance_url, tok.access_token, buildQuery(range));
      STATE.rows = analyze(records);
      STATE.instanceUrl = tok.instance_url;
      $("status").classList.add("hidden");
      $("dashboard").classList.remove("hidden");
      $("logoutBtn").classList.remove("hidden");
      $("who").textContent = tok.instance_url ? new URL(tok.instance_url).host : "";
      render();
    } catch (e) {
      if (String(e).includes("INVALID_SESSION") || String(e).includes("401")) {
        signOut();
        return;
      }
      setStatus("Error: " + esc(e.message || e), true);
    } finally {
      $("refreshBtn").disabled = false;
    }
  }

  function showSetupBanner() {
    const b = $("setupBanner");
    b.innerHTML =
      "<b>Almost ready.</b> This dashboard needs a one-time Salesforce Connected App. " +
      "Open <code>config.js</code> and paste your <code>consumerKey</code> and <code>loginUrl</code>. " +
      'Full steps in <a href="SETUP.md">SETUP.md</a>.';
    b.classList.remove("hidden");
    setStatus("Configuration needed — see the banner above.", true);
  }

  // ---- wire up ---------------------------------------------------------------
  document.addEventListener("DOMContentLoaded", async () => {
    $("refreshBtn").addEventListener("click", refresh);
    $("logoutBtn").addEventListener("click", signOut);
    $("csvBtn").addEventListener("click", toCSV);
    $("search").addEventListener("input", render);
    $("onlyFlagged").addEventListener("change", render);
    document.querySelectorAll("th[data-sort]").forEach((th) =>
      th.addEventListener("click", () => {
        const k = th.getAttribute("data-sort");
        if (sortKey === k) sortDir *= -1;
        else { sortKey = k; sortDir = 1; }
        render();
      })
    );

    if (CFG.consumerKey.includes("PASTE_")) { showSetupBanner(); return; }
    try {
      const returned = await completeLoginIfReturning();
      if (returned) refresh();
    } catch (e) {
      setStatus("Sign-in error: " + esc(e.message || e), true);
    }
  });
})();
