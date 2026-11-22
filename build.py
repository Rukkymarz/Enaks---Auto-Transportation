#!/usr/bin/env python3
"""Build the ENAKS site into ./public (Netlify publish folder).

  python3 build.py                         # production (form posts to /api/request)
  python3 build.py --preview               # review build: form validates but never sends
  python3 build.py --site-url https://...  # adds canonical tags + sitemap.xml once the domain is live

Content comes from the owner's template (enaks_website_github_ready). Publish only owner-confirmed facts.
"""
import argparse, html, json, os, re, shutil

ap = argparse.ArgumentParser(); ap.add_argument('--site-url', default=''); ap.add_argument('--preview', action='store_true'); A = ap.parse_args()
SITE = A.site_url.rstrip('/')
ROOT = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.join(ROOT, 'public')
LEGAL = 'ENAKS Auto and Transportations LLC'
PHONE, TEL, EMAIL = '(404) 354-7930', '+14043547930', 'Eautotransport@mail.com'
E = html.escape

def ico(d, extra=''):
    return f'<svg viewBox="0 0 24 24" aria-hidden="true" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"{extra}>{d}</svg>'
I = {
 'heart': '<path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1.1-1.1a5.5 5.5 0 0 0-7.8 7.8L12 21l8.8-8.6a5.5 5.5 0 0 0 0-7.8Z"/>',
 'box': '<path d="m12 2 9 5-9 5-9-5 9-5Zm-9 5v10l9 5 9-5V7M12 12v10"/>',
 'plane': '<path d="M17.8 19.2 16 11l3.5-3.5A2.1 2.1 0 0 0 16.5 4.5L13 8 4.8 6.2 3 8l6.5 3.5L7 14H4l-1 1 3 2 2 3 1-1v-3l2.5-2.5L15 20Z"/>',
 'users': '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
 'brief': '<rect x="3" y="7" width="18" height="13" rx="2"/><path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2M3 13h18"/>',
 'pin': '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 1 1 16 0Z"/><circle cx="12" cy="10" r="2.5"/>',
 'pill': '<path d="m10.5 20.5-7-7a5 5 0 0 1 7-7l7 7a5 5 0 0 1-7 7ZM8.5 8.5l7 7"/>',
 'route': '<circle cx="6" cy="19" r="2.5"/><circle cx="18" cy="5" r="2.5"/><path d="M8.5 19H17a3.5 3.5 0 0 0 0-7H7a3.5 3.5 0 0 1 0-7h8.5"/>',
 'wrench': '<path d="M14.7 6.3a4 4 0 0 0 5 5L22 14l-8 8-2.3-2.3a4 4 0 0 0-5-5L3 11l8-8Z" transform="scale(.9) translate(1.3 1.3)"/>',
 'tow': '<path d="M3 17h2m4 0h6m4 0h2V12l-3-5h-5v10M3 17V9h8"/><circle cx="7" cy="17" r="2"/><circle cx="17" cy="17" r="2"/><path d="m3 9 6-5"/>',
 'truck': '<path d="M3 7h11v9H3zM14 10h4l3 3v3h-7z"/><circle cx="7" cy="18" r="2"/><circle cx="17" cy="18" r="2"/>',
 'car': '<path d="M5 17h14v-5l-2-5H7l-2 5v5Zm0 0v2m14-2v2M5 12h14"/><circle cx="8" cy="14.5" r="1"/><circle cx="16" cy="14.5" r="1"/>',
 'cal': '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/>',
 'shield': '<path d="M12 2 4 5v6c0 5 3.4 8.6 8 11 4.6-2.4 8-6 8-11V5l-8-3Z"/><path d="m9 12 2 2 4-4"/>',
 'phone': '<path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1 1 .4 1.9.7 2.8a2 2 0 0 1-.5 2.1L8 9.9a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.8.7a2 2 0 0 1 1.7 2Z"/>',
 'mail': '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 6-10 7L2 6"/>',
 'arrow': '<path d="M5 12h14m-6-6 6 6-6 6"/>',
 'menu': '<path d="M4 7h16M4 12h16M4 17h16"/>',
 'gov': '<path d="M3 21h18M5 21V10m4 11V10m6 11V10m4 11V10M2 10l10-6 10 6"/>',
 'spark': '<path d="m12 3 2 6 6 2-6 2-2 6-2-6-6-2 6-2 2-6Z"/>',
}
ARR = ico(I['arrow'])

