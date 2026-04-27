# Norwood Self-Assessment — Loops integration

The Norwood self-assessment widget on the landing page captures `(email, stage)`
and is designed to email the user a graft-range estimate via [Loops](https://loops.so/).

## Why this is wired through a backend (not directly from the browser)

The site is served as **static GitHub Pages** (no server-side rendering).
A Loops API key embedded in client JS would be public — anyone could read it
and abuse the account. We therefore call a tiny **server-side proxy** that
holds the Loops API key as an environment variable, validates input, and calls
Loops on the user's behalf.

If no proxy is configured, the widget still works: the user sees their result
immediately, but no email is sent and a small notice is shown explaining that
email delivery isn't enabled yet.

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
  "source": "landing-norwood"
}
```

A `2xx` response means "email was sent". Any non-2xx surfaces a retry message
to the user.

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

## Reference Cloudflare Worker (drop-in)

Save as `worker.js` and deploy with `wrangler deploy`. Set
`LOOPS_API_KEY`, `LOOPS_TRANSACTIONAL_ID`, and (optionally)
`LOOPS_TRANSACTIONAL_ID_RU` as Worker secrets.

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

    const headers = {
      'Authorization': `Bearer ${env.LOOPS_API_KEY}`,
      'Content-Type': 'application/json'
    };

    // 1) upsert contact (so it lands in the right list / has the right custom fields)
    await fetch('https://app.loops.so/api/v1/contacts/update', {
      method: 'PUT', headers,
      body: JSON.stringify({
        email,
        source: 'landing-norwood',
        userGroup: 'Norwood Lead',
        norwoodStage: stage,
        language: lang
      })
    });

    // 2) send the transactional email
    const templateId = lang === 'ru' && env.LOOPS_TRANSACTIONAL_ID_RU
      ? env.LOOPS_TRANSACTIONAL_ID_RU
      : env.LOOPS_TRANSACTIONAL_ID;

    const txRes = await fetch('https://app.loops.so/api/v1/transactional', {
      method: 'POST', headers,
      body: JSON.stringify({
        transactionalId: templateId,
        email,
        dataVariables: {
          stage,
          pattern: body.pattern || '',
          grafts: body.grafts || '',
          nextStep: body.nextStep || '',
          language: lang,
          appUrl: 'https://apps.apple.com/app/grafto-hair-transplant-smp/id6759666757'
        }
      })
    });

    if (!txRes.ok) return cors(new Response('Loops error', { status: 502 }));
    return cors(new Response('{"ok":true}', { status: 200, headers: { 'Content-Type': 'application/json' } }));
  }
};

function cors(res) {
  res.headers.set('Access-Control-Allow-Origin', 'https://start.grafto.hair');
  res.headers.set('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.headers.set('Access-Control-Allow-Headers', 'Content-Type');
  res.headers.set('Access-Control-Max-Age', '86400');
  return res;
}
```

The same logic ports trivially to Vercel / Netlify / AWS Lambda — only the
handler signature changes.

## Until the backend is deployed

`window.GRAFTO_NORWOOD_ENDPOINT` is unset → the widget shows the result
immediately and notes that email delivery isn't enabled. No data leaves the
browser, no API key is exposed, nothing breaks.
