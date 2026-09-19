/**
 * Lawton Buyer Tools — lead mailer
 * ------------------------------------------------------------------
 * Lives inside the "Lawton Buyer Tools Leads" Google Sheet
 * (Extensions > Apps Script). Deployed as a web app it receives one
 * POST per print from assets/leadgate.js on the site and then:
 *
 *   1. appends the lead to the first sheet tab (your email list),
 *   2. emails Dustin the contact details, the scenario, and the PDF,
 *   3. emails the buyer their own copy of the PDF (optional).
 *
 * Nothing here needs an API key. It sends from the Google account that
 * deploys it, so it counts against that account's daily Gmail quota
 * (about 100 messages a day on a regular Gmail account, two per lead).
 * ------------------------------------------------------------------
 */

var TO        = "dustin@homes-lawton.com";      // where every lead lands
var FROM_NAME = "Dustin Ray, Pam & Barry's Team";
var CC_BUYER  = true;                            // email the buyer their copy too

function doPost(e) {
  try {
    var d = JSON.parse((e && e.postData && e.postData.contents) || "{}");
    var name  = clean(d.name), email = clean(d.email), phone = clean(d.phone);
    var page  = clean(d.page) || "Lawton Buyer Tools";
    var url   = clean(d.url);
    var summary = String(d.summary || "").slice(0, 6000);
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return out({ ok: false, error: "bad email" });

    // 1. the list
    var sh = SpreadsheetApp.getActiveSpreadsheet().getSheets()[0];
    if (sh.getLastRow() === 0) {
      sh.appendRow(["Time", "Name", "Email", "Phone", "Page", "URL", "Scenario"]);
      sh.getRange(1, 1, 1, 7).setFontWeight("bold");
      sh.setFrozenRows(1);
    }
    var now = new Date();
    sh.appendRow([now, name, email, phone, page, url, summary]);

    // 2. the PDF
    var atts = [];
    if (d.pdf) {
      try {
        atts.push(Utilities.newBlob(Utilities.base64Decode(d.pdf), "application/pdf",
          clean(d.filename) || "lawton-buyer-tools.pdf"));
      } catch (err) { /* bad base64: send without it */ }
    }

    // 3. to Dustin
    var when = Utilities.formatDate(now, Session.getScriptTimeZone(), "EEE, MMM d 'at' h:mm a");
    MailApp.sendEmail({
      to: TO,
      replyTo: email,
      subject: "New lead: " + name + " (" + page.split("|")[0].trim() + ")",
      htmlBody:
        "<p style='font:15px/1.5 Arial,sans-serif'>" +
        "<b>" + esc(name) + "</b><br>" +
        "<a href='mailto:" + esc(email) + "'>" + esc(email) + "</a><br>" +
        "<a href='tel:" + esc(phone.replace(/\D/g, "")) + "'>" + esc(phone) + "</a></p>" +
        "<p style='font:14px/1.5 Arial,sans-serif;color:#424242'>Printed <b>" + esc(page) + "</b> on " + when +
        (url ? " &middot; <a href='" + esc(url) + "'>open the page</a>" : "") + "</p>" +
        (summary ? "<pre style='font:13px/1.5 Menlo,Consolas,monospace;background:#EDF2F8;padding:12px;border-left:4px solid #004A9A;white-space:pre-wrap'>" + esc(summary) + "</pre>" : "") +
        (atts.length ? "<p style='font:13px Arial,sans-serif;color:#595959'>Their PDF is attached.</p>" : ""),
      attachments: atts
    });

    // 4. to the buyer
    if (CC_BUYER) {
      var first = name.split(/\s+/)[0] || "there";
      MailApp.sendEmail({
        to: email,
        replyTo: TO,
        name: FROM_NAME,
        subject: "Your numbers from " + page.split("|")[0].trim(),
        htmlBody:
          "<div style='font:15px/1.6 Arial,sans-serif;color:#222;max-width:60ch'>" +
          "<p>Hey " + esc(first) + ",</p>" +
          "<p>Here's the copy of what you ran on my site. I've attached it as a PDF so you have it.</p>" +
          "<p>I'll take a look at your numbers and follow up with what's actually listed in that range right now. If you want to talk it through sooner, call or text me at 580-351-4683.</p>" +
          "<p>I appreciate you,</p>" +
          "<p><b>Dustin Ray</b><br>Buyer Specialist, Pam &amp; Barry's Team, RE/MAX Professionals<br>" +
          "580-351-4683 &middot; <a href='mailto:dustin@homes-lawton.com'>dustin@homes-lawton.com</a><br>" +
          "<a href='https://movingtoftsill.com/'>movingtoftsill.com</a></p>" +
          "<p style='font-size:12px;color:#595959'>Each Office Independently Owned and Operated. These figures are estimates for planning and are not a loan estimate, a pre-approval, or a commitment to lend.</p>" +
          "</div>",
        attachments: atts
      });
    }

    return out({ ok: true });
  } catch (err) {
    return out({ ok: false, error: String(err) });
  }
}

// Visiting the web app URL in a browser just confirms it's alive.
function doGet() {
  return out({ ok: true, service: "Lawton Buyer Tools lead mailer" });
}

// Run this once from the editor to grant permissions and send yourself a test.
function sendTest() {
  var fake = { postData: { contents: JSON.stringify({
    name: "Test Buyer", email: TO, phone: "580-555-0100",
    page: "Buyer Payment Toolkit | test", url: "https://movingtoftsill.com/payment-toolkit.html",
    summary: "Purchase price: 199500\nRate: 6.76\nTotal monthly payment: $1,828", pdf: ""
  }) } };
  Logger.log(doPost(fake).getContent());
}

function out(o) {
  return ContentService.createTextOutput(JSON.stringify(o)).setMimeType(ContentService.MimeType.JSON);
}
function clean(v) { return String(v == null ? "" : v).replace(/[\r\n<>]/g, " ").trim().slice(0, 300); }
function esc(s) { return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#39;"); }