# Owner's 11 services, owner's 4 groups. Wording from the template, capacity claims softened.
GROUPS = [
 ('medical', 'Medical and personal care', 'Rides for appointments, dialysis, therapy and outpatient visits.', [
   ('Non-Emergency Medical Transportation', 'heart', 'Care-centred rides for seniors and individuals going to appointments, dialysis, therapy and outpatient visits. Accessibility and timing are confirmed before every trip.', 'Non-emergency only'),
 ]),
 ('passenger', 'Passenger services', 'Airport, group, corporate and personalised trips.', [
   ('Airport Luggage Transfers & Delivery', 'plane', 'Pickup, drop-off and luggage transfers that make travel days easier.', None),
   ('Group & Event Transportation', 'users', 'Coordinated travel for small groups, private gatherings and special occasions.', None),
   ('Corporate Transportation', 'brief', 'Transportation for meetings, business visits, staff and clients.', None),
   ('Personalized Transport Services', 'pin', 'Tell us what you need, and we explore a transportation plan built around your circumstances.', None),
 ]),
 ('delivery', 'Delivery and logistics', 'Prescriptions, supplies and scheduled courier runs.', [
   ('Medical Delivery Services', 'pill', 'Delivery requests for prescriptions, healthcare supplies and approved medical materials, subject to handling requirements.', None),
   ('Medical Courier Services', 'route', 'Scheduled courier support for clinics, pharmacies and healthcare operations.', None),
 ]),
 ('auto', 'Auto and hauling', 'Towing, mobile mechanics, moving help and car buying.', [
   ('Towing Services', 'tow', 'Vehicle towing and recovery requests, with scheduling and service area confirmed in advance.', None),
   ('Auto Services & Mobile Mechanics', 'wrench', 'Vehicle diagnostics, maintenance and repair requests, including fleet vehicles, where service is available.', None),
   ('Move-In & Move-Out Hauling', 'truck', 'Help with small loads, household items and relocation moves.', None),
   ('New Car Enquiries Assistance', 'car', 'Personal guidance for people researching or arranging their next vehicle purchase.', None),
 ]),
]
SERVICES = [s[0] for g in GROUPS for s in g[3]]
EXTRA = ['Fleet or agency contract', 'Teaming or subcontracting', 'Funding or grant partnership', 'General enquiry']
slug = lambda s: re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')

NAV = [('index.html', 'Home'), ('services.html', 'Services'), ('business.html', 'Business and government'), ('about.html', 'About'), ('contact.html', 'Contact')]

def page(fname, title, desc, main):
    canon = f'<link rel="canonical" href="{SITE}/{"" if fname == "index.html" else fname}">' if SITE else ''
    ld = {"@context": "https://schema.org", "@type": "Organization", "name": LEGAL, "telephone": TEL, "email": EMAIL,
          "description": "Non-emergency medical transportation, passenger services, medical delivery and courier, towing, hauling and mobile auto services, based in Georgia."}
    if SITE: ld["url"] = SITE + "/"
    nav = ''.join(f'<a href="{h}"{" aria-current=\"page\"" if h == fname else ""}>{t}</a>' for h, t in NAV)
    mnav = ''.join(f'<li><a href="{h}"{" aria-current=\"page\"" if h == fname else ""}>{t}</a></li>' for h, t in NAV)
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
{canon}
<meta property="og:type" content="website"><meta property="og:title" content="{E(title)}"><meta property="og:description" content="{E(desc)}"><meta property="og:image" content="assets/hero-transport.webp">
<meta name="theme-color" content="#edf2f5">
<link rel="icon" href="assets/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lexend:wght@300;350;400;450;500;600&family=Unbounded:wght@500;600&display=swap">
<link rel="stylesheet" href="assets/site.css">
<script type="application/ld+json">{json.dumps(ld)}</script>
<script src="assets/site.js" defer></script>
</head>
<body{" data-preview" if A.preview else ""}>
<a class="skip" href="#main">Skip to content</a>
<header class="site-head"><div class="shell head-in">
 <a class="brand" href="index.html" aria-label="ENAKS home"><b>ENAKS<i>.</i></b><small>AUTO AND TRANSPORTATIONS LLC</small></a>
 <nav class="nav" aria-label="Main">{nav}</nav>
 <a class="head-phone" href="tel:{TEL}">{ico(I['phone'])}{PHONE}</a>
 <a class="btn" href="contact.html">Request a ride {ARR}</a>
 <button class="menu-btn" aria-expanded="false" aria-controls="m-nav" aria-label="Open menu">{ico(I['menu'])}</button>
 <nav class="m-nav" id="m-nav" aria-label="Mobile"><ul>{mnav}<li><a href="tel:{TEL}">Call {PHONE}</a></li></ul></nav>
