const test=require('node:test');
const assert=require('node:assert/strict');
const {readFileSync,existsSync}=require('node:fs');
const {join}=require('node:path');
const root=join(__dirname,'../public');
const read=name=>readFileSync(join(root,name),'utf8');
const PAGES=['index.html','services.html','government.html','capabilities.html','funding.html','about.html','contact.html','privacy.html'];
test('all pages exist with main landmark, unique title, description and exactly one h1',()=>{
 const titles=new Set();
 for(const p of PAGES){const h=read(p);
  assert.match(h,/<main id="main">/,p);
  const t=h.match(/<title>([^<]+)<\/title>/);assert.ok(t,p);assert.ok(!titles.has(t[1]),'duplicate title '+p);titles.add(t[1]);
  assert.match(h,/name="description" content="[^"]{50,}"/,p);
  assert.equal((h.match(/<h1>/g)||[]).length,1,p);}
});
test('service directory retains all 11 offerings with anchors',()=>{
 const h=read('services.html');
 for(const n of ['Non-Emergency Medical Transportation','Medical Delivery Services','Medical Courier Services','Airport Luggage Transfers &amp; Delivery','Group &amp; Event Transportation','Corporate Transportation','Move-In &amp; Move-Out Hauling','Towing Services','Auto Services &amp; Mobile Mechanics','New Car Enquiries Assistance','Personalized Transport Services'])assert.ok(h.includes(n),n);
 assert.equal((h.match(/<li id="/g)||[]).length,11);
});
test('contact form matches the function fields and warns about health information',()=>{
 const h=read('contact.html');
 for(const n of ['name','phone','email','service','message','consent','formStarted','website','organization','inquiry_type','location','due_date','solicitation'])assert.ok(h.includes(`name="${n}"`),n);
 assert.match(h,/do not include medical records/i);
 assert.match(h,/call 911/i);
});
test('every service option in the form is accepted by the function',async()=>{
 const fn=readFileSync(join(__dirname,'../netlify/functions/request.mjs'),'utf8');
 const opts=[...read('contact.html').matchAll(/<option value="([^"]+)" data-slug/g)].map(m=>m[1].replace(/&amp;/g,'&'));
 assert.equal(opts.length,15);for(const o of opts)assert.ok(fn.includes(`'${o}'`),o);
});
test('public contact details are present and no unverified claims slipped in',()=>{
 for(const p of PAGES){const h=read(p);
  assert.ok(h.includes('tel:+14043547930')&&h.includes('Eautotransport@mail.com'),p);
  assert.doesNotMatch(h,/licensed|insured|bonded|certified|24\/7|years of experience|USDOT|award-winning|5-star/i,p);}
});
test('static assets exist',()=>{for(const f of ['assets/site.css','assets/site.js','assets/favicon.svg','robots.txt'])assert.ok(existsSync(join(root,f)),f);});
