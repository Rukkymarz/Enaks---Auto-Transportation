// ENAKS site script: nav, hero route sequence (+ pause), transit line reveal, enquiry form.
(function () {
  'use strict';
  var doc = document.documentElement;
  doc.classList.add('js');
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // ---- mobile nav ----
  var btn = document.querySelector('.menu-btn'), mnav = document.getElementById('m-nav');
  if (btn && mnav) {
    var setOpen = function (open) {
      if (open) mnav.setAttribute('data-open', ''); else mnav.removeAttribute('data-open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');
    };
    btn.addEventListener('click', function () { setOpen(!mnav.hasAttribute('data-open')); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && mnav.hasAttribute('data-open')) { setOpen(false); btn.focus(); } });
  }

  // ---- hero route: draw, light stops, then the vehicle runs (pausable) ----
  var card = document.querySelector('.route-card');
  if (card) {
    var svg = card.querySelector('svg'), pause = card.querySelector('.motion-btn'), live = card.querySelector('.live');
    var setPaused = function (p) {
      if (!svg || !svg.pauseAnimations) return;
      if (p) svg.pauseAnimations(); else svg.unpauseAnimations();
      card.classList.toggle('is-paused', p);
      if (pause) { pause.textContent = p ? 'Play motion' : 'Pause motion'; pause.setAttribute('aria-pressed', p ? 'true' : 'false'); }
      if (live) live.textContent = p ? 'Route paused' : 'Route in progress';
    };
    if (reduce) { setPaused(true); if (pause) pause.hidden = true; if (live) live.textContent = 'Example route'; }
    else {
      if (svg && svg.pauseAnimations) svg.pauseAnimations();               // hold the vehicle until the route has drawn
      setTimeout(function () { card.classList.add('is-live'); }, 120);   // let the hidden start state paint first
      setTimeout(function () { if (!card.classList.contains('is-paused')) setPaused(false); }, 2100);
      if (pause) pause.addEventListener('click', function () { setPaused(!card.classList.contains('is-paused')); });
    }
  }

  // ---- transit line draws when it scrolls into view ----
  var transit = document.querySelector('.transit');
  if (transit) {
    if (reduce || !('IntersectionObserver' in window)) transit.classList.add('in-view');
    else {
      var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { transit.classList.add('in-view'); io.disconnect(); } }); }, { threshold: .35 });
      io.observe(transit);
      setTimeout(function () { transit.classList.add('in-view'); }, 4000); // never leave it undrawn
    }
  }

  // ---- year ----
  var y = document.getElementById('year'); if (y) y.textContent = String(new Date().getFullYear());

  // ---- enquiry form -> /api/request ----
  var form = document.getElementById('contact-form');
  if (!form) return;
  var PREVIEW = document.body.hasAttribute('data-preview');
  var PHI = /\b(diagnos\w*|medicaid (id|number)|member id|insurance id|policy number|dob|date of birth|patient name|medical record|mrn)\b/i;
  var started = document.getElementById('formStarted'); if (started) started.value = String(Date.now());

  // preselect: ?service=Name (live site) or #svc-slug / #teaming (preview frame allows hash only)
  var svcSel = document.getElementById('service'), typeSel = document.getElementById('inquiry_type'), extra = form.querySelector('details.extra');
  try { var q = new URLSearchParams(location.search).get('service'); if (q && svcSel) Array.prototype.forEach.call(svcSel.options, function (o) { if (o.value === q) svcSel.value = q; }); } catch (e) {}
  var h = decodeURIComponent((location.hash || '').slice(1));
  if (h.indexOf('svc-') === 0 && svcSel) { var o = svcSel.querySelector('option[data-slug="' + h.slice(4) + '"]'); if (o) svcSel.value = o.value; }
  if (h && typeSel && typeSel.querySelector('option[value="' + h + '"]')) { typeSel.value = h; if (extra && ['quote', 'teaming', 'funding', 'commercial'].indexOf(h) > -1) extra.open = true; }

  var status = form.querySelector('.status');
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
    if (el.type === 'email' && v && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(v)) return setErr(el, 'Enter an email like name@example.com.');
    if (el.type === 'tel' && v && v.replace(/\D/g, '').length < 7) return setErr(el, 'Enter a phone number with area code.');
    if (el.id === 'message' && v && v.length < 10) return setErr(el, 'Add a little more detail (at least 10 characters).');
    if (el.id === 'solicitation' && v && /^http:/i.test(v)) return setErr(el, 'Use the https link from the official portal, or the solicitation number.');
    if (el.id === 'due_date' && v && v < new Date().toISOString().slice(0, 10)) return setErr(el, 'This date has passed. Enter a current date, or leave it blank.');
    if ((el.id === 'message' || el.id === 'location') && PHI.test(v)) return setErr(el, 'Remove patient or health details. Describe the service need only.');
    return setErr(el, '');
  }
  fields.forEach(function (el) { el.addEventListener('blur', function () { if (el.value) check(el); }); el.addEventListener('input', function () { if (el.getAttribute('aria-invalid')) check(el); }); });
  function say(html, kind) { status.innerHTML = html; status.className = 'status is-' + kind; status.focus(); }

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    if (!fields.map(check).every(Boolean)) {
      var first = form.querySelector('[aria-invalid="true"]');
      if (first && extra && extra.contains(first)) extra.open = true;
      say('Check the highlighted fields, then send again.', 'error'); if (first) first.focus(); return;
    }
    var data = {};
    Array.prototype.forEach.call(form.elements, function (el) { if (el.name) data[el.name] = el.type === 'checkbox' ? el.checked : el.value.trim(); });
    data.formStarted = Number(data.formStarted);
    if (PREVIEW) { say('<strong>Preview: request not sent.</strong> Every field passed. On the live site it goes straight to the ENAKS inbox.', 'ok'); return; }
    var b = form.querySelector('button[type="submit"]'), label = b.innerHTML; b.disabled = true; b.textContent = 'Sending';
    say('Sending your request.', 'info');
    var ctl = new AbortController(), t = setTimeout(function () { ctl.abort(); }, 12000);
    fetch('https://eautoandtransport.netlify.app/api/request', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data), signal: ctl.signal })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { if (!r.ok) throw new Error(j.message || 'The request did not send.'); }); })
      .then(function () { form.reset(); if (started) started.value = String(Date.now()); say('<strong>Request sent.</strong> We will call or email you to confirm the details. A request is not a booking until we both confirm.', 'ok'); })
      .catch(function (err) { say((err.name === 'AbortError' ? 'The connection timed out.' : err.message) + ' You can also call <a href="tel:+14043547930">(404) 354-7930</a>.', 'error'); })
      .then(function () { clearTimeout(t); b.disabled = false; b.innerHTML = label; });
  });
})();
