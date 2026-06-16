/**
 * Google Apps Script — Keep Render free tier awake
 *
 * Setup:
 * 1. Go to https://script.google.com → New project
 * 2. Paste this code
 * 3. Set RENDER_API_URL to your backend health endpoint
 * 4. Triggers → Add Trigger → timeDriven → minute timer → Every minute
 *    (runs every minute; script internally pings every 30 sec via 2 URLs or use 1-min interval)
 *
 * Note: Google Apps Script minimum trigger interval is 1 minute (not 30 sec).
 * For true 30-sec pings, use cron-job.org or UptimeRobot with 30s interval (paid) or two 1-min triggers.
 */

const RENDER_URL = 'https://YOUR-APP.onrender.com/health/';

function pingRender() {
  try {
    const response = UrlFetchApp.fetch(RENDER_URL, {
      method: 'get',
      muteHttpExceptions: true,
      followRedirects: true,
    });
    Logger.log(RENDER_URL + ' → ' + response.getResponseCode());
  } catch (e) {
    Logger.log('Error: ' + e);
  }
}

function createTrigger() {
  ScriptApp.getProjectTriggers().forEach(function (t) {
    ScriptApp.deleteTrigger(t);
  });
  ScriptApp.newTrigger('pingRender')
    .timeBased()
    .everyMinutes(1)
    .create();
}