</div></header>
<main id="main">
{main}
</main>
<footer class="site-foot"><div class="shell">
 <div class="foot-grid">
  <div><a class="brand" href="index.html" aria-label="ENAKS home"><b>ENAKS<i>.</i></b><small>AUTO AND TRANSPORTATIONS LLC</small></a>
   <p>Thoughtful transportation and auto services, coordinated around the people who count on us. Based in Georgia. Availability is confirmed for each request.</p></div>
  <div><h2>Explore</h2><ul><li><a href="services.html">Services</a></li><li><a href="business.html">Business and government</a></li><li><a href="funding.html">Funding and community</a></li><li><a href="about.html">About</a></li></ul></div>
  <div><h2>Requests</h2><ul><li><a href="contact.html#svc-{slug(SERVICES[0])}">Request a ride</a></li><li><a href="contact.html#svc-medical-courier-services">Courier request</a></li><li><a href="contact.html#quote">Quote for a bid</a></li><li><a href="contact.html#teaming">Teaming</a></li></ul></div>
  <div><h2>Talk to us</h2><ul><li><a href="tel:{TEL}">{PHONE}</a></li><li><a href="mailto:{EMAIL}">{EMAIL}</a></li><li>For emergencies, call 911.</li></ul></div>
 </div>
 <div class="foot-base"><span>&copy; <span id="year">2026</span> {LEGAL}</span><span><a href="privacy.html">Privacy</a></span></div>
</div></footer>
<div class="callbar"><a class="btn" href="tel:{TEL}">{ico(I['phone'])} Call</a><a class="btn btn--light" href="contact.html">Request a ride</a></div>
</body>
</html>
'''

def page_hero(h1, lead):
    return f'<section class="page-hero"><div class="shell"><h1>{h1}</h1><p class="lead">{lead}</p></div></section>'

reach = f'<div class="reach"><a href="tel:{TEL}">{ico(I["phone"])}{PHONE}</a><a href="mailto:{EMAIL}">{ico(I["mail"])}{EMAIL}</a></div>'

# Hero route: Home -> Clinic -> Pharmacy -> Airport, drawn over the template photo.
ROUTE = 'M48 404 C 92 330 112 236 172 212 S 250 318 304 330 S 520 370 590 340'
hero_svg = f'''<svg class="route-svg" viewBox="0 0 640 440" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
 <path id="route" class="route-path-bg" d="{ROUTE}"/>
 <path class="route-path" d="{ROUTE}" pathLength="1"/>
 <g class="stop"><circle class="ring" cx="48" cy="404" r="10"/><circle class="core" cx="48" cy="404" r="3.5"/><text x="66" y="410">Home</text></g>
 <g class="stop"><circle class="ring" cx="172" cy="212" r="10"/><circle class="core" cx="172" cy="212" r="3.5"/><text x="150" y="190">Clinic</text></g>
 <g class="stop"><circle class="ring" cx="304" cy="330" r="10"/><circle class="core" cx="304" cy="330" r="3.5"/><text x="232" y="362">Pharmacy</text></g>
 <g class="stop"><circle class="ring" cx="590" cy="340" r="10"/><circle class="core" cx="590" cy="340" r="3.5"/><text x="534" y="316">Airport</text></g>
 <g class="vehicle"><circle class="halo" r="15"/><circle class="dot" r="7"/>
  <animateMotion dur="10s" repeatCount="indefinite" rotate="auto" keyPoints="0;1" keyTimes="0;1" calcMode="linear"><mpath href="#route"/></animateMotion></g>
