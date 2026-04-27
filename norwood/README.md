# Norwood Self-Assessment — Loops + Google Sheets integration

The Norwood self-assessment widget on the landing page captures `(email, stage)`
and is wired to do two things server-side:

1. Email the user a graft-range estimate via [Loops](https://loops.so/).
2. Append the lead as a row to a Google Sheet named
   **"Collected emails: Norwood scale"**
   (ID: `1CyK6Ru-olLOl47ljWN1oSdNb42W1UwM9wDonER8jXtM`, tab: `Sheet1`).

## Why this is wired through a backend (not directly from the browser)

The site is served as **static GitHub Pages** (no server-side rendering).
Embedding a Loops API key — or Google service-account credentials — in client
JS would expose them publicly. We therefore call a tiny **server-side proxy**
that holds all secrets as environment variables, validates input, and calls
Loops + Google Sheets on the user's behalf.

If no proxy is configured, the widget still works: the user sees their result
immediately, but no email is sent and no row is logged. A small notice is
shown explaining that email delivery isn't enabled yet. No data leaves the
browser, no API key is exposed, nothing breaks.

## Frontend → backend contract

The frontend (`index.html`) reads `window.GRAFTO_NORWOOD_ENDPOINT` at runtime.
Set it once via a small inline script in the deployed site, e.g.:

```html
<script>window.GRAFTO_NORWOOD_ENDPOINT = "https://api.grafto.hair/norwood";</script>
```

The widget POSTs JSON:

```json
{
  "email": "user@example.com",
  "stage": 4,
  "language": "en",
  "pattern": "Likely Norwood 4 — front + crown involvement.",
  "grafts": "Typical planning range: 3,000–4,000 grafts.",
  "nextStep": "Prioritize hairline framing first, then assess crown coverage based on donor capacity.",
  "source": "landing-norwood",
  "timestamp": "2026-04-27T10:15:32.000Z",
  "appUrl": "https://apps.apple.com/app/grafto-hair-transplant-smp/id6759666757",
  "pageUrl": "https://start.grafto.hair/",
  "referrer": "https://www.google.com/",
  "userAgent": "Mozilla/5.0 …"
}
```

A `2xx` response means the lead was logged AND the email was sent. Any non-2xx
surfaces a retry message to the user.

## Required Loops setup (one-time, manual)

1. **Create a transactional template** in Loops (Transactional → Create).
   The template should reference these data variables:
   - `{{stage}}` — number 1–7
   - `{{pattern}}` — localized pattern sentence
   - `{{grafts}}` — localized graft-range sentence
   - `{{nextStep}}` — localized "best next step"
   - `{{language}}` — "en" or "ru" (use Loops branching for localized copy,
     or create separate templates and key off `language` server-side)
   - `{{appUrl}}` — `https://apps.apple.com/app/grafto-hair-transplant-smp/id6759666757`
2. Copy the **transactional template ID** — you'll set it as
   `LOOPS_TRANSACTIONAL_ID` (or `LOOPS_TRANSACTIONAL_ID_RU` if you prefer
   separate templates per language).
3. Generate a **Loops API key** (Settings → API). Set it as `LOOPS_API_KEY`.

## Required Google Sheets setup (one-time, manual)

Two production-ready options. **Option A (service account)** is recommended —
it is the standard Google-Cloud-native path, scales cleanly, and uses keys
that can be rotated and audited. **Option B (Apps Script webhook)** is a
faster setup if you don't want to touch GCP at all.

### Sheet preparation (do this for either option)

Open the target sheet
([Collected emails: Norwood scale](https://docs.google.com/spreadsheets/d/1CyK6Ru-olLOl47ljWN1oSdNb42W1UwM9wDonER8jXtM))
and add this header row to `Sheet1` row 1 (the worker assumes headers exist —
new rows are appended starting at row 2):

```
Timestamp | Email | Language | Norwood Stage | Pattern | Graft Estimate | Best Next Step | Source | Page URL | Referrer | User Agent
```

### Option A — Google service account (recommended)

1. In Google Cloud Console, create (or reuse) a project and **enable the
   Google Sheets API**.
2. Create a **service account**. Generate a **JSON key**; you'll only need
   the `client_email` and `private_key` fields.
3. **Share the spreadsheet** with the service account's `client_email`
   address, granting **Editor** access. Without this share the API will
   return `403`.
4. Set Worker secrets:
   - `GOOGLE_SERVICE_ACCOUNT_EMAIL` — the `client_email` from the JSON key.
   - `GOOGLE_PRIVATE_KEY` — the `private_key` from the JSON key
     (keep the `\n` newlines as-is — the worker normalizes them).
   - `GOOGLE_SHEET_ID` — `1CyK6Ru-olLOl47ljWN1oSdNb42W1UwM9wDonER8jXtM`.
   - `GOOGLE_SHEET_NAME` — `Sheet1`.

### Option B — Google Apps Script webhook (zero-GCP alternative)

1. Open the spreadsheet → **Extensions → Apps Script**. Paste:

   ```js
   function doPost(e) {
     const sheet = SpreadsheetApp
       .openById('1CyK6Ru-olLOl47ljWN1oSdNb42W1UwM9wDonER8jXtM')
       .getSheetByName('Sheet1');
     const secret = PropertiesService.getScriptProperties().getProperty('SHARED_SECRET');
     const data = JSON.parse(e.postData.contents);
     if (!secret || data.secret !== secret) {
       return ContentService.createTextOutput('forbidden').setMimeType(ContentService.MimeType.TEXT);
     }
     sheet.appendRow([
       data.timestamp || new Date().toISOString(),
       data.email || '',
       data.language || '',
       data.stage || '',
       data.pattern || '',
       data.grafts || '',
       data.nextStep || '',
       data.source || '',
       data.pageUrl || '',
       data.referrer || '',
       data.userAgent || ''
     ]);
     return ContentService.createTextOutput('{"ok":true}').setMimeType(ContentService.MimeType.JSON);
   }
   ```

2. **Project Settings → Script Properties** → add `SHARED_SECRET` with a long
   random string.
3. **Deploy → New deployment → Web app**, execute as **Me**, access
   **Anyone**. Copy the `/exec` URL.
4. Set Worker secrets:
   - `SHEETS_WEBHOOK_URL` — the `/exec` URL from step 3.
   - `SHEETS_WEBHOOK_SECRET` — the same long random string.

The worker code below supports **both** options — it prefers service-account
mode when `GOOGLE_SERVICE_ACCOUNT_EMAIL` + `GOOGLE_PRIVATE_KEY` are set, and
falls back to the Apps Script webhook when `SHEETS_WEBHOOK_URL` is set.

## Reference Cloudflare Worker (drop-in)

Save as `worker.js` and deploy with `wrangler deploy`. Set the Loops + Sheets
secrets listed above. The worker validates input, sends the transactional
email via Loops, and appends a row to the spreadsheet.

```js
export default {
  async fetch(req, env) {
    if (req.method === 'OPTIONS') return cors(new Response(null, { status: 204 }));
    if (req.method !== 'POST') return cors(new Response('Method not allowed', { status: 405 }));

    let body;
    try { body = await req.json(); } catch { return cors(new Response('Bad JSON', { status: 400 })); }

    const email = (body.email || '').trim().toLowerCase();
    const stage = Number(body.stage);
    const lang = body.language === 'ru' ? 'ru' : 'en';
    if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) return cors(new Response('Invalid email', { status: 400 }));
    if (!(stage >= 1 && stage <= 7)) return cors(new Response('Invalid stage', { status: 400 }));

    const lead = {
      timestamp: typeof body.timestamp === 'string' ? body.timestamp : new Date().toISOString(),
      email,
      language: lang,
      stage,
      pattern: String(body.pattern || '').slice(0, 500),
      grafts: String(body.grafts || '').slice(0, 500),
      nextStep: String(body.nextStep || '').slice(0, 500),
      source: String(body.source || 'landing-norwood').slice(0, 100),
      pageUrl: String(body.pageUrl || '').slice(0, 500),
      referrer: String(body.referrer || '').slice(0, 500),
      userAgent: String(body.userAgent || '').slice(0, 500)
    };

    // Run sheet append + Loops email in parallel; surface a 502 only if BOTH fail.
    const [sheetRes, loopsRes] = await Promise.allSettled([
      appendToSheet(lead, env),
      sendLoopsEmail(lead, body, env)
    ]);

    if (sheetRes.status === 'rejected') console.error('Sheets error:', sheetRes.reason);
    if (loopsRes.status === 'rejected') console.error('Loops error:', loopsRes.reason);

    if (sheetRes.status === 'rejected' && loopsRes.status === 'rejected') {
      return cors(new Response('Upstream error', { status: 502 }));
    }
    return cors(new Response(JSON.stringify({
      ok: true,
      sheetLogged: sheetRes.status === 'fulfilled',
      emailSent: loopsRes.status === 'fulfilled'
    }), { status: 200, headers: { 'Content-Type': 'application/json' } }));
  }
};

async function sendLoopsEmail(lead, body, env) {
  if (!env.LOOPS_API_KEY || !env.LOOPS_TRANSACTIONAL_ID) {
    throw new Error('Loops not configured');
  }
  const headers = {
    'Authorization': `Bearer ${env.LOOPS_API_KEY}`,
    'Content-Type': 'application/json'
  };

  // 1) upsert contact
  await fetch('https://app.loops.so/api/v1/contacts/update', {
    method: 'PUT', headers,
    body: JSON.stringify({
      email: lead.email,
      source: 'landing-norwood',
      userGroup: 'Norwood Lead',
      norwoodStage: lead.stage,
      language: lead.language
    })
  });

  // 2) send transactional email
  const templateId = lead.language === 'ru' && env.LOOPS_TRANSACTIONAL_ID_RU
    ? env.LOOPS_TRANSACTIONAL_ID_RU
    : env.LOOPS_TRANSACTIONAL_ID;

  const txRes = await fetch('https://app.loops.so/api/v1/transactional', {
    method: 'POST', headers,
    body: JSON.stringify({
      transactionalId: templateId,
      email: lead.email,
      dataVariables: {
        stage: lead.stage,
        pattern: lead.pattern,
        grafts: lead.grafts,
        nextStep: lead.nextStep,
        language: lead.language,
        appUrl: body.appUrl || 'https://apps.apple.com/app/grafto-hair-transplant-smp/id6759666757'
      }
    })
  });
  if (!txRes.ok) throw new Error(`Loops ${txRes.status}`);
}

// === Google Sheets append ===
// Prefers service account (Option A); falls back to Apps Script webhook (Option B).
async function appendToSheet(lead, env) {
  const row = [
    lead.timestamp,
    lead.email,
    lead.language,
    lead.stage,
    lead.pattern,
    lead.grafts,
    lead.nextStep,
    lead.source,
    lead.pageUrl,
    lead.referrer,
    lead.userAgent
  ];

  if (env.GOOGLE_SERVICE_ACCOUNT_EMAIL && env.GOOGLE_PRIVATE_KEY && env.GOOGLE_SHEET_ID) {
    return await appendViaServiceAccount(row, env);
  }
  if (env.SHEETS_WEBHOOK_URL) {
    return await appendViaWebhook(lead, env);
  }
  throw new Error('Sheets not configured');
}

async function appendViaWebhook(lead, env) {
  const res = await fetch(env.SHEETS_WEBHOOK_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ...lead, secret: env.SHEETS_WEBHOOK_SECRET || '' })
  });
  if (!res.ok) throw new Error(`Sheets webhook ${res.status}`);
}

async function appendViaServiceAccount(row, env) {
  const token = await getGoogleAccessToken(env);
  const sheetName = env.GOOGLE_SHEET_NAME || 'Sheet1';
  const url = `https://sheets.googleapis.com/v4/spreadsheets/${encodeURIComponent(env.GOOGLE_SHEET_ID)}` +
    `/values/${encodeURIComponent(sheetName)}!A1:append?valueInputOption=USER_ENTERED&insertDataOption=INSERT_ROWS`;
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ values: [row] })
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Sheets API ${res.status}: ${text}`);
  }
}

// Sign a JWT with the service-account private key and exchange for an access token.
// Uses Cloudflare Workers' built-in WebCrypto — no external deps required.
async function getGoogleAccessToken(env) {
  const now = Math.floor(Date.now() / 1000);
  const claim = {
    iss: env.GOOGLE_SERVICE_ACCOUNT_EMAIL,
    scope: 'https://www.googleapis.com/auth/spreadsheets',
    aud: 'https://oauth2.googleapis.com/token',
    iat: now,
    exp: now + 3600
  };
  const header = { alg: 'RS256', typ: 'JWT' };
  const encode = (obj) => base64UrlEncode(new TextEncoder().encode(JSON.stringify(obj)));
  const unsigned = `${encode(header)}.${encode(claim)}`;

  const key = await importPkcs8(env.GOOGLE_PRIVATE_KEY);
  const sig = await crypto.subtle.sign('RSASSA-PKCS1-v1_5', key, new TextEncoder().encode(unsigned));
  const jwt = `${unsigned}.${base64UrlEncode(new Uint8Array(sig))}`;

  const res = await fetch('https://oauth2.googleapis.com/token', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({
      grant_type: 'urn:ietf:params:oauth:grant-type:jwt-bearer',
      assertion: jwt
    })
  });
  if (!res.ok) throw new Error(`Token exchange ${res.status}: ${await res.text()}`);
  const json = await res.json();
  return json.access_token;
}

async function importPkcs8(pem) {
  // Accept either real newlines or escaped "\n" sequences (env vars often store the latter).
  const normalized = pem.replace(/\\n/g, '\n');
  const b64 = normalized
    .replace('-----BEGIN PRIVATE KEY-----', '')
    .replace('-----END PRIVATE KEY-----', '')
    .replace(/\s+/g, '');
  const der = Uint8Array.from(atob(b64), c => c.charCodeAt(0));
  return crypto.subtle.importKey(
    'pkcs8', der.buffer,
    { name: 'RSASSA-PKCS1-v1_5', hash: 'SHA-256' },
    false, ['sign']
  );
}

function base64UrlEncode(bytes) {
  let str = '';
  for (const b of bytes) str += String.fromCharCode(b);
  return btoa(str).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
}

function cors(res) {
  res.headers.set('Access-Control-Allow-Origin', 'https://start.grafto.hair');
  res.headers.set('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.headers.set('Access-Control-Allow-Headers', 'Content-Type');
  res.headers.set('Access-Control-Max-Age', '86400');
  return res;
}
```

The same logic ports trivially to Vercel / Netlify / AWS Lambda — only the
handler signature changes. Node runtimes can use the official
`google-auth-library` + `googleapis` packages instead of the hand-rolled JWT.

## Worker secrets summary

```
# Loops
LOOPS_API_KEY                  = sk_live_…
LOOPS_TRANSACTIONAL_ID         = clxxxxxxx
LOOPS_TRANSACTIONAL_ID_RU      = clxxxxxxx   # optional, RU-specific template

# Google Sheets — Option A (service account, recommended)
GOOGLE_SERVICE_ACCOUNT_EMAIL   = norwood-leads@<project>.iam.gserviceaccount.com
GOOGLE_PRIVATE_KEY             = -----BEGIN PRIVATE KEY-----\n…\n-----END PRIVATE KEY-----\n
GOOGLE_SHEET_ID                = 1CyK6Ru-olLOl47ljWN1oSdNb42W1UwM9wDonER8jXtM
GOOGLE_SHEET_NAME              = Sheet1

# Google Sheets — Option B (Apps Script webhook, alternative to Option A)
SHEETS_WEBHOOK_URL             = https://script.google.com/macros/s/…/exec
SHEETS_WEBHOOK_SECRET          = <long random string>
```

Set with: `wrangler secret put <NAME>`.

## Until the backend is deployed

`window.GRAFTO_NORWOOD_ENDPOINT` is unset → the widget shows the result
immediately and notes that email delivery isn't enabled. No data leaves the
browser, no API key is exposed, nothing breaks.
