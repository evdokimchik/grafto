# Norwood lead capture — production path (Google Forms, email-only)

The production Norwood lead-capture path is intentionally minimal:

- The visitor's **email** (and only their email) is POSTed from the browser to a
  pre-existing **Google Form** named **"Grafto Norwood Scale Leads"**
  (`formId: 1TD-3lpXWlZuT8l-Pjv7nyeKMn1g1xHj6_vXnM2ueNLU`).
- Submissions are stored in the Google Form's response sheet, viewable by the
  form's owner in Google Forms / Drive.
- **No** Norwood stage, computed result, language, page URL, referrer, user
  agent, or any other PII is collected or transmitted.
- **No API keys or secrets** are present anywhere in the client. The form URL
  and the email field's `entry.<id>` are public Google Forms identifiers, safe
  to embed in static HTML/JS.

## Configuration in `index.html`

```html
<script>
  window.GRAFTO_NORWOOD_FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLScAethmSc6kM82Kv6hYmEPzGqUmnOkGsPK7rHydh3abKGTdeA/formResponse";
  window.GRAFTO_NORWOOD_EMAIL_ENTRY = "entry.2119806365";
</script>
```

## How submission works

The widget builds a `FormData` containing only `entry.2119806365 = <email>` and
POSTs it to the Google Forms `formResponse` URL with `mode: 'no-cors'`. Google
Forms returns an opaque response by design, so the client treats network
completion as success and shows the user their Norwood result locally.

No owner notification email is sent. No transactional email is sent to the user.

## Updating the Google Form

The form lives at:

- Public form: <https://docs.google.com/forms/d/e/1FAIpQLScAethmSc6kM82Kv6hYmEPzGqUmnOkGsPK7rHydh3abKGTdeA/viewform>
- Edit URL: open via Google Forms → form `1TD-3lpXWlZuT8l-Pjv7nyeKMn1g1xHj6_vXnM2ueNLU`.

If you ever change the email field, copy the new `entry.<id>` from the form's
prefilled-link tool and update `window.GRAFTO_NORWOOD_EMAIL_ENTRY` in
`index.html`.

## Legacy / optional paths

The previous lead-capture design used a Google Apps Script Web App that
appended rows to the spreadsheet "Collected emails: Norwood scale" and emailed
the user a confirmation. That code (`apps_script/norwood.gs`) is retained as a
**legacy / optional** reference only — it is **not** wired into the live site
and is not required. The richer Cloudflare Worker + Loops design described in
[`norwood/README.md`](./norwood/README.md) is also legacy/optional.

The live site uses **only** the Google Form path described above.
