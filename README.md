# ENAKS Auto and Transportations LLC — website

Eight-page static site + one Netlify Function. No framework, no build step for hosting: Netlify publishes `public/`.

| | |
|---|---|
| Pages | Home, Services (all 11), Government and teaming, Capabilities, Funding and impact, About, Contact, Privacy |
| Form | `public/contact.html` → `POST /api/request` → `netlify/functions/request.mjs` → email via Resend |
| Design | US highway guide-sign language: green sign hero with an exit-tab call to action, Overpass type (derived from Highway Gothic), amber only for status notes |
| Public contact | (404) 354-7930 · Eautotransport@mail.com |

## Edit and build
Edit `build.py` (pages and copy), `src/site.css`, `src/site.js`, then:
```bash
python3 build.py                 # production -> public/
python3 build.py --preview       # form validates but never sends (for review links)
npm test                         # function + static checks (17 tests)
```
Commit `public/` together with the source change.

## Deploy (Netlify; commercial use is allowed on the free plan, Vercel Hobby is not)
1. Netlify → Add new project → Import from GitHub → this repo. `netlify.toml` already sets `public` and the functions folder.
2. Site configuration → Environment variables: `RESEND_API_KEY`, `ENAKS_FROM_EMAIL` (a sender on a domain you verified in Resend), `ENAKS_CONTACT_EMAIL` (e.g. Eautotransport@mail.com).
3. Redeploy, send one test enquiry with your own details, confirm it lands in the inbox.
4. Add the custom domain in Netlify, then the DNS records Netlify gives you at your registrar. Do not touch MX records.
5. Rebuild with `--site-url https://your-domain` for canonical tags and sitemap.xml.

Without the three variables the function answers 503 and the page shows an honest error with the phone number.

## Rules
- Publish only owner-confirmed facts. See `LAUNCH-CHECKLIST.md`.
- No patient data: the form and function both reject common health identifiers.
- An enquiry is never a booking.
