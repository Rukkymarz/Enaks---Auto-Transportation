#!/usr/bin/env python3
"""Build the ENAKS Auto and Transportations LLC site into ./public (Netlify publish folder).

  python3 build.py                         # production build (form posts to /api/request)
  python3 build.py --preview               # preview build: form validates but never sends
  python3 build.py --site-url https://...  # adds canonical tags + sitemap.xml once the domain is live

Copy rule: publish only facts the owner has confirmed. Everything else lives in LAUNCH-CHECKLIST.md.
"""
import argparse, html, json, os, re, shutil

ap = argparse.ArgumentParser(); ap.add_argument('--site-url', default=''); ap.add_argument('--preview', action='store_true'); a = ap.parse_args()
SITE_URL = a.site_url.rstrip('/')
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, 'public')

LEGAL = 'ENAKS Auto and Transportations LLC'
SHORT = 'ENAKS Auto and Transportations'
PHONE_DISPLAY, PHONE_TEL = '(404) 354-7930', '+14043547930'
EMAIL = 'Eautotransport@mail.com'

NAV = [('index.html', 'Home'), ('services.html', 'Services'), ('government.html', 'Government'), ('capabilities.html', 'Capabilities'),
       ('funding.html', 'Funding'), ('about.html', 'About'), ('contact.html', 'Contact')]

ARROW = {
 'up': '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M20 4 32 18h-8v18h-8V18H8z" fill="#fff"/></svg>',
 'upright': '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M34 6v16l-5.6-5.6L11 33.8 6.2 29l17.4-17.4L18 6z" fill="#fff"/></svg>',
 'right': '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M36 20 22 32v-8H4v-8h18V8z" fill="#fff"/></svg>',
 'cross': '<svg viewBox="0 0 40 40" aria-hidden="true"><path d="M15 5h10v10h10v10H25v10H15V25H5V15h10z" fill="#fff"/></svg>',
}
MARK = ('<svg viewBox="0 0 30 30" aria-hidden="true"><rect x="1" y="1" width="28" height="28" rx="6" fill="#00694f"/>'
        '<rect x="3.5" y="3.5" width="23" height="23" rx="4" fill="none" stroke="#fff" stroke-width="1.6"/>'
        '<path d="M15 7.5 21 14h-3.6v8.5h-4.8V14H9z" fill="#fff"/></svg>')

# The owner's 11 services, grouped by the owner's own categories. Wording kept close to the owner's copy;
# capacity claims ("on-demand", "dependable") removed until confirmed.
CATS = [
 ('medical', 'Medical and personal care', 'cross', [
   ('Non-Emergency Medical Transportation', 'Rides for seniors and individuals going to appointments, dialysis, therapy and outpatient visits. Vehicle accessibility and timing are confirmed before any ride.', 'Non-emergency only'),
 ]),
 ('passenger', 'Passenger services', 'up', [
   ('Airport Luggage Transfers & Delivery', 'Pickup, drop-off and luggage transfer to make travel days easier.', None),
   ('Group & Event Transportation', 'Coordinated travel for small groups, private gatherings and special occasions.', None),
   ('Corporate Transportation', 'Transportation for meetings, business visits, staff and clients.', None),
   ('Personalized Transport Services', 'Tell us what you need and we look at a transportation plan built around it.', None),
 ]),
 ('delivery', 'Delivery and logistics', 'right', [
   ('Medical Delivery Services', 'Delivery of prescriptions, healthcare supplies and approved medical materials, subject to handling requirements.', None),
   ('Medical Courier Services', 'Scheduled courier support for clinics, pharmacies and healthcare operations.', None),
 ]),
 ('auto', 'Auto and hauling', 'upright', [
   ('Auto Services & Mobile Mechanics', 'Vehicle diagnostics, maintenance and repair requests, including fleet vehicles, where service is available.', None),
   ('Towing Services', 'Vehicle towing and recovery requests. Scheduling and service area are confirmed in advance.', None),
   ('Move-In & Move-Out Hauling', 'Help with small loads, household items and relocation moves.', None),
   ('New Car Enquiries Assistance', 'Guidance for people researching or arranging their next vehicle purchase.', None),
 ]),
]
SERVICE_NAMES = [s[0] for _, _, _, items in CATS for s in items]
EXTRA_OPTIONS = ['Fleet or agency contract', 'Teaming or subcontracting', 'Funding or grant partnership', 'General enquiry']
slug = lambda s: re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

