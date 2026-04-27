# Norwood Self-Assessment — lead capture

The Norwood self-assessment widget on the landing page lets the visitor pick a
stage, enter an email, and see a graft-range estimate computed entirely in the
browser.

## Production path (live site): Google Forms, email-only

The live site at <https://start.grafto.hair/> submits the visitor's **email
address — and nothing else** — to a Google Form named **"Grafto Norwood Scale
Leads"** (`formId: 1TD-3lpXWlZuT8l-Pjv7nyeKMn1g1xHj6_vXnM2ueNLU`).

- Public form: <https://docs.google.com/forms/d/e/1FAIpQLScAethmSc6kM82Kv6hYmEPzGqUmnOkGsPK7rHydh3abKGTdeA/viewform>
- POST endpoint used by the widget:
  `https://docs.google.com/forms/d/e/1FAIpQLScAethmSc6kM82Kv6hYmEPzGqUmnOkGsPK7rHydh3abKGTdeA/formResponse`
- Email field entry ID: `entry.2119806365`

These identifiers are public Google Forms values; they are safe to embed in
client code. There are **no API keys or secrets** in the static site.

### Why email-only?

Safety / privacy. The Norwood stage and graft estimate are computed and shown
to the visitor entirely in the browser — they never leave the device. No page
URL, referrer, or user-agent is collected. No owner notification email is
sent. The only data sent off-device is the email address the visitor typed in.

### Submission flow

1. Visitor selects a Norwood stage.
2. Visitor enters their email and submits.
3. The widget builds a `FormData` containing only
   `entry.2119806365 = <email>` and POSTs it to the Google Form's
   `formResponse` URL with `fetch(..., { method: 'POST', mode: 'no-cors' })`.
4. The opaque response (Google Forms blocks CORS reads) is treated as success.
5. The widget shows the visitor their Norwood result locally; no email is sent
   to them or to the site owner.

### Where to view collected emails

In Google Forms, open the **"Grafto Norwood Scale Leads"** form
(`1TD-3lpXWlZuT8l-Pjv7nyeKMn1g1xHj6_vXnM2ueNLU`) → **Responses** tab.

### Updating the form

If you change the email field on the form, copy the new `entry.<id>` from the
form's prefilled-link tool (Form → ⋮ → Get pre-filled link) and update
`window.GRAFTO_NORWOOD_EMAIL_ENTRY` in `index.html`.

---

## Legacy / optional reference designs

The two designs below were prior plans for richer lead capture (transactional
email, Google Sheet logging with extra fields). They are **not in use on the
live site** and are kept here purely as reference. Following them would
re-introduce extra PII collection and require server-side secrets, which the
current production path deliberately avoids.

### Legacy option 1: Google Apps Script Web App (deprecated on the live site)

A previous version of the site posted JSON `{ email, stage, language, pattern,
grafts, nextStep, source, timestamp, appUrl, pageUrl, referrer, userAgent }`
to a Google Apps Script Web App which appended a row to the spreadsheet
**"Collected emails: Norwood scale"**
(`1CyK6Ru-olLOl47ljWN1oSdNb42W1UwM9wDonER8jXtM`, tab `Sheet1`) and sent the
user a confirmation email via Gmail/MailApp.

The Apps Script source is retained at [`../apps_script/norwood.gs`](../apps_script/norwood.gs)
for reference. It is **not** wired into the live site.

### Legacy option 2: Cloudflare Worker + Loops + Google Sheets (deprecated)

An earlier plan proxied the form through a Cloudflare Worker that:
1. Sent a transactional email via [Loops](https://loops.so/) using a template
   ID stored in env (`LOOPS_TRANSACTIONAL_ID`).
2. Appended a lead row to the same Google Sheet via either a service account
   (`GOOGLE_SERVICE_ACCOUNT_EMAIL`, `GOOGLE_PRIVATE_KEY`, `GOOGLE_SHEET_ID`) or
   an Apps Script webhook (`SHEETS_WEBHOOK_URL`, `SHEETS_WEBHOOK_SECRET`).

This design required server-side secrets and is **not deployed**. The live
site does not require, read, or expose any of these env vars; none of them
exist in the codebase. If you ever want to revive this path, treat it as a
new project — review against the current privacy posture first.
