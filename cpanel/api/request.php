<?php
/* ENAKS public enquiry handler for Namecheap cPanel hosting (PHP mail()).
 * Mirrors netlify/functions/request.mjs: same fields, limits, honeypot, timing check, health-detail block.
 * Not a patient portal. Edit the two addresses below if the inbox or sender changes. */
const CONTACT_EMAIL = 'Eautotransport@mail.com';
const FROM_EMAIL    = 'noreply@eautoandtransport.com';

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store');
header('X-Content-Type-Options: nosniff');
function out($status, $message) { http_response_code($status); echo json_encode(['message' => $message]); exit; }

$services = ['Non-Emergency Medical Transportation','Medical Delivery Services','Medical Courier Services',
  'Airport Luggage Transfers & Delivery','Group & Event Transportation','Corporate Transportation',
  'Move-In & Move-Out Hauling','Towing Services','Auto Services & Mobile Mechanics',
  'New Car Enquiries Assistance','Personalized Transport Services','Fleet or agency contract','Teaming or subcontracting','Funding or grant partnership','General enquiry'];
$inquiries = ['','ride','delivery','quote','teaming','commercial','funding','other'];
$PHI = '/\b(diagnos\w*|medicaid (id|number)|member id|insurance id|policy number|dob|date of birth|patient name|medical record|mrn)\b/i';

if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') out(405, 'Only POST requests are allowed.');
if (stripos($_SERVER['CONTENT_TYPE'] ?? '', 'application/json') !== 0) out(415, 'Please send a JSON request.');
if ((int)($_SERVER['CONTENT_LENGTH'] ?? 0) > 12000) out(413, 'Request too large.');
$text = file_get_contents('php://input', false, null, 0, 12001);
if ($text === false) out(400, 'Unable to read request.');
if (strlen($text) > 12000) out(413, 'Request too large.');
$body = json_decode($text, true);
if (!is_array($body) || array_key_exists(0, $body)) out(400, 'Invalid request format.');

$t = function ($k) use ($body) { return isset($body[$k]) && is_string($body[$k]) ? trim($body[$k]) : ''; };
if ($t('website') !== '') out(200, 'Request received.'); // honeypot

$name=$t('name'); $phone=$t('phone'); $email=$t('email'); $service=$t('service'); $message=$t('message');
$org=$t('organization'); $inq=$t('inquiry_type'); $loc=$t('location'); $due=$t('due_date'); $sol=$t('solicitation');
$len = function ($s) { return mb_strlen($s, 'UTF-8'); };
$started = isset($body['formStarted']) && is_numeric($body['formStarted']) ? (float)$body['formStarted'] : 0;
$nowMs = microtime(true) * 1000;

if ($len($org)>150 || $len($loc)>150 || $len($sol)>300 || !in_array($inq, $inquiries, true)
  || ($due !== '' && !preg_match('/^\d{4}-\d{2}-\d{2}$/', $due))
  || (preg_match('/^https?:/i', $sol) && !preg_match('/^https:\/\//i', $sol))) {
  out(422, 'Please check the optional organization, location, due date and solicitation fields.');
}
if (preg_match($PHI, $message) || preg_match($PHI, $loc)) out(422, 'Please remove patient or health details and describe the service need only.');
$emailOk = $len($email) <= 150 && preg_match('/^[^\s@]+@[^\s@]+\.[^\s@]+$/', $email) && !preg_match('/[\r\n]/', $email);
if ($len($name)<2 || $len($name)>100 || $len($phone)<7 || $len($phone)>30 || !$emailOk || !in_array($service, $services, true)
  || $len($message)<10 || $len($message)>2000 || ($body['consent'] ?? null) !== true
  || $started <= 0 || $nowMs-$started < 1400 || $nowMs-$started > 86400000) {
  out(422, 'Please provide a valid name, phone, email, service, message and consent.');
}

// Light per-IP throttle: 5 sends per 10 minutes.
$ip = preg_replace('/[^0-9a-f:.]/i', '', $_SERVER['REMOTE_ADDR'] ?? 'x');
$f = sys_get_temp_dir() . '/enaks_rl_' . md5($ip);
$hits = array_filter((array)@json_decode(@file_get_contents($f), true), function ($ts) { return $ts > time() - 600; });
if (count($hits) >= 5) out(429, 'Too many requests. Please call (404) 354-7930.');
$hits[] = time(); @file_put_contents($f, json_encode(array_values($hits)));

$clean = function ($s) { return str_replace(["\r", "\n"], ' ', $s); };
$lines = ['New ENAKS website enquiry', "Name: $name", "Phone: $phone", "Email: $email", "Service: $service",
  'Inquiry type: '.($inq ?: '-'), 'Organization: '.($org ?: '-'), 'Location: '.($loc ?: '-'),
  'Response due: '.($due ?: '-'), 'Solicitation: '.($sol ?: '-'), '', "Message:\n$message", '',
  'Please do not process sensitive health information through regular email.'];
$subject = '=?UTF-8?B?' . base64_encode('ENAKS website enquiry: ' . $clean($service)) . '?=';
$headers = implode("\r\n", ['From: ENAKS Website <' . FROM_EMAIL . '>', 'Reply-To: ' . $clean($email),
  'MIME-Version: 1.0', 'Content-Type: text/plain; charset=UTF-8', 'Content-Transfer-Encoding: 8bit']);
$ok = @mail(CONTACT_EMAIL, $subject, implode("\n", $lines), $headers, '-f' . FROM_EMAIL);
if (!$ok) { error_log('ENAKS enquiry mail() failed'); out(502, 'Message delivery is temporarily unavailable. Please call (404) 354-7930.'); }
out(200, 'Message delivered successfully.');
