// ============================================================================
//  MSS Opp Split Review — configuration
//  Edit the values below ONCE. See SETUP.md for where to get each value.
// ============================================================================
window.OPP_SPLIT_CONFIG = {

  // --- Salesforce connection -------------------------------------------------
  // Your Salesforce login domain. Examples:
  //   "https://yourcompany.my.salesforce.com"   (production / My Domain)
  //   "https://yourcompany--sandbox.sandbox.my.salesforce.com"  (sandbox)
  loginUrl: "https://login.salesforce.com",

  // The "Consumer Key" of the Connected App you create (see SETUP.md, step 1).
  // This is NOT a secret — it is safe to commit and serve publicly.
  consumerKey: "PASTE_YOUR_CONNECTED_APP_CONSUMER_KEY_HERE",

  // The page's own URL, registered as the Connected App callback.
  // Leave as-is to auto-detect; it will use wherever this page is served from.
  redirectUri: window.location.origin + window.location.pathname,

  // --- Report definition -----------------------------------------------------
  // Stage value(s) to include. Per the Salesforce report: "08 - Closed".
  // Matches the StageName picklist string exactly.
  closedWonStages: ["08 - Closed"],

  // Team Member Full Names to EXCLUDE (report filter:
  // "Team Member: Full Name not equals to Sam Hansen, Digital Renewals").
  excludeNames: ["Sam Hansen", "Digital Renewals"],

  // Which split roles form a "primary + coverage" pair. The analysis flags any
  // opp whose split contains BOTH a base role and its "<role> - Coverage".
  // Matching is done by the " - Coverage" suffix, so this list is informational
  // and used to label/group; you usually don't need to edit it.
  coverageSuffix: " - Coverage",

  // Report type: "Opportunity Splits with Team Member".
  // We query OpportunitySplit — each split is owned by an opportunity team
  // member, and the "Full Name" exclusion above applies to that split owner.
  //   "OpportunitySplit"      -> splits with % + amount (this report)
  //   "OpportunityTeamMember" -> team roles only (no amount)
  splitObject: "OpportunitySplit",

  // Salesforce REST/Query API version.
  apiVersion: "v60.0",
};