def page(fname, title, desc, body):
    canonical = f'<link rel="canonical" href="{SITE_URL}/{"" if fname=="index.html" else fname}">' if SITE_URL else ''
    ld = {"@context": "https://schema.org", "@type": "Organization", "name": LEGAL, "telephone": PHONE_TEL, "email": EMAIL,
          "description": "Non-emergency medical transportation, passenger services, medical delivery and courier, towing, hauling and auto services."}
    if SITE_URL: ld["url"] = SITE_URL + '/'
    nav = ''.join(f'<li><a href="{h}"{" aria-current=\"page\"" if h==fname else ""}>{t}</a></li>' for h, t in NAV)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(desc)}">
{canonical}
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:type" content="website">
<meta name="theme-color" content="#00694f">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Overpass:wght@400;600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="assets/site.css">
<script type="application/ld+json">{json.dumps(ld)}</script>
</head>
<body{" data-preview" if a.preview else ""}>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="wrap">
  <a class="mark" href="index.html">{MARK}<span>{SHORT}</span></a>
  <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">Menu</button>
  <nav id="site-nav" class="nav" aria-label="Main"><ul>{nav}</ul></nav>
</div></header>
<main id="main">
{body}
</main>
<footer class="site-foot"><div class="wrap">
  <div><p><strong>{LEGAL}</strong><br>Based in Georgia. Service area and availability are confirmed for each request.</p>
  <p><a href="tel:{PHONE_TEL}">{PHONE_DISPLAY}</a><br><a href="mailto:{EMAIL}">{EMAIL}</a></p>
  <p>For emergencies, call 911.</p></div>
  <ul><li><a href="contact.html">Send an enquiry</a></li><li><a href="contact.html#teaming">Teaming</a></li><li><a href="funding.html">Funding partners</a></li><li><a href="privacy.html">Privacy</a></li></ul>
</div></footer>
<script src="assets/site.js" defer></script>
</body>
</html>
'''

def inner_sign(h1, lede):
    return f'''<div class="sign-zone"><div class="wrap"><div class="sign sign--small"><div class="sign-inner">
<h1>{h1}</h1><p class="lede">{lede}</p></div></div></div></div>'''

def services_list():
    out = []
    for cid, cname, _, items in CATS:
        rows = ''.join(
            f'<li id="{slug(n)}"><div><h3>{html.escape(n)}</h3>{f"<span class=\"plate status\">{p}</span>" if p else ""}</div>'
            f'<p>{d}</p><p class="who"><a href="contact.html#svc-{slug(n)}">Ask about this service</a></p></li>' for n, d, p in items)
        out.append(f'<section id="{cid}"><div class="wrap"><h2>{cname}</h2><ul class="svc">{rows}</ul></div></section>')
    return ''.join(out)

def contact_block():
    return f'''<p class="reach"><a href="tel:{PHONE_TEL}">Call {PHONE_DISPLAY}</a> <span aria-hidden="true">|</span> <a href="mailto:{EMAIL}">{EMAIL}</a></p>'''

opts = ''.join(f'<option value="{html.escape(n)}" data-slug="{slug(n)}">{html.escape(n)}</option>' for n in SERVICE_NAMES + EXTRA_OPTIONS)
FORM = f'''<form id="contact-form" class="inquiry" novalidate>
 <div class="field"><label for="name">Your name</label><input id="name" name="name" autocomplete="name" required data-label="your name"><span class="err" id="name-err"></span></div>
 <div class="field"><label for="phone">Phone</label><input id="phone" name="phone" type="tel" autocomplete="tel" required data-label="a phone number"><span class="err" id="phone-err"></span></div>
 <div class="field"><label for="email">Email</label><input id="email" name="email" type="email" autocomplete="email" required data-label="an email address"><span class="err" id="email-err"></span></div>
 <div class="field"><label for="organization">Organization <span class="hint">(optional)</span></label><input id="organization" name="organization" autocomplete="organization" data-label="an organization"><span class="err" id="organization-err"></span></div>
 <div class="field"><label for="inquiry_type">What kind of request?</label>
  <select id="inquiry_type" name="inquiry_type" required data-label="the kind of request">
   <option value="">Choose one</option><option value="ride">A ride or passenger trip</option><option value="delivery">A delivery or courier job</option>
   <option value="quote">A quote for a bid or contract</option><option value="teaming">Teaming or subcontracting</option>
   <option value="commercial">Business or fleet service</option><option value="funding">Funding or grant partnership</option><option value="other">Something else</option>
  </select><span class="err" id="inquiry_type-err"></span></div>
 <div class="field"><label for="service">Service</label><select id="service" name="service" required data-label="a service"><option value="">Choose a service</option>{opts}</select><span class="err" id="service-err"></span></div>
 <div class="field"><label for="location">Service location</label><input id="location" name="location" required data-label="the service location" placeholder="City and state"><span class="err" id="location-err"></span></div>
 <div class="field"><label for="due_date">Date needed or response due <span class="hint">(optional)</span></label><input id="due_date" name="due_date" type="date" data-label="a date"><span class="err" id="due_date-err"></span></div>
 <div class="field field--wide"><label for="message">Details</label><span class="hint" id="message-hint">Pickup and drop-off area, timing, number of people or items, vehicle type. Do not include medical records, diagnoses, insurance or patient ID numbers.</span>
  <textarea id="message" name="message" required data-label="the details" aria-describedby="message-hint" maxlength="2000"></textarea><span class="err" id="message-err"></span></div>
 <div class="field field--wide"><label for="solicitation">Solicitation link or number <span class="hint">(optional, for agencies and primes)</span></label><input id="solicitation" name="solicitation" data-label="a solicitation" placeholder="Official portal link or ID"><span class="err" id="solicitation-err"></span></div>
 <div class="field field--wide check"><input id="consent" name="consent" type="checkbox" required data-label="consent"><label for="consent">I agree that ENAKS may contact me about this enquiry. Sending an enquiry does not confirm a booking. <a href="privacy.html">Privacy</a></label><span class="err" id="consent-err"></span></div>
 <input type="hidden" id="formStarted" name="formStarted" value="">
 <div class="trap" aria-hidden="true"><label for="website">Leave empty</label><input id="website" name="website" tabindex="-1" autocomplete="off"></div>
 <div class="field field--wide"><button class="btn" type="submit">Send enquiry</button></div>
 <div class="form-status" role="status" tabindex="-1" aria-live="polite"></div>