</svg>'''

transit = ''.join(f'<li class="station"><h3><a href="services.html#{gid}">{gname}</a></h3><ul>' + ''.join(f'<li>{E(s[0])}</li>' for s in items) + '</ul></li>' for gid, gname, _, items in GROUPS)

pages = {}
pages['index.html'] = ('ENAKS Auto and Transportations | Medical transportation, courier, towing and auto services in Georgia',
 'Non-emergency medical transportation, airport and group trips, medical delivery and courier, towing, hauling and mobile auto services. Call (404) 354-7930 or send a request.',
 f'''<section class="hero"><div class="shell hero-grid">
 <div>
  <p class="kicker">Here for the moments that matter</p>
  <h1>Care in every journey.</h1>
  <p class="lead">Rides to appointments, medical deliveries, airport and group trips, towing and auto care, coordinated by people who listen first.</p>
  <div class="actions"><a class="btn" href="contact.html#svc-{slug(SERVICES[0])}">Request a ride {ARR}</a><a class="btn btn--ghost" href="contact.html#svc-medical-delivery-services">Request a delivery</a></div>
  <p class="hero-note">{ico(I['phone'])}<span>Prefer to talk? Call <a href="tel:{TEL}">{PHONE}</a>.</span></p>
 </div>
 <figure class="route-card" style="margin:0">
  <picture><source media="(max-width: 680px)" srcset="assets/hero-transport-small.webp"><img src="assets/hero-transport.webp" alt="An older woman getting a helping hand as she steps out of a passenger van" width="1600" height="900" fetchpriority="high"></picture>
  {hero_svg}
  <figcaption class="route-status"><span class="live" aria-live="off">Route in progress</span><button class="motion-btn" type="button" aria-pressed="false">Pause motion</button></figcaption>
 </figure>
</div></section>

<section class="section section--white"><div class="shell">
 <div class="head-row"><h2>Four ways we can help, one point of contact.</h2><div><p>Everyday travel, healthcare deliveries and practical auto support. Service area and availability are confirmed for each request.</p><a class="text-link" href="services.html">See all 11 services {ARR}</a></div></div>
 <ol class="transit" aria-label="Service groups">{transit}</ol>
</div></section>

<section class="section section--ink grid-bg"><div class="shell statement">
 <p class="kicker" style="color:#7fe0d3">Our promise</p>
 <div><h2>Good service is more than getting from A to B.</h2><p style="margin-top:1.2rem">It means feeling heard, being treated with respect, and knowing someone is looking after the details. That is the standard we are building at ENAKS.</p>
 <div class="actions"><a class="btn btn--light" href="about.html">Get to know us {ARR}</a></div></div>
</div></section>

<section class="section"><div class="shell">
 <div class="head-row"><h2>People first. Always.</h2><p>Simple principles behind every request.</p></div>
 <ul class="values">
  <li><span class="ic">{ico(I['heart'])}</span><h3>People come first</h3><p>Every request deserves patience, clear communication and genuine care.</p></li>
  <li><span class="ic">{ico(I['cal'])}</span><h3>Thoughtful planning</h3><p>From timing to special arrangements, we listen before we coordinate.</p></li>
  <li><span class="ic">{ico(I['shield'])}</span><h3>No surprises</h3><p>A request becomes a trip only after we both confirm the details.</p></li>
 </ul>
</div></section>

<section class="section section--white"><div class="shell steps-wrap">
 <div><h2>Simple from the start.</h2><p class="lead" style="margin-top:1rem">Have a specific need? We help you work out the next step.</p><div class="actions"><a class="btn btn--ghost" href="contact.html">Send a request {ARR}</a></div></div>
 <ol class="steps">
  <li><h3>Tell us what you need</h3><p>Choose a service and share where, when and who is travelling.</p></li>
  <li><h3>We review the details</h3><p>We confirm availability, accessibility and anything needed to plan.</p></li>
  <li><h3>Move forward with confidence</h3><p>Once both sides confirm, we coordinate the trip or job with you.</p></li>
 </ol>
