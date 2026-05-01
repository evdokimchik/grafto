# Grafto Landing Page Handoff

Last updated: 2026-05-01

## What Was Done

- Added an Android waitlist email capture under the inactive Google Play badge in the `#download` section.
- Replaced the old `Coming soon` / `Скоро` text with a bilingual embedded form.
- Wired the waitlist form to Google Forms:
  - Endpoint: `https://docs.google.com/forms/d/e/1FAIpQLScCpKmknKFL5vpHjfRrpKU6tUxeTbqDVMs6DKm-reyLnjpiew/formResponse`
  - Email field: `entry.1557041389`
- The Android waitlist posts only the visitor email using `FormData` and `fetch(..., { mode: "no-cors" })`.
- Updated the hero primary CTA:
  - English: `Stage Assessment`
  - Russian: `Оценка стадии`
  - Both point to `#norwood`.
- Pushed both changes to `main`.
- Verified `https://start.grafto.hair/` serves the updated waitlist and hero CTA.
- Configured this local machine to push via SSH using the key named `Grafto deploy Codex` in GitHub.

## What Is Left

- Do one real end-to-end waitlist submission with an email address the owner controls, then confirm it appears in the Android Waiting List Google Form responses.
- Visually check the hero and download sections on mobile Safari/Chrome after cache expiry.
- Optionally update `DEPLOY.md` to include the Android waitlist Google Form, since it currently documents the Norwood form path only.
- Decide whether the local GitHub SSH key should remain on the GitHub account long-term or be removed after deployment work is complete.

## Key Constraints

- This is a static GitHub Pages site served from `main` with custom domain `start.grafto.hair`.
- There is no build step, backend, serverless endpoint, API key, cookie, localStorage, or analytics event for the Android waitlist.
- Google Forms responses are opaque because of `no-cors`; the browser treats a dispatched request as success.
- The waitlist must collect only email. Do not add language, page URL, referrer, user agent, Norwood stage, or other metadata unless the privacy/data policy is intentionally changed.
- Keep English/Russian parity using the existing `data-lang` toggle pattern.
- GitHub Pages may cache HTML for several minutes; cache-busted checks can show updates before the bare URL refreshes everywhere.

## Done When

- The live hero button says `Stage Assessment` in English and `Оценка стадии` in Russian.
- Both hero CTA variants scroll to the `Norwood Scale at a Glance` / `Шкала Норвуда` section.
- The Google Play area shows the Android waitlist form instead of `Coming soon` / `Скоро`.
- Invalid email input shows localized validation.
- Valid waitlist submission stores exactly one email value in the Android Waiting List Google Form.
- App Store link, language toggle, theme toggle, Norwood assessment, and checklist download still work.
- `git status --short --branch` is clean and `main` matches `origin/main`.
