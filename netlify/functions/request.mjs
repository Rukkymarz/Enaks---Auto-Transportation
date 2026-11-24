/** Public enquiry handler, not a patient portal.
 * Required env: RESEND_API_KEY, ENAKS_CONTACT_EMAIL, ENAKS_FROM_EMAIL.
 * Designed for Netlify Functions (web Request/Response API).
 */
const services=new Set([
  'Non-Emergency Medical Transportation','Medical Delivery Services','Medical Courier Services',
  'Airport Luggage Transfers & Delivery','Group & Event Transportation','Corporate Transportation',
  'Move-In & Move-Out Hauling','Towing Services','Auto Services & Mobile Mechanics',
  'New Car Enquiries Assistance','Personalized Transport Services','Fleet or agency contract','Teaming or subcontracting','Funding or grant partnership','General enquiry'
]);
const safe=value=>String(value).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const trim=value=>typeof value==='string'?value.trim():'';
const emailOk=value=>value.length<=150&&/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
// Same rule as the client: no patient or health details in a general enquiry.
const PHI=/\b(diagnos\w*|medicaid (id|number)|member id|insurance id|policy number|dob|date of birth|patient name|medical record|mrn)\b/i;
const INQUIRY=new Set(['','ride','delivery','quote','teaming','commercial','funding','other']);
// The public site is served from GitHub Pages at the custom domain; allow it to call this function.
const ORIGINS=new Set(['https://eautoandtransport.com','https://www.eautoandtransport.com','https://eautoandtransport.netlify.app']);
let CORS={};
const json=(status,message)=>new Response(JSON.stringify({message}),{status,headers:{'content-type':'application/json; charset=utf-8','cache-control':'no-store','x-content-type-options':'nosniff',...CORS}});
export const config={path:'/api/request'};
export default async function handler(request){
  const origin=request.headers.get('origin')||'';
  CORS=ORIGINS.has(origin)?{'access-control-allow-origin':origin,'access-control-allow-methods':'POST, OPTIONS','access-control-allow-headers':'content-type','access-control-max-age':'86400',vary:'origin'}:{};
  if(request.method==='OPTIONS')return new Response(null,{status:204,headers:CORS});
  if(request.method!=='POST')return json(405,'Only POST requests are allowed.');
  if(!(request.headers.get('content-type')||'').toLowerCase().startsWith('application/json'))return json(415,'Please send a JSON request.');
  const contentLength=Number(request.headers.get('content-length')||0);
  if(contentLength>12000)return json(413,'Request too large.');
  let text;
  try{text=await request.text();}catch{return json(400,'Unable to read request.');}
  if(text.length>12000)return json(413,'Request too large.');
  let body;
  try{body=JSON.parse(text);}catch{return json(400,'Invalid request format.');}
  if(!body||typeof body!=='object'||Array.isArray(body))return json(400,'Invalid request.');
  // Honeypot: pretend success without notifying the business.
  if(trim(body.website))return json(200,'Request received.');
  const name=trim(body.name),phone=trim(body.phone),email=trim(body.email),service=trim(body.service),message=trim(body.message);
  const organization=trim(body.organization),inquiry=trim(body.inquiry_type),location=trim(body.location),due=trim(body.due_date),solicitation=trim(body.solicitation);
  const started=Number(body.formStarted||0);
  if(organization.length>150||location.length>150||solicitation.length>300||!INQUIRY.has(inquiry)||(due&&!/^\d{4}-\d{2}-\d{2}$/.test(due))||(/^https?:/i.test(solicitation)&&!/^https:\/\//i.test(solicitation))){
    return json(422,'Please check the optional organization, location, due date and solicitation fields.');
  }
  if(PHI.test(message)||PHI.test(location)){return json(422,'Please remove patient or health details and describe the service need only.');}
  if(name.length<2||name.length>100||phone.length<7||phone.length>30||!emailOk(email)||!services.has(service)||message.length<10||message.length>2000||body.consent!==true||!Number.isFinite(started)||Date.now()-started<1400||Date.now()-started>86400000){
    return json(422,'Please provide a valid name, phone, email, service, message and consent.');
  }
  const {RESEND_API_KEY,ENAKS_CONTACT_EMAIL,ENAKS_FROM_EMAIL}=process.env;
  if(!RESEND_API_KEY||!ENAKS_CONTACT_EMAIL||!ENAKS_FROM_EMAIL){return json(503,'Online enquiries are not available yet. Please try again later.');}
  const bodyText=['New ENAKS website enquiry',`Name: ${name}`,`Phone: ${phone}`,`Email: ${email}`,`Service: ${service}`,`Inquiry type: ${inquiry||'-'}`,`Organization: ${organization||'-'}`,`Location: ${location||'-'}`,`Response due: ${due||'-'}`,`Solicitation: ${solicitation||'-'}`,'',`Message:\n${message}`,'','Please do not process sensitive health information through regular email.'].join('\n');
  const bodyHtml=`<h2>New ENAKS website enquiry</h2><p><b>Name:</b> ${safe(name)}<br><b>Phone:</b> ${safe(phone)}<br><b>Email:</b> ${safe(email)}<br><b>Service:</b> ${safe(service)}<br><b>Inquiry type:</b> ${safe(inquiry||'-')}<br><b>Organization:</b> ${safe(organization||'-')}<br><b>Location:</b> ${safe(location||'-')}<br><b>Response due:</b> ${safe(due||'-')}<br><b>Solicitation:</b> ${safe(solicitation||'-')}</p><h3>Message</h3><p style="white-space:pre-wrap">${safe(message)}</p><p><small>Do not process sensitive health information through regular email.</small></p>`;
  try{
    const reply=await fetch('https://api.resend.com/emails',{
      method:'POST',headers:{authorization:`Bearer ${RESEND_API_KEY}`,'content-type':'application/json'},
      body:JSON.stringify({from:ENAKS_FROM_EMAIL,to:[ENAKS_CONTACT_EMAIL],reply_to:email,subject:`ENAKS website enquiry: ${service}`,text:bodyText,html:bodyHtml}),
      signal:AbortSignal.timeout(9000)
    });
    if(!reply.ok){console.error('Email delivery rejected',reply.status);return json(502,'Message delivery is temporarily unavailable. Please try again later.');}
    return json(200,'Message delivered successfully.');
  }catch(error){console.error('Email transport error:',error.name);return json(502,'Message delivery is temporarily unavailable. Please try again later.');}
}