</form>'''

pages = {}
dest = ''.join(f'<li>{ARROW[arr]}<a href="services.html#{cid}">{cname}</a></li>' for cid, cname, arr, _ in CATS)
pages['index.html'] = (f'{SHORT} | Medical transportation, courier, towing and auto services in Georgia',
 'Non-emergency medical transportation, airport and group transportation, medical delivery and courier, towing, hauling and mobile auto services. Enquire by phone or online.',
 f'''<div class="sign-zone"><div class="wrap">
<div class="sign sign--home">
 <a class="exit-tab" href="contact.html"><span>Request a service</span></a>
 <div class="sign-inner">
  <h1>{SHORT}</h1>
  <p class="lede">Rides, deliveries, towing and auto care for people, healthcare providers, businesses and public agencies. Tell us where and when, and we confirm what we can do.</p>
  <ul class="dest" aria-label="Service groups">{dest}</ul>
 </div>
</div>
<div class="sign-post" aria-hidden="true"><i></i><i></i></div>
{contact_block()}
</div></div>
<section><div class="wrap">
 <h2>Who we work with</h2>
 <ul class="buyers"><li>Individuals, seniors and families</li><li>Clinics, pharmacies and care providers</li><li>Businesses and event planners</li><li>Public fleet managers and agencies</li><li>Prime contractors</li><li>Funders and community partners</li></ul>
</div></section>
<section><div class="wrap cols">
 <div><h2>Need a ride or a delivery?</h2><p>Send the pickup area, timing and what you need. We confirm availability before anything is scheduled. For emergencies, call 911.</p>
 <div class="actions"><a class="btn" href="contact.html#ride">Ask about a ride</a><a class="btn btn--quiet" href="contact.html#delivery">Ask about a delivery</a></div></div>
 <div><h2>Bidding or teaming?</h2><p>Share a solicitation, ask for a quote, or talk to us about subcontracting under your prime.</p>
 <div class="actions"><a class="btn btn--quiet" href="government.html">Government and teaming</a></div></div>
</div></section>''')

pages['services.html'] = (f'Services | {SHORT}',
 'All 11 ENAKS services: non-emergency medical transportation, airport luggage transfers, group, corporate and personalized transport, medical delivery and courier, mobile mechanics, towing, hauling and new car assistance.',
 inner_sign('Services', 'Eleven services in four groups. Availability and service area are confirmed for each request.') + services_list() + '''