</div></section>

<section class="section"><div class="shell cols">
 <div><p class="kicker">For organizations</p><h2>Clinics, businesses and public agencies.</h2></div>
 <div><p>Scheduled courier runs for healthcare operations, transportation for staff and events, fleet auto support, and quotes or teaming for public contracts.</p><div class="actions"><a class="btn" href="business.html">Business and government {ARR}</a></div></div>
</div></section>

<section class="section section--ink grid-bg"><div class="shell cta">
 <div><h2>Where can we take you next?</h2><p style="margin-top:1rem">Ask about transportation, a delivery, towing, or a service built around your needs.</p>{reach}</div>
 <div class="actions"><a class="btn btn--light" href="contact.html">Request a ride {ARR}</a><a class="btn btn--line" href="contact.html#svc-general-enquiry">Send a message</a></div>
</div></section>''')

def group_html(gid, gname, gdesc, items):
    cards = ''.join(
        f'<li class="svc" id="{slug(n)}"><span class="ic">{ico(I[ic])}</span><h3>{E(n)}{f" <span class=\"badge\">{b}</span>" if b else ""}</h3>'
        f'<p>{d}</p><a class="ask" href="contact.html#svc-{slug(n)}">Ask about this service {ico(I["arrow"])}</a></li>' for n, ic, d, b in items)
    return f'<section class="group" id="{gid}"><div class="group-head"><span class="node" aria-hidden="true"></span><h2>{gname}</h2></div><p class="lead" style="margin-bottom:1.4rem">{gdesc}</p><ul class="svc-list">{cards}</ul></section>'

pages['services.html'] = ('Services | ENAKS Auto and Transportations',
 'All 11 ENAKS services: non-emergency medical transportation, airport luggage transfers, group, corporate and personalized transport, medical delivery and courier, towing, mobile mechanics, hauling and new car assistance.',
 page_hero('Support for every kind of journey.', 'Eleven services in four groups. Service area and availability are confirmed for each request.') +
 '<div class="shell">' + ''.join(group_html(*g) for g in GROUPS) + '</div>' +
 f'''<section class="section section--white"><div class="shell cols"><div><p class="note"><strong>Medical transportation is non-emergency only.</strong> For emergencies, call 911. Vehicle accessibility, handling of medical items, timing and availability are confirmed before any trip.</p></div>
 <div><h2>Something specific?</h2><p style="margin-top:.8rem">Tell us what you have in mind and we discuss possible next steps.</p>{reach}<div class="actions"><a class="btn" href="contact.html">Send a request {ARR}</a></div></div></div></section>''')

pages['business.html'] = ('Business and government | ENAKS Auto and Transportations',
 'Courier, transportation and fleet auto services for clinics, businesses and agencies. Quotes for public bids and teaming with prime contractors.',
 page_hero('For clinics, businesses and public agencies.', 'Scheduled courier support, staff and event transportation, fleet auto services, and quotes or teaming for public contracts.') +
 f'''<section class="section"><div class="shell cols">
 <div><h2>Bids, quotes and teaming</h2><p style="margin-top:1rem">Send a solicitation and we tell you whether the scope and location fit before you plan around us. Prime contractors can ask about subcontracting the same way.</p>
 <div class="actions"><a class="btn" href="contact.html#quote">Request a quote {ARR}</a><a class="btn btn--ghost" href="contact.html#teaming">Discuss teaming</a></div></div>
 <div><h2>Vendor details</h2><p style="margin-top:1rem">Registration details and our capability statement are shared once verified. Ask for them in your request and we send what is confirmed.</p>
 <p class="note">Registrations, certifications and insurance appear on this site only after they are verified.</p></div>
</div></section>
<section class="section section--white"><div class="shell steps-wrap">
 <div><h2>How a request is handled</h2><p class="lead" style="margin-top:1rem">The same steps for a single courier run or a multi-site contract.</p></div>
 <ol class="steps">
  <li><h3>You send the scope</h3><p>Locations, timing, volumes, and any solicitation number or link.</p></li>
  <li><h3>We confirm fit</h3><p>Service area, schedule, vehicles and any special handling.</p></li>
  <li><h3>You get a written answer</h3><p>A quote, a teaming reply, or a clear no.</p></li>
  <li><h3>Service starts</h3><p>On the agreed schedule, with records kept for each job.</p></li>
 </ol>
