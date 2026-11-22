const test=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync,existsSync}=require('node:fs');
const {join}=require('node:path');
const root=join(__dirname,'../public');
const read=n=>readFileSync(join(root,n),'utf8');
const PAGES=['index.html','services.html','business.html','funding.html','about.html','contact.html','privacy.html'];
test('every page: main landmark, unique title, real description, exactly one h1, skip link',()=>{
 const seen=new Set();
 for(const p of PAGES){const h=read(p);
  assert.match(h,/<main id="main">/,p); assert.match(h,/class="skip" href="#main"/,p);
  const t=h.match(/<title>([^<]+)<\/title>/); assert.ok(t,p); assert.ok(!seen.has(t[1]),'dup title '+p); seen.add(t[1]);
  assert.match(h,/name="description" content="[^"]{60,}"/,p);
  assert.equal((h.match(/<h1[ >]/g)||[]).length,1,p);}
});
test('all 11 services listed with anchors',()=>{
 const h=read('services.html');
 for(const n of ['Non-Emergency Medical Transportation','Medical Delivery Services','Medical Courier Services','Airport Luggage Transfers &amp; Delivery','Group &amp; Event Transportation','Corporate Transportation','Move-In &amp; Move-Out Hauling','Towing Services','Auto Services &amp; Mobile Mechanics','New Car Enquiries Assistance','Personalized Transport Services'])assert.ok(h.includes(n),n);
 assert.equal((h.match(/<li class="svc" id="/g)||[]).length,11);
});
test('no "Book" wording: the site takes requests, not bookings',()=>{for(const p of PAGES)assert.doesNotMatch(read(p),/>\s*Book a ride|Book now/i,p);});
test('contact form fields match the Netlify function and warn about health details',()=>{
 const h=read('contact.html');
 for(const n of ['name','phone','email','service','location','message','consent','formStarted','website','organization','inquiry_type','due_date','solicitation'])assert.ok(h.includes(`name="${n}"`),n);
 assert.match(h,/do not include medical records/i); assert.match(h,/call 911/i);
 const fn=readFileSync(join(__dirname,'../netlify/functions/request.mjs'),'utf8');
 const opts=[...h.matchAll(/<option value="([^"]+)" data-slug/g)].map(m=>m[1].replace(/&amp;/g,'&'));
 assert.equal(opts.length,15); for(const o of opts)assert.ok(fn.includes(`'${o}'`),'function rejects option '+o);
});
test('phone and email on every page; no unverified claims',()=>{
 for(const p of PAGES){const h=read(p);
  assert.ok(h.includes('tel:+14043547930')&&h.includes('Eautotransport@mail.com'),p);
  assert.doesNotMatch(h,/\blicensed\b|\binsured\b|\bbonded\b|\bcertified\b|24\/7|years of experience|USDOT|award-winning|5-star/i,p);}
});
test('motion is accessible: pause control and reduced-motion rules exist',()=>{
 assert.match(read('index.html'),/class="motion-btn"[^>]*aria-pressed/);
 assert.match(read('assets/site.css'),/prefers-reduced-motion: reduce/);
});
test('assets exist',()=>{for(const f of ['assets/site.css','assets/site.js','assets/favicon.svg','assets/hero-transport.webp','assets/hero-transport-small.webp','robots.txt'])assert.ok(existsSync(join(root,f)),f);});
