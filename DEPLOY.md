# Norwood lead capture — minimal deploy (Apps Script only)

This is the **fastest path** to make the Norwood form actually capture emails on
the live site. It needs no Cloudflare account, no Google Cloud, and no Loops
account. Total time: ~5 minutes.

It uses a single **Google Apps Script Web App** that:

1. Appends a row to the spreadsheet **"Collected emails: Norwood scale"**
   (`1CyK6Ru-olLOl47ljWN1oSdNb42W1UwM9wDonER8jXtM`, tab `Sheet1`).
2. Sends the user a confirmation email with their estimate (via Gmail/MailApp).

For the production-grade architecture (Cloudflare Worker + Loops transactional
templates + Google service account), see `norwood/README.md`.

## Step 1 — Prepare the sheet

Open
[Collected emails: Norwood scale](https://docs.google.com/spreadsheets/d/1CyK6Ru-olLOl47ljWN1oSdNb42W1UwM9wDonER8jXtM)
and ensure row 1 of `Sheet1` has these headers (create them if missing):

```
Timestamp | Email | Language | Norwood Stage | Pattern | Graft Estimate | Best Next Step | Source | Page URL | Referrer | User Agent
```

## Step 2 — Create the Apps Script

1. In the same spreadsheet, open **Extensions → Apps Script**.
2. Replace `Code.gs` with the contents of [`apps_script/norwood.gs`](./apps_script/norwood.gs)
   (also reproduced below).
3. **Deploy → New deployment**.
   - Type: **Web app**
   - Description: `Norwood lead capture`
   - Execute as: **Me**
   - Who has access: **Anyone**
4. Authorize when prompted (Gmail + Sheets scopes).
5. Copy the **Web app URL** (looks like `https://script.google.com/macros/s/AKfycbx…/exec`).

## Step 3 — Wire the URL into the site

Edit `index.html` and set the URL on the inline config tag in `<head>`:

```html
<script>window.GRAFTO_NORWOOD_ENDPOINT = "https://script.google.com/macros/s/AKfycbx…/exec";</script>
```

Commit and push. GitHub Pages redeploys automatically.

That's it — submitting the form on https://start.grafto.hair/ will now append a
row and email the user.

## Apps Script source

See [`apps_script/norwood.gs`](./apps_script/norwood.gs).