<section><div class="wrap"><p class="note"><strong>Medical transportation is non-emergency only.</strong> For emergencies, call 911. Vehicle accessibility, handling of medical items, timing and availability are confirmed before any trip.</p></div></section>''')

pages['government.html'] = (f'Government contracting and teaming | {SHORT}',
 'Quotes for public bids and subcontracting with prime contractors for non-emergency medical transportation, courier and delivery, towing and fleet auto services.',
 inner_sign('Government contracting and teaming', 'For federal, state and municipal buyers, and prime contractors looking for a transportation or auto-services subcontractor.') + '''
<section><div class="wrap cols">
 <div><h2>How to work with us</h2>
 <p>Send a solicitation and we tell you whether the scope and location fit before you plan around us. We review teaming and subcontracting requests the same way.</p>
 <div class="actions"><a class="btn" href="contact.html#quote">Request a quote</a><a class="btn btn--quiet" href="contact.html#teaming">Discuss teaming</a></div></div>
 <div><h2>Vendor details</h2>
 <p>Registration details and our capability statement are shared once verified. Ask for them in your enquiry and we send what is confirmed.</p>
 <p class="note">We list registrations, certifications and insurance on this site only after they are verified.</p></div>
</div></section>
<section><div class="wrap">
 <h2>Industry codes we are aligning to</h2>
 <p class="muted">2022 NAICS titles. Final codes are set at registration.</p>
 <table class="codes"><thead><tr><th scope="col">NAICS</th><th scope="col">Official title</th><th scope="col">Our services</th></tr></thead><tbody>
 <tr><td>485991</td><td>Special Needs Transportation</td><td>Non-emergency medical transportation</td></tr>
 <tr><td>492110</td><td>Couriers and Express Delivery Services</td><td>Medical courier services</td></tr>
 <tr><td>492210</td><td>Local Messengers and Local Delivery</td><td>Medical delivery services</td></tr>
 <tr><td>485999</td><td>All Other Transit and Ground Passenger Transportation</td><td>Airport, group, corporate and personalized transport</td></tr>
 <tr><td>488410</td><td>Motor Vehicle Towing</td><td>Towing services</td></tr>
 <tr><td>811111</td><td>General Automotive Repair</td><td>Auto services and mobile mechanics, fleet vehicles</td></tr>
 <tr><td>484210</td><td>Used Household and Office Goods Moving</td><td>Move-in and move-out hauling</td></tr>
 </tbody></table>
</div></section>''')

pages['capabilities.html'] = (f'Capabilities and past performance | {SHORT}',
 'How ENAKS handles a request from enquiry to service, and where approved project examples will be published.',
 inner_sign('Capabilities and past performance', 'How a request moves from enquiry to service.') + '''
<section><div class="wrap">
 <h2>How a request is handled</h2>
 <ol class="steps">
  <li><h3>You send the details</h3><p>Location, timing, people or items, and any solicitation.</p></li>
  <li><h3>We confirm fit</h3><p>Service area, schedule, vehicle and any special handling.</p></li>
  <li><h3>You get a clear answer</h3><p>A quote, a teaming reply, or a plain no.</p></li>
  <li><h3>Service is scheduled</h3><p>Only after both sides confirm. An enquiry is not a booking.</p></li>
 </ol>
</div></section>
<section><div class="wrap">
 <h2>Past performance</h2>
 <p>We publish project examples here only with the client's approval. Ask for references in your enquiry and we share what we can.</p>
 <div class="actions"><a class="btn btn--quiet" href="contact.html#quote">Ask for references</a></div>
</div></section>''')

pages['funding.html'] = (f'Funding and community impact | {SHORT}',
 'Growth priorities for vehicle readiness, driver training, dispatch capacity and dependable local transportation, including non-emergency medical transportation.',
 inner_sign('Funding and community impact', 'Where outside funding would make the biggest difference, and how funders and partners can reach us.') + '''
<section><div class="wrap cols">
 <div><h2>Growth priorities</h2>
 <ul>
  <li><strong>Vehicle readiness.</strong> Inspected, accessible vehicles so trips happen on time.</li>
  <li><strong>Driver training.</strong> Train local drivers for passenger, medical-transport and courier work.</li>
  <li><strong>Dispatch capacity.</strong> Scheduling that can take on more trips without missed pickups.</li>
  <li><strong>Local mobility.</strong> Getting seniors and people without a car to appointments, dialysis and therapy.</li>
 </ul></div>
 <div><h2>Planned outcomes</h2>
 <p>We set targets for each funded project, such as drivers trained, vehicles ready for service and trips completed. These are targets, not past results, and we report against them.</p>
 <p class="note">Applications, budgets and supporting records are shared privately with funders, not published here.</p>
 <div class="actions"><a class="btn" href="contact.html#funding">Contact us about funding</a></div></div>
