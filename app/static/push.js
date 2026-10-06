/* Opt-in daily web push: "today's vrat, else today's Rahu Kaal" (DIVASTRO-112).
 *
 * Fills <div id="push-optin"> on the home page (under the Today strip) and on
 * the server-rendered /vrat-tyohar pages. Self-contained — the SEO pages have
 * no app.js — so its EN/HI strings live here and the language is read from
 * <html lang>, which app.js keeps in step with the language switch.
 *
 * Never prompts by itself: the permission prompt appears only after a tap. The
 * button stays hidden when the browser cannot do push, when notifications are
 * blocked, or when the server has push switched off (/api/push/key is a 404).
 * The city is the Today strip's (localStorage 'astro.todayCity'), else Delhi.
 */
'use strict';

(() => {
  const root = document.getElementById('push-optin');
  // DIVASTRO-135: the "stay in touch" strip on the content pages has its own button
  // (#strip-push, loaded lazily by strip.js). Where the page also has #push-optin
  // (home, /vrat-tyohar) that one is the offer and the strip's button stays hidden.
  const stripBtn = root ? null : document.getElementById('strip-push');
  if (!root && !stripBtn) return;
  if (!('serviceWorker' in navigator) || !('PushManager' in window) || !('Notification' in window)) return;
  if (Notification.permission === 'denied') return;

  const TODAY_KEY = 'astro.todayCity';
  const DELHI = { latitude: 28.6139, longitude: 77.2090, timezone: 'Asia/Kolkata', label: 'New Delhi, India' };
  const S = {
    en: {
      btn: '🔔 Daily vrat & Rahu Kaal alerts',
      hint: 'One notification every morning around 6 AM. No sign-in needed.',
      on: '🔔 Daily alerts on · {city}',
      off: 'Unsubscribe',
      busy: 'Turning on…',
      err: 'Could not turn on alerts. Please try again.',
      denied: 'Notifications are blocked for this site in your browser settings.',
    },
    hi: {
      btn: '🔔 रोज़ व्रत और राहु काल की सूचना',
      hint: 'हर सुबह लगभग 6 बजे एक सूचना। साइन-इन ज़रूरी नहीं।',
      on: '🔔 रोज़ की सूचना चालू है · {city}',
      off: 'बंद करें',
      busy: 'चालू हो रही है…',
      err: 'सूचना चालू नहीं हो सकी। कृपया फिर से कोशिश करें।',
      denied: 'आपके ब्राउज़र में इस साइट की सूचनाएं बंद हैं।',
    },
  };

  let key = null;
  let sub = null;           // the current PushSubscription, or null
  let busy = false;
  let note = '';            // a one-off message (error / denied)

  // The page's language: the app's state.lang, else (a server page) <html lang>.
  const lang = () => {
    if (typeof state !== 'undefined' && state.lang) return state.lang;
    return String(document.documentElement.lang || 'en').toLowerCase().split('-')[0];
  };
  // DIVASTRO-121: in the app these come from i18n/<code>.json ("push.<key>", English
  // fallback per key). Server pages (/vrat-tyohar) load push.js without app.js, so
  // the English and Hindi copies above stay as their source; other languages get
  // English there until the server pages carry the app's tables.
  const tr = (k) => {
    if (typeof t === 'function') {
      const v = t(`push.${k}`);
      if (v && v !== `push.${k}`) return v;
    }
    return (S[lang()] || S.en)[k];
  };
  const place = () => {
    try {
      const p = JSON.parse(localStorage.getItem(TODAY_KEY) || 'null');
      if (p && Number.isFinite(p.latitude) && Number.isFinite(p.longitude) && typeof p.label === 'string') return p;
    } catch { /* private mode or bad JSON */ }
    return DELHI;
  };
  const cityName = () => String(place().label || '').split(',')[0];

  function b64ToBytes(b64) {
    const pad = '='.repeat((4 - (b64.length % 4)) % 4);
    const raw = atob((b64 + pad).replace(/-/g, '+').replace(/_/g, '/'));
    return Uint8Array.from(raw, (c) => c.charCodeAt(0));
  }

  async function post(url, body) {
    const res = await fetch(url, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      credentials: 'same-origin', body: JSON.stringify(body),
    });
    if (!res.ok) throw new Error(String(res.status));
    return res.json();
  }

  function payload(s) {
    const p = place();
    return {
      subscription: s.toJSON(),
      lat: p.latitude, lon: p.longitude, tz: p.timezone || 'Asia/Kolkata',
      label: p.label || '', lang: lang(),
    };
  }

  // The strip's button: shown while not subscribed, replaced by a short thanks once on.
  function renderStrip() {
    if (!stripBtn) return;
    const li = stripBtn.parentElement;
    let done = li.querySelector('.stay-done');
    if (sub) {
      stripBtn.hidden = true;
      if (done) done.hidden = false;
      else if (stripBtn.dataset.justOn) {
        done = document.createElement('span');
        done.className = 'stay-done';
        done.setAttribute('role', 'status');
        done.textContent = stripBtn.dataset.on || '';
        li.append(done);
      }
      return;
    }
    if (done) done.hidden = true;
    stripBtn.disabled = busy;
    stripBtn.textContent = busy ? (stripBtn.dataset.busy || '…') : stripBtn.dataset.label;
    let n = li.querySelector('.stay-note');
    if (note) {
      if (!n) { n = document.createElement('small'); n.className = 'stay-note'; n.setAttribute('role', 'status'); li.append(n); }
      n.textContent = note;
    } else if (n) n.remove();
    stripBtn.hidden = false;
  }

  function render() {
    if (!root) { renderStrip(); return; }
    root.textContent = '';
    if (sub) {
      const span = document.createElement('span');
      span.className = 'push-on';
      span.textContent = tr('on').replace('{city}', cityName());
      const off = document.createElement('a');
      off.href = '#';
      off.className = 'push-off';
      off.id = 'push-unsubscribe';
      off.textContent = tr('off');
      off.addEventListener('click', (e) => { e.preventDefault(); unsubscribe(); });
      root.append(span, ' · ', off);
    } else {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'push-btn';
      btn.id = 'push-subscribe';
      btn.disabled = busy;
      btn.textContent = busy ? tr('busy') : tr('btn');
      btn.addEventListener('click', subscribe);
      const hint = document.createElement('small');
      hint.className = 'push-hint';
      hint.textContent = tr('hint');
      root.append(btn, hint);
    }
    if (note) {
      const n = document.createElement('small');
      n.className = 'push-note';
      n.setAttribute('role', 'status');
      n.textContent = note;
      root.append(n);
    }
    root.hidden = false;
  }

  async function subscribe() {
    if (busy) return;
    busy = true; note = ''; render();
    try {
      const perm = await Notification.requestPermission();
      if (perm !== 'granted') {
        note = perm === 'denied' ? ((stripBtn && stripBtn.dataset.denied) || tr('denied')) : '';
        return;
      }
      const reg = await navigator.serviceWorker.register('/sw.js', { scope: '/' });
      await navigator.serviceWorker.ready;
      const s = (await reg.pushManager.getSubscription())
        || await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: b64ToBytes(key) });
      await post('/api/push/subscribe', payload(s));
      sub = s;
      if (stripBtn) stripBtn.dataset.justOn = '1';
    } catch {
      note = (stripBtn && stripBtn.dataset.err) || tr('err');
    } finally {
      busy = false;
      render();
    }
  }

  async function unsubscribe() {
    const s = sub;
    sub = null; note = ''; render();
    if (!s) return;
    try { await post('/api/push/unsubscribe', { endpoint: s.endpoint }); } catch { /* server forgets it on the next 410 */ }
    try { await s.unsubscribe(); } catch { /* already gone */ }
  }

  // Keep the server's copy in step when the reader switches language or city
  // while subscribed (the notification follows what they last chose).
  let resync = null;
  function sync() {
    clearTimeout(resync);
    resync = setTimeout(() => { if (sub) post('/api/push/subscribe', payload(sub)).catch(() => {}); }, 400);
  }

  async function init() {
    try {
      const res = await fetch('/api/push/key');
      if (!res.ok) return;                        // push is switched off on the server
      key = (await res.json()).key;
      if (!key) return;
      const reg = await navigator.serviceWorker.getRegistration('/');
      sub = reg ? await reg.pushManager.getSubscription() : null;
    } catch { return; }
    if (stripBtn) {
      stripBtn.dataset.label = stripBtn.textContent;
      stripBtn.addEventListener('click', subscribe);
    }
    render();
    new MutationObserver(() => { render(); sync(); })
      .observe(document.documentElement, { attributes: true, attributeFilter: ['lang'] });
    window.addEventListener('today:city', () => { render(); sync(); });
  }

  init();
})();
