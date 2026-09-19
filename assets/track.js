/**
 * Lawton Buyer Tools — page view beacon
 * ------------------------------------------------------------------
 * Fires one "view" to the same Apps Script web app that already takes the
 * lead captures. The script routes on kind === "view", appends a row to the
 * Hits sheet, and mails a nightly digest the Buyer Ops Hub reads out of Gmail.
 *
 * Shared file rather than an inline block on every page on purpose: Apps
 * Script sometimes hands out a fresh /exec URL on redeploy, and when that
 * happens this is the ONE line to change instead of nine.
 *
 * Nothing recorded here identifies a person: no IP, no name, no email, no
 * full referring URL, no third-party script, no cookie.
 * ------------------------------------------------------------------
 */
(function () {
  "use strict";

  var ENDPOINT = "https://script.google.com/macros/s/AKfycbwSkkgNvZqNTFDnO9jp5sIiXGEer16rfLo08lX2XEH41uk5IcsiAI7GPcQ3n-Jxdi2d/exec";

  // ---- your own visits ----
  // Load any page once with ?mute=1 and this browser never reports again.
  try {
    if (location.search.indexOf("mute=1") > -1) localStorage.setItem("lbt.mute", "1");
    if (localStorage.getItem("lbt.mute")) return;
  } catch (e) {}

  // ---- bots ----
  // Checked here rather than in the Apps Script: doPost cannot see request
  // headers at all, so a server-side user-agent filter can never fire. Most
  // crawlers never run this file in the first place; this catches the rest
  // without putting a fingerprintable UA string in the sheet.
  try {
    if (navigator.webdriver) return;
    if (/bot|crawl|spider|slurp|headless|preview|lighthouse|pingdom|gtmetrix/i.test(navigator.userAgent)) return;
  } catch (e) {}

  // ---- session and returning ----
  // sid lives in sessionStorage, so five reloads are five views and one visit.
  var sid = "", seen = "no";
  try {
    sid = sessionStorage.getItem("lbt.sid") || "";
    if (!sid) {
      sid = Math.random().toString(36).slice(2, 8);
      sessionStorage.setItem("lbt.sid", sid);
    }
    seen = localStorage.getItem("lbt.seen") ? "yes" : "no";
    localStorage.setItem("lbt.seen", "1");
  } catch (e) {
    sid = "nostore";
    seen = "no";
  }

  // ---- referrer, host only, never the query string ----
  var ref = "";
  try {
    if (document.referrer) {
      var host = new URL(document.referrer).hostname.replace(/^www\./, "");
      if (host && host !== location.hostname) ref = host;
    }
  } catch (e) {}

  var body = JSON.stringify({
    kind: "view",
    page: location.pathname,
    title: document.title,
    ref: ref,
    sid: sid,
    device: (screen.width < 760 ? "mobile" : "desktop"),
    seen: seen
  });

  // text/plain dodges the CORS preflight an Apps Script web app will not
  // answer. sendBeacon is fire and forget, so a slow script never holds up
  // the page; fetch with keepalive is the fallback when the queue is full.
  function send() {
    try {
      var blob = new Blob([body], { type: "text/plain;charset=UTF-8" });
      if (!navigator.sendBeacon(ENDPOINT, blob)) throw new Error("queue full");
    } catch (e) {
      try {
        fetch(ENDPOINT, {
          method: "POST",
          mode: "no-cors",
          headers: { "Content-Type": "text/plain" },
          body: body,
          keepalive: true
        });
      } catch (e2) {}
    }
  }

  // Wait for a real paint before reporting, so a bounce that never rendered
  // does not count as a view.
  if (document.readyState === "complete") send();
  else window.addEventListener("load", send, { once: true });
})();