</div></section>
<section class="section"><div class="shell">
 <div class="head-row"><h2>Industry codes we are aligning to</h2><p>2022 NAICS titles. Final codes are set at registration.</p></div>
 <table class="codes"><thead><tr><th scope="col">NAICS</th><th scope="col">Official title</th><th scope="col">Our service</th></tr></thead><tbody>
 <tr><td>485991</td><td>Special Needs Transportation</td><td>Non-emergency medical transportation</td></tr>
 <tr><td>492110</td><td>Couriers and Express Delivery Services</td><td>Medical courier services</td></tr>
 <tr><td>492210</td><td>Local Messengers and Local Delivery</td><td>Medical delivery services</td></tr>
 <tr><td>485999</td><td>All Other Transit and Ground Passenger Transportation</td><td>Airport, group, corporate and personalized transport</td></tr>
 <tr><td>488410</td><td>Motor Vehicle Towing</td><td>Towing services</td></tr>
 <tr><td>811111</td><td>General Automotive Repair</td><td>Auto services, mobile mechanics, fleet vehicles</td></tr>
 <tr><td>484210</td><td>Used Household and Office Goods Moving</td><td>Move-in and move-out hauling</td></tr>
 </tbody></table>
 <h2 style="margin-top:3.5rem">Past performance</h2><p style="margin-top:1rem">We publish project examples only with the client's approval. Ask for references in your request and we share what we can.</p>
 <p><a class="text-link" href="funding.html">Funding and community partnerships {ARR}</a></p>
</div></section>''')

pages['funding.html'] = ('Funding and community | ENAKS Auto and Transportations',
 'Where funding would make the biggest difference for ENAKS: vehicle readiness, driver training, dispatch capacity and getting people without a car to care.',
 page_hero('Getting more people to care, on time.', 'Where outside funding would make the biggest difference, and how funders and partners can reach us.') +
 f'''<section class="section"><div class="shell cols">
 <div><h2>Growth priorities</h2><ul style="margin-top:1rem">
  <li><strong>Vehicle readiness.</strong> Inspected, accessible vehicles so trips happen on time.</li>
  <li><strong>Driver training.</strong> Local drivers trained for passenger, medical-transport and courier work.</li>
  <li><strong>Dispatch capacity.</strong> Scheduling that takes on more trips without missed pickups.</li>
  <li><strong>Local mobility.</strong> Getting seniors and people without a car to appointments, dialysis and therapy.</li></ul></div>
 <div><h2>Planned outcomes</h2><p style="margin-top:1rem">Each funded project gets targets, such as drivers trained, vehicles ready for service and trips completed. These are targets, not past results, and we report against them.</p>
 <p class="note">Applications, budgets and supporting records are shared privately with funders, not published here.</p>
 <div class="actions"><a class="btn" href="contact.html#funding">Contact us about funding {ARR}</a></div></div>
</div></section>''')

pages['about.html'] = ('About | ENAKS Auto and Transportations',
 'ENAKS Auto and Transportations LLC is a Georgia-based, multi-service transportation and auto-care provider for individuals, seniors, families, healthcare providers and businesses.',
 page_hero('A little more care, every step of the way.', 'We make everyday transportation and auto needs feel more personal, more dependable and less complicated.') +
 f'''<section class="section"><div class="shell cols">
 <div><h2>Built around people.</h2></div>
 <div><p class="lead">{LEGAL} is a multi-service transportation and auto-care provider helping individuals, seniors, families, healthcare providers and businesses feel supported.</p>
 <p>Our services span non-emergency medical transportation, delivery and courier requests, airport transfers, towing, hauling, auto support and personalized transport coordination.</p>
 <p>Whatever brings you to us, we listen closely, communicate clearly, and handle your request with attention and respect.</p></div>
</div></section>
<section class="section section--ink grid-bg"><div class="shell statement"><p class="kicker" style="color:#7fe0d3">Our mission</p>
 <div><h2>Peace of mind, comfort and dependable support with every ride, delivery and request.</h2></div></div></section>