</div></section>''')

pages['about.html'] = (f'About | {SHORT}',
 'ENAKS Auto and Transportations LLC is a Georgia-based multi-service transportation and auto-care company for individuals, healthcare providers, businesses and agencies.',
 inner_sign('About ENAKS', 'A multi-service transportation and auto-care company, built around listening first.') + f'''
<section><div class="wrap cols">
 <div><h2>What we do</h2>
 <p>{LEGAL} helps individuals, seniors, families, healthcare providers, businesses and public agencies with non-emergency medical transportation, deliveries and courier work, airport and group transportation, towing, hauling and auto support.</p>
 <p>Whatever brings you to us, we listen, confirm what is possible, and communicate clearly.</p></div>
 <div><h2>How we work</h2>
 <ul><li><strong>People first.</strong> Every request gets patience and a clear answer.</li>
 <li><strong>Plan before we move.</strong> Timing, access and special arrangements are confirmed up front.</li>
 <li><strong>No surprises.</strong> An enquiry is never treated as a booking until you confirm.</li></ul></div>
</div></section>
<section><div class="wrap"><h2>Talk to us</h2>{contact_block()}<div class="actions"><a class="btn" href="contact.html">Send an enquiry</a></div></div></section>''')

pages['contact.html'] = (f'Contact | {SHORT}',
 'Call (404) 354-7930, email Eautotransport@mail.com, or send an enquiry for rides, deliveries, towing, auto services, quotes, teaming or funding.',
 inner_sign('Contact', 'Call, email, or send the details below. Please do not include patient or health information.') + f'''
<section><div class="wrap">
 {contact_block()}
 <p class="muted">Enquiries are not bookings. For emergencies, call 911.</p>
 {FORM}
</div></section>''')

pages['privacy.html'] = (f'Privacy | {SHORT}', 'How ENAKS handles information sent through the website enquiry form.',
 inner_sign('Privacy', 'How we handle information sent through this website.') + f'''
<section><div class="wrap">
 <h2>What we collect</h2><p>The enquiry form asks for your name, phone, email, the service you need, the location, and details you choose to share. Organization, dates and solicitation numbers are optional.</p>
 <h2>How we use it</h2><p>Only to review and reply to your enquiry. Sending an enquiry does not confirm a reservation or service.</p>
 <h2>How it travels</h2><p>When you send the form, your details pass through our website host and email-delivery provider to our inbox. We do not publish submissions or sell them. Those providers may keep technical or delivery records under their own policies.</p>
 <h2>Sensitive information</h2><p>Do not include diagnoses, medical records, insurance or patient ID numbers, or payment card details. The form blocks common health details. This website is not a patient portal or an emergency channel. For emergencies, call 911.</p>
 <h2>Your choices</h2><p>To correct or delete information you sent us, call {PHONE_DISPLAY} or email {EMAIL}.</p>
</div></section>''')

# ---------- write ----------
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, 'assets'))
shutil.copy(os.path.join(ROOT, 'src', 'site.css'), os.path.join(OUT, 'assets', 'site.css'))
shutil.copy(os.path.join(ROOT, 'src', 'site.js'), os.path.join(OUT, 'assets', 'site.js'))
with open(os.path.join(OUT, 'assets', 'favicon.svg'), 'w') as fh: fh.write(MARK.replace('aria-hidden="true"', 'xmlns="http://www.w3.org/2000/svg"'))
for fname, (title, desc, body) in pages.items():
    with open(os.path.join(OUT, fname), 'w') as fh: fh.write(page(fname, title, desc, body))
with open(os.path.join(OUT, 'robots.txt'), 'w') as fh:
    fh.write('User-agent: *\nAllow: /\n' + (f'Sitemap: {SITE_URL}/sitemap.xml\n' if SITE_URL else ''))
if SITE_URL:
    urls = ''.join(f'<url><loc>{SITE_URL}/{"" if f=="index.html" else f}</loc></url>' for f in pages)
    with open(os.path.join(OUT, 'sitemap.xml'), 'w') as fh:
        fh.write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>\n')
print(f'built {len(pages)} pages -> public/ | preview={a.preview} | site url: {SITE_URL or "(not set)"}')
