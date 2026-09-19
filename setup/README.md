# Lead mailer setup (one time, about five minutes)

Every "Print or save as PDF" button on the site asks for a name, email and phone
the first time, then posts those details plus a PDF of the page to a Google Apps
Script that runs from your own Gmail. The script emails you, emails the buyer
their copy, and logs the lead in a Google Sheet. No third-party service, no
API keys, nothing to pay for.

## 1. Make the sheet

1. Go to [sheets.new](https://sheets.new) while signed in to the Google account
   you want the emails to come from.
2. Name it **Lawton Buyer Tools Leads**. Leave it empty. The script writes the
   header row on the first lead.

## 2. Add the script

1. In that sheet: **Extensions > Apps Script**.
2. Delete whatever is in the editor and paste the whole contents of
   [`lead-mailer.gs`](lead-mailer.gs).
3. At the top of the file, check `TO` is the address you want leads sent to.
   Set `CC_BUYER = false` if you'd rather the buyer not get an automatic copy.
4. Save (the disk icon, or Ctrl+S).

## 3. Grant permission and test

1. In the toolbar, pick the function **sendTest** from the dropdown and press
   **Run**.
2. Google will ask you to authorize the script. Choose your account, click
   **Advanced > Go to (project name)**, then **Allow**. It's your own script, the
   "unverified" warning is normal.
3. Check your inbox. You should have a "New lead: Test Buyer" email and, since
   `TO` is also the test buyer's email, a "Your numbers from…" email. The sheet
   should now have a header row and one test row (delete that row whenever).

## 4. Deploy it

1. **Deploy > New deployment**.
2. Click the gear next to "Select type" and choose **Web app**.
3. Settings:
   - Description: anything
   - Execute as: **Me**
   - Who has access: **Anyone**  (this is what lets the public site post to it;
     nobody can read the sheet or your mail through it)
4. **Deploy**, then copy the **Web app URL**. It looks like
   `https://script.google.com/macros/s/AKfycb.../exec`.

## 5. Plug the URL into the site

Open `assets/leadgate.js` and paste the URL between the quotes on the
`var ENDPOINT = "..."` line. Commit and push. Pages redeploys in a minute or two.

**Status: done on Sep 18, 2026.** The sheet is "Lawton Buyer Tools Leads" in
dustin.ray.ok@gmail.com's Drive, the script project is "Lawton Buyer Tools lead
mailer" bound to it, and the live URL is already in `assets/leadgate.js`.

## Changing the script later

Edit the code, save, then **Deploy > Manage deployments > (pencil) > Version:
New version > Deploy**. The URL stays the same, so the site doesn't need touching.

## What the visitor sees

- First print: a small form (name, email, phone). Remembered in that browser,
  so the second print skips straight to the print dialog.
- A short "Building your PDF…" message, then the browser's normal print / save
  as PDF dialog.
- If the PDF library or the network ever fails, they still get their printout.
  You just won't get that lead's email.

## Limits worth knowing

- Consumer Gmail sends about 100 messages a day through Apps Script; each lead
  uses two (you and the buyer). Google Workspace accounts get 1,500.
- PDFs run roughly 0.6 to 1.2 MB, well under Gmail's attachment cap.

## Traffic counting (added Sep 19, 2026)

Every page loads `assets/track.js`, which beacons one page view to the **same**
web app URL the capture form already posts to. `doPost` routes on `kind`, so
the lead path is untouched. Views land in a Hits sheet and one digest email a
night carries the counts to the Buyer Ops Hub through Gmail.

The endpoint lives in **one place** — `ENDPOINT` at the top of
`assets/track.js`. Apps Script sometimes issues a fresh `/exec` URL on
redeploy, and when it does that is the only line to change.

### Turn it on

1. Open the same Apps Script project and paste in the current
   [`lead-mailer.gs`](lead-mailer.gs) — it now carries `logView`, `setupHits`,
   `dailyTraffic` and the routing `doPost` alongside the lead code.
2. Run **setupHits** once. Approve the prompt, read `HITS_SHEET_ID` out of the
   execution log, and paste it into the variable at the top.
3. **Deploy > Manage deployments > (pencil) > Version: New version > Deploy.**
   Using *Manage deployments* rather than *New deployment* keeps the existing
   `/exec` URL, so neither the lead form nor the beacon breaks.
4. Add a time-driven trigger for `dailyTraffic`, day timer, 1am to 2am.
5. Run `dailyTraffic` by hand once. The digest should arrive within a minute.

### Mute your own visits

Load any page once with `?mute=1` on the end and that browser never reports
again. Do it on your phone and your laptop before you go looking at the site.
Clearing site data undoes it, so redo it if you ever wipe your browser.

### What is recorded

Time, page path, page title, referring host, a random per-tab session id,
mobile or desktop, and whether that browser has been here before. No IP, no
name, no email, no full referring URL, no third-party script, no cookie.

### One change from the spec

The spec filtered bots on the user agent inside `logView`, reading
`e.parameter.ua`. An Apps Script web app cannot see request headers at all and
the beacon never sends a `ua` parameter, so that check could never fire. The
filter now runs in `track.js` before the beacon is sent, which actually works
and keeps a fingerprintable UA string out of the sheet.

### Two things break this

- **Who has access set to anything but Anyone.** Visitors are not signed into
  your Google account, so the beacon gets a login page and every view vanishes
  with no error anywhere.
- **A new deployment URL that never made it into `track.js`.** If the sheet
  stops filling after you edit the script, check that first.