<section class="section"><div class="shell">
 <div class="head-row"><h2>Our values in motion.</h2><p>How we handle every request.</p></div>
 <ul class="values">
  <li><span class="ic">{ico(I['heart'])}</span><h3>People come first</h3><p>Every request deserves patience, clear communication and genuine care.</p></li>
  <li><span class="ic">{ico(I['cal'])}</span><h3>Thoughtful planning</h3><p>From timing to special arrangements, we listen before we coordinate.</p></li>
  <li><span class="ic">{ico(I['shield'])}</span><h3>Dependable support</h3><p>Practical, professional help for everyday journeys and logistics.</p></li>
 </ul>
 <div class="actions"><a class="btn" href="contact.html">Start a conversation {ARR}</a></div>
</div></section>''')

opts = ''.join(f'<option value="{E(n)}" data-slug="{slug(n)}">{E(n)}</option>' for n in SERVICES + EXTRA)
def fld(id_, label, inp, opt=False, err=True):
    return f'<div class="field"><label for="{id_}">{label}{" <span class=\"opt\">(optional)</span>" if opt else ""}</label>{inp}{f"<span class=\"err\" id=\"{id_}-err\"></span>" if err else ""}</div>'
FORM = f'''<form id="contact-form" class="form" novalidate>
 <h2>How can we help?</h2><p>All fields are required unless marked optional.</p>
 <div class="row">{fld('name', 'Your name', '<input id="name" name="name" autocomplete="name" required maxlength="100" data-label="your name">')}
 {fld('phone', 'Phone', '<input id="phone" name="phone" type="tel" autocomplete="tel" required maxlength="30" data-label="a phone number">')}</div>
 {fld('email', 'Email', '<input id="email" name="email" type="email" autocomplete="email" required maxlength="150" data-label="an email address">')}
 <div class="row">{fld('service', 'Service', f'<select id="service" name="service" required data-label="a service"><option value="">Choose a service</option>{opts}</select>')}
 {fld('location', 'Service location', '<input id="location" name="location" required maxlength="150" data-label="the service location" placeholder="City and state">')}</div>
 {fld('message', 'Details', '<span class="hint" id="message-hint">Pickup and drop-off area, preferred date and time, number of people or items. Do not include medical records, diagnoses or patient ID numbers.</span><textarea id="message" name="message" required maxlength="2000" data-label="the details" aria-describedby="message-hint"></textarea>')}
 <details class="extra"><summary>For businesses and agencies</summary>
  {fld('organization', 'Organization', '<input id="organization" name="organization" autocomplete="organization" maxlength="150" data-label="an organization">', True)}
  <div class="row">{fld('inquiry_type', 'Type of request', '<select id="inquiry_type" name="inquiry_type" data-label="a request type"><option value="">Choose one</option><option value="ride">Ride or passenger trip</option><option value="delivery">Delivery or courier</option><option value="quote">Quote for a bid or contract</option><option value="teaming">Teaming or subcontracting</option><option value="commercial">Business or fleet service</option><option value="funding">Funding or grant partnership</option><option value="other">Something else</option></select>', True)}
  {fld('due_date', 'Date needed or response due', '<input id="due_date" name="due_date" type="date" data-label="a date">', True)}</div>
  {fld('solicitation', 'Solicitation link or number', '<input id="solicitation" name="solicitation" maxlength="300" data-label="a solicitation" placeholder="Official portal link or ID">', True)}
 </details>
 <div class="check"><input id="consent" name="consent" type="checkbox" required data-label="consent"><label for="consent">I agree that ENAKS may contact me about this request. Sending it does not confirm a booking. <a href="privacy.html">Privacy notice</a></label></div><span class="err" id="consent-err"></span>
 <input type="hidden" id="formStarted" name="formStarted" value="">
 <div class="trap" aria-hidden="true"><label for="website">Leave empty</label><input id="website" name="website" tabindex="-1" autocomplete="off"></div>
 <button class="btn" type="submit">Send request {ARR}</button>
 <div class="status" role="status" aria-live="polite" tabindex="-1"></div>
