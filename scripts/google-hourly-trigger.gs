/**
 * US Tax Bots - Hourly Trigger (Google Apps Script)
 * No cron-job.org needed. Uses your existing Google account.
 *
 * SETUP (browser only, ~3 min):
 * 1. Open https://script.google.com → New project
 * 2. Paste this entire file
 * 3. Replace YOUR_GITHUB_TOKEN below with Tax repo PAT
 * 4. Click clock icon (Triggers) → Add Trigger:
 *    - Function: triggerUSTaxBots
 *    - Event: Time-driven → Hour timer → Every hour
 * 5. Authorize when prompted (one time)
 *
 * Runs 8 AM - 11 PM IST only. Triggers all 3 bots via Tax orchestrator.
 */
function triggerUSTaxBots() {
  var hour = parseInt(Utilities.formatDate(new Date(), "Asia/Kolkata", "H"), 10);
  if (hour < 8 || hour > 23) {
    Logger.log("Outside 8AM-11PM IST, skip hour=" + hour);
    return;
  }

  var url = "https://api.github.com/repos/pav715/ustax-jobs-bot/actions/workflows/hourly-orchestrator.yml/dispatches";
  var token = "YOUR_GITHUB_TOKEN";

  var options = {
    method: "post",
    contentType: "application/json",
    headers: {
      Authorization: "Bearer " + token,
      Accept: "application/vnd.github+json"
    },
    payload: JSON.stringify({ ref: "main" }),
    muteHttpExceptions: true
  };

  var response = UrlFetchApp.fetch(url, options);
  var code = response.getResponseCode();
  Logger.log("Orchestrator dispatch HTTP " + code);
  if (code !== 204) {
    throw new Error("Dispatch failed: " + response.getContentText());
  }
}

/** Run once manually to test (Run button in editor) */
function testNow() {
  triggerUSTaxBots();
}
