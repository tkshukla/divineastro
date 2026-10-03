/* WhatsApp share buttons (DIVASTRO-107).
 *
 * This audience forwards things on WhatsApp, so the free tools offer a
 * "Share on WhatsApp" button where people naturally want to share: the Kundali
 * Milan score and today's Rahu Kaal / Panchang for their city (tools.js wires
 * them). Every link is tagged utm_source=whatsapp&utm_medium=share&utm_campaign=…,
 * which the visit beacon (visit.js -> app/analytics.py) reads as source "whatsapp".
 *
 * Each button is a real <a href="https://wa.me/?text=…" target="_blank">, so a
 * desktop (or a page whose script failed) just opens WhatsApp in a new tab. On a
 * phone with the Web Share API the click is intercepted and the system share
 * sheet is offered instead, which reaches the WhatsApp app directly.
 *
 * PRIVACY: share texts are built ONLY from a score, today's public almanac
 * values and a city name. Never pass a name, birth date, time or place into any
 * builder here — tests/test_frontend_routes.py checks the Milan builder's inputs.
 *
 * Depends on app.js for `t` and `state` (globals); degrades to English without them.
 */
'use strict';

(() => {
  const SITE = 'https://divineastro.org';

  const lang = () => (typeof state !== 'undefined' && state.lang === 'hi' ? 'hi' : 'en');
  const tr = (k, fallback) => {
    try { const v = t(k); return v && v !== k ? v : fallback; } catch { return fallback; }
  };
  // "{a} and {b}" templates from the i18n table.
  const fill = (tpl, vars) => String(tpl).replace(/\{(\w+)\}/g, (_, k) => (k in vars ? String(vars[k]) : ''));

  function url(path, campaign) {
    const qs = new URLSearchParams({ utm_source: 'whatsapp', utm_medium: 'share', utm_campaign: campaign });
    return `${SITE}${path}${path.includes('?') ? '&' : '?'}${qs}`;
  }

  function waHref(text, link) {
    return `https://wa.me/?text=${encodeURIComponent(`${text} ${link}`)}`;
  }

  /* ---- the SEO city list: /rahu-kaal/<slug> when the city has its own page ---- */
  let cities = null;
  let defaultSlug = 'new-delhi';
  const ready = fetch('/api/share/cities')
    .then((r) => (r.ok ? r.json() : null))
    .then((d) => {
      if (d && Array.isArray(d.cities)) { cities = d.cities; defaultSlug = d.default || defaultSlug; }
    })
    .catch(() => { /* no list: links fall back to the bare tool page */ });

  const norm = (s) => String(s || '').split(',')[0].trim().toLowerCase().replace(/\s+/g, ' ');

  // The SEO city for a place: its name first, else a city centre within ~10 km
  // (GeoNames calls Bengaluru "Bangalore", Gurugram "Gurgaon", …).
  function cityFor(place) {
    if (!cities || !place) return null;
    const name = norm(place.label);
    const byName = cities.find((c) => norm(c.name) === name || norm(c.name_hi) === name);
    if (byName) return byName;
    const lat = Number(place.latitude), lon = Number(place.longitude);
    if (!Number.isFinite(lat) || !Number.isFinite(lon)) return null;
    return cities.find((c) => Math.abs(c.lat - lat) < 0.1 && Math.abs(c.lon - lon) < 0.1) || null;
  }

  // '/rahu-kaal/mumbai', '/rahu-kaal' (the default city's page), or the fallback.
  function cityPath(tool, place, fallback) {
    const c = cityFor(place);
    if (!c) return fallback;
    return c.slug === defaultSlug ? `/${tool}` : `/${tool}/${c.slug}`;
  }

  // The name people will read: the Hindi one for an SEO city in Hindi, else as typed.
  function cityName(place) {
    const c = cityFor(place);
    if (c) return lang() === 'hi' ? c.name_hi : c.name;
    return String((place && place.label) || '').split(',')[0].trim();
  }

  /* ---- share-text builders ---- */
  // Kundali Milan: the score and nothing else. Takes numbers only, on purpose.
  function milanText(score, maximum) {
    return fill(tr('shareMilanText', 'We got {score}/{max} in Kundali Milan 💍 — check yours free:'),
      { score: Number(score), max: Number(maximum) });
  }

  // Today strip / Panchang: public almanac values for a city.
  function todayText(v) {
    return fill(tr('shareTodayText', "Today's Rahu Kaal in {city}: {rahu} · Tithi {tithi} —"), v);
  }
  function panchangText(v) {
    return fill(tr('sharePanchangText', 'Panchang for {city}, {date}: Tithi {tithi} · Nakshatra {nak} · Rahu Kaal {rahu} —'), v);
  }

  /* ---- sending ---- */
  // A phone: the system share sheet reaches the WhatsApp app. A desktop browser
  // may also have navigator.share, but there WhatsApp Web via wa.me is better.
  const isMobile = () => /Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent || '')
    || (navigator.userAgentData && navigator.userAgentData.mobile === true);

  // Point an existing <a class="share-wa"> at a message. Safe to call repeatedly.
  function wire(el, text, link) {
    if (!el) return;
    el.href = waHref(text, link);
    el.target = '_blank';
    el.rel = 'noopener';
    el.dataset.text = text;
    el.dataset.url = link;
    if (el.dataset.wired) return;
    el.dataset.wired = '1';
    el.addEventListener('click', (e) => {
      if (!(isMobile() && typeof navigator.share === 'function')) return;   // the wa.me link opens
      e.preventDefault();
      navigator.share({ text: `${el.dataset.text} ${el.dataset.url}` }).catch((err) => {
        // Cancelled by the person: do nothing. Any other failure: the plain link.
        if (!err || err.name !== 'AbortError') window.location.href = el.href;
      });
    });
  }

  // The markup for a share button (the label follows the UI language).
  const ICON = '<svg class="share-wa-icon" viewBox="0 0 24 24" width="18" height="18" aria-hidden="true" focusable="false">'
    + '<path fill="currentColor" d="M12 2a10 10 0 0 0-8.6 15.1L2 22l5-1.3A10 10 0 1 0 12 2zm0 18.2c-1.5 0-3-.4-4.3-1.2'
    + 'l-.3-.2-3 .8.8-2.9-.2-.3A8.2 8.2 0 1 1 12 20.2zm4.5-6.1c-.2-.1-1.5-.7-1.7-.8s-.4-.1-.6.1-.7.8-.8 1-.3.2-.5.1'
    + 'a6.7 6.7 0 0 1-3.3-2.9c-.3-.4.3-.4.7-1.3.1-.2 0-.3 0-.4l-.8-1.8c-.2-.5-.4-.4-.6-.4h-.5a1 1 0 0 0-.7.3 3 3 0 0 0'
    + '-.9 2.2 5.2 5.2 0 0 0 1.1 2.7 11.8 11.8 0 0 0 4.5 4c1.7.7 2.3.8 3.2.6.5-.1 1.5-.6 1.7-1.2s.2-1.1.2-1.2-.2-.2-.5-.3z"/></svg>';
  function button(id, label) {
    return `<a class="share-wa" id="${id}" href="https://wa.me/" target="_blank" rel="noopener">${ICON}`
      + `<span>${String(label).replace(/[&<>"']/g, (c) => `&#${c.charCodeAt(0)};`)}</span></a>`;
  }

  window.DAShare = {
    ready, url, waHref, cityPath, cityName, milanText, todayText, panchangText, wire, button, ICON,
  };
})();
