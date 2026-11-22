const test=require('node:test');
const assert=require('node:assert/strict');
const {pathToFileURL}=require('node:url');
const {join}=require('node:path');
const getHandler=async()=> (await import(pathToFileURL(join(__dirname,'../netlify/functions/request.mjs')))).default;
function sample(){return {name:'Taylor Reed',phone:'4045551212',email:'test@example.org',service:'General enquiry',message:'I would like to ask about your services.',consent:true,formStarted:Date.now()-5000,website:''};}
async function send(body,{method='POST',type='application/json'}={}){
 const handler=await getHandler();
 const request=new Request('https://enaks.test/api/request',{method,headers:{'content-type':type},...(method==='POST'?{body:JSON.stringify(body)}:{})});
 const result=await handler(request,{});
 return {status:result.status,json:await result.json()};
}
test('only POST is accepted',async()=>assert.equal((await send(null,{method:'GET'})).status,405));
test('only JSON is accepted',async()=>assert.equal((await send(sample(),{type:'text/plain'})).status,415));
test('rejects invalid email',async()=>{const b=sample();b.email='bad';assert.equal((await send(b)).status,422)});
test('rejects missing consent',async()=>{const b=sample();b.consent=false;assert.equal((await send(b)).status,422)});
test('rejects rapid bot activity',async()=>{const b=sample();b.formStarted=Date.now();assert.equal((await send(b)).status,422)});
test('honeypot catches bot',async()=>{const b=sample();b.website='lottery';assert.equal((await send(b)).status,200)});
test('unconfigured mail never reports a successful submission',async()=>{
 const previous={RESEND_API_KEY:process.env.RESEND_API_KEY,ENAKS_CONTACT_EMAIL:process.env.ENAKS_CONTACT_EMAIL,ENAKS_FROM_EMAIL:process.env.ENAKS_FROM_EMAIL};
 delete process.env.RESEND_API_KEY; delete process.env.ENAKS_CONTACT_EMAIL; delete process.env.ENAKS_FROM_EMAIL;
 try{assert.equal((await send(sample())).status,503)}finally{for(const [k,v] of Object.entries(previous)){if(v===undefined)delete process.env[k];else process.env[k]=v;}}
});
test('rejects patient details in the message',async()=>{const b=sample();b.message='Ride for patient name Jane, date of birth 1/2/50';assert.equal((await send(b)).status,422)});
test('rejects http (non-https) solicitation links',async()=>{const b=sample();b.solicitation='http://example.gov/rfp';assert.equal((await send(b)).status,422)});
test('rejects unknown inquiry type',async()=>{const b=sample();b.inquiry_type='hack';assert.equal((await send(b)).status,422)});
test('accepts a full procurement enquiry (fails closed only on missing mail config)',async()=>{const b={...sample(),organization:'City of Test Fleet Services',inquiry_type:'quote',service:'Fleet or agency contract',location:'Atlanta, GA',due_date:'2027-01-15',solicitation:'RFP-2027-014'};delete process.env.RESEND_API_KEY;assert.equal((await send(b)).status,503)});
