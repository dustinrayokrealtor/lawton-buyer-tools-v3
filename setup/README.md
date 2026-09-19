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