</form>'''

pages['contact.html'] = ('Contact | ENAKS Auto and Transportations',
 'Call (404) 354-7930, email Eautotransport@mail.com, or send a request for a ride, delivery, towing, auto service, quote or teaming.',
 page_hero("We're here to help.", 'Call, email, or send the details. We review every request and reply to confirm next steps.') +
 f'''<section class="section"><div class="shell contact-grid">
 <div><h2>Talk to a person.</h2>
  <ul class="ways">
   <li><a href="tel:{TEL}"><span class="ic">{ico(I['phone'])}</span><span><b>{PHONE}</b><span>Call</span></span></a></li>
   <li><a href="mailto:{EMAIL}"><span class="ic">{ico(I['mail'])}</span><span><b>{EMAIL}</b><span>Email</span></span></a></li>
   <li><div><span class="ic">{ico(I['pin'])}</span><span><b>Based in Georgia</b><span>Routes and coverage confirmed for each request</span></span></div></li>
  </ul>
  <p class="note"><strong>Please don't share health details here.</strong> No medical records, diagnoses or patient identifiers. For an emergency, call 911.</p>
 </div>
 {FORM}
</div></section>''')

pages['privacy.html'] = ('Privacy | ENAKS Auto and Transportations', 'How ENAKS handles information sent through the website request form.',
 page_hero('Your privacy matters to us.', 'How we handle information you send through this website.') +
 f'''<section class="section"><div class="shell" style="max-width:820px">
 <h2>What we collect</h2><p style="margin-top:.8rem">The request form asks for your name, phone, email, the service you need, the location and the details you choose to share. Organization, dates and solicitation numbers are optional.</p>
 <h2 style="margin-top:2.2rem">How we use it</h2><p style="margin-top:.8rem">Only to review and reply to your request. Sending a request does not confirm a reservation or service.</p>
 <h2 style="margin-top:2.2rem">How it travels</h2><p style="margin-top:.8rem">Your details pass through our website host and email-delivery provider to our inbox. We do not publish or sell submissions. Those providers may keep technical or delivery records under their own policies.</p>
 <h2 style="margin-top:2.2rem">Sensitive information</h2><p style="margin-top:.8rem">Do not include diagnoses, medical records, patient or insurance ID numbers, or payment card details. The form blocks common health details. This website is not a patient portal or an emergency channel. For emergencies, call 911.</p>
 <h2 style="margin-top:2.2rem">Your choices</h2><p style="margin-top:.8rem">To correct or delete information you sent us, call {PHONE} or email {EMAIL}.</p>
</div></section>''')

# ---------- write ----------
if os.path.exists(OUT): shutil.rmtree(OUT)
os.makedirs(os.path.join(OUT, 'assets'))
for f in ('site.css', 'site.js'): shutil.copy(os.path.join(ROOT, 'src', f), os.path.join(OUT, 'assets', f))
for f in ('hero-transport.webp', 'hero-transport-small.webp'): shutil.copy(os.path.join(ROOT, 'src', 'img', f), os.path.join(OUT, 'assets', f))
with open(os.path.join(OUT, 'assets', 'favicon.svg'), 'w') as fh:
    fh.write('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect width="32" height="32" rx="9" fill="#0b1f33"/><path d="M8 23c4 0 4-6 8-6s4-6 8-6" fill="none" stroke="#14b8a6" stroke-width="3" stroke-linecap="round"/><circle cx="24" cy="11" r="3" fill="#ffb23f"/></svg>')
for fname, (t, d, m) in pages.items():
    with open(os.path.join(OUT, fname), 'w') as fh: fh.write(page(fname, t, d, m))
with open(os.path.join(OUT, 'robots.txt'), 'w') as fh: fh.write('User-agent: *\nAllow: /\n' + (f'Sitemap: {SITE}/sitemap.xml\n' if SITE else ''))
if SITE:
    with open(os.path.join(OUT, 'sitemap.xml'), 'w') as fh:
        fh.write('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + ''.join(f'<url><loc>{SITE}/{"" if f == "index.html" else f}</loc></url>' for f in pages) + '</urlset>\n')
print(f'built {len(pages)} pages -> public/ | preview={A.preview} | site url: {SITE or "(not set)"}')
