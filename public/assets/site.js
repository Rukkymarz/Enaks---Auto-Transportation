// ENAKS site script: mobile nav + enquiry form -> Netlify Function /api/request.
// <body data-preview> (set by `build.py --preview`) validates but never sends, and says so.
(function () {
  'use strict';
  var toggle = document.querySelector('.nav-toggle');
  var nav = document.getElementById('site-nav');
  if (toggle && nav) {
    var close = function () { nav.classList.remove('is-open'); toggle.setAttribute('aria-expanded', 'false'); };
    toggle.addEventListener('click', function () {
      var open = nav.classList.toggle('is-open');
      toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && nav.classList.contains('is-open')) { close(); toggle.focus(); } });
  }

  var form = document.getElementById('contact-form');
  if (!form) return;
  var PREVIEW = document.body.hasAttribute('data-preview');
  var PHI = /\b(diagnos\w*|medicaid (id|number)|member id|insurance id|policy number|dob|date of birth|patient name|medical record|mrn)\b/i;
  var started = document.getElementById('formStarted');
  if (started) started.value = String(Date.now());

  // Preselect from #hash (query strings are not allowed in the preview frame): contact.html#teaming, #svc-towing-services
  var h = decodeURIComponent((location.hash || '').slice(1));
  var typeSel = document.getElementById('inquiry_type'), svcSel = document.getElementById('service');
  if (h && typeSel && typeSel.querySelector('option[value="' + h + '"]')) typeSel.value = h;
  if (h.indexOf('svc-') === 0 && svcSel) { var o = svcSel.querySelector('option[data-slug="' + h.slice(4) + '"]'); if (o) svcSel.value = o.value; }

  var status = form.querySelector('.form-status');
  var fields = Array.prototype.slice.call(form.querySelectorAll('input:not([type=hidden]):not(.trap input), select, textarea'));

  function setErr(el, msg) {
    var box = document.getElementById(el.id + '-err');
    if (msg) el.setAttribute('aria-invalid', 'true'); else el.removeAttribute('aria-invalid');
    if (box) box.textContent = msg || '';
    return !msg;
  }
  function check(el) {
    var v = el.type === 'checkbox' ? el.checked : (el.value || '').trim();
    if (el.required && !v) return setErr(el, el.type === 'checkbox' ? 'Tick the box so we can reply to you.' : 'Enter ' + el.dataset.label + '.');
    if (el.type === 'email' && v && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)) return setErr(el, 'Enter an email address like name@example.com.');
    if (el.type === 'tel' && v && v.replace(/\D/g, '').length < 7) return setErr(el, 'Enter a phone number with area code.');
    if (el.id === 'message' && v && v.length < 10) return setErr(el, 'Add a little more detail (at least 10 characters).');
    if (el.id === 'solicitation' && v && /^http:/i.test(v)) return setErr(el, 'Use the https link from the official portal, or the solicitation number.');
    if (el.id === 'due_date' && v && v < new Date().toISOString().slice(0, 10)) return setErr(el, 'This date has passed. Enter the current due date, or leave it blank.');
    if ((el.id === 'message' || el.id === 'location') && PHI.test(v)) return setErr(el, 'Remove patient or health details. Describe the service need only.');
    return setErr(el, '');
  }
  fields.forEach(function (el) { el.addEventListener('blur', function () { if (el.value) check(el); }); });

  function say(html, kind) { status.innerHTML = html; status.className = 'form-status is-' + kind; status.focus(); }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    var ok = fields.map(check).every(Boolean);
    if (!ok) {
      say('Check the highlighted fields, then send again.', 'error');
      var first = form.querySelector('[aria-invalid="true"]'); if (first) first.focus();
      return;
    }
    var data = {};
    Array.prototype.forEach.call(form.elements, function (el) { if (el.name) data[el.name] = el.type === 'checkbox' ? el.checked : el.value.trim(); });
    data.formStarted = Number(data.formStarted);
    if (PREVIEW) { say('<strong>Preview: enquiry not sent.</strong> Every field passed validation. On the live site this goes to the ENAKS inbox.', 'ok'); return; }
    var btn = form.querySelector('button[type="submit"]'); btn.disabled = true; btn.textContent = 'Sending';
    var ctl = new AbortController(); var timer = setTimeout(function () { ctl.abort(); }, 12000);
    fetch('/api/request', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data), signal: ctl.signal })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok) throw new Error(j.message || 'The enquiry did not send.'); }); })
      .then(function () { form.reset(); if (started) started.value = String(Date.now()); say('<strong>Enquiry sent.</strong> We reply by phone or email. Sending an enquiry does not confirm a booking.', 'ok'); })
      .catch(function (err) { say((err.name === 'AbortError' ? 'The connection timed out.' : err.message) + ' You can also call (404) 354-7930.', 'error'); })
      .then(function () { clearTimeout(timer); btn.disabled = false; btn.textContent = 'Send enquiry'; });
  });
})();
