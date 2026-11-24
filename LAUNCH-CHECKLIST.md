# Launch checklist (private)

## Done
- [x] Phone and email published: (404) 354-7930, Eautotransport@mail.com
- [x] All 11 services, grouped; NEMT marked non-emergency with a 911 note
- [x] Form ↔ function field match tested; patient-data block on both sides; honeypot + timing check
- [x] Unique titles/descriptions, one H1 per page, Organization JSON-LD (name, phone, email)

## Blocks launch
- [ ] **Business address** (owner is getting a commercial address). Needed for SAM.gov, Google Business Profile and LocalBusiness structured data. Not published until confirmed.
- [x] Domain: eautoandtransport.com (Namecheap; DNS on Namecheap hosting nameservers, mail MX on jellyfish.systems; keep MX, change only @ A and www)
- [ ] Netlify site + custom domain + HTTPS; Resend sender domain
- [ ] Resend account + the 3 Netlify environment variables, then one live test enquiry
- [ ] Owner approves the wording on every page

## Confirm per service (available now / through a partner / planned)
| Service | Evidence that would let us say more |
|---|---|
| Non-Emergency Medical Transportation | Vehicles (wheelchair-accessible?), driver screening, Georgia NEMT broker enrollment if Medicaid trips |
| Medical Delivery / Medical Courier | Handling rules (temperature, chain of custody), any HIPAA business associate agreements |
| Airport, group, corporate, personalized transport | Vehicle type and seats; for-hire passenger authority required in Georgia |
| Towing | Tow vehicle, Georgia towing permit/registration, insurance |
| Auto services and mobile mechanics | Who performs it, where, any certifications |
| Move-in / move-out hauling | Household-goods mover rules if moving for hire |
| New car enquiries assistance | Scope (advice only vs. brokering) |

## Vendor details (publish only when verified)
SAM.gov UEI/CAGE, USDOT/MC numbers if applicable, insurance limits (general liability, commercial auto, workers' comp), MBE/WBE/WOSB/DBE status, final NAICS codes.

## Hosting (2026-11-24)
- Public site: GitHub Pages from branch `gh-pages` (contents of `public/` + CNAME), custom domain eautoandtransport.com. Rebuild: `python3 build.py --site-url https://eautoandtransport.com --api-url https://eautoandtransport.netlify.app/api/request`, then copy `public/` to `gh-pages`.
- Form API: Netlify function at eautoandtransport.netlify.app/api/request (CORS allows the custom domain). Netlify could not attach the domain (held by an old Netlify DNS zone on another team).
- DNS at Namecheap BasicDNS: 4 GitHub A records on @, www CNAME rukkymarz.github.io, TXT verified-for-netlify kept.
