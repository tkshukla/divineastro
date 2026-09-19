/* Feedback page. Everything it sends is checked again by the server; this file
 * is about making the form pleasant, not about security. */
'use strict';

const $ = (s, r = document) => r.querySelector(s);
const esc = (s) => String(s ?? '').replace(/[&<>"']/g,
  (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const store = {
  get(k) { try { return localStorage.getItem(k); } catch { return null; } },
  set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
};

const SUPPORT = 'support@divineastro.org';

const T = {
  en: {
    title: 'Send us your feedback',
    lead: 'Something not working, an answer that missed the mark, or an idea you would like to see? ' +
      'Tell us plainly — every message is read by a person.',
    lCategory: 'About', lRating: 'How is your experience so far?', optional: 'optional',
    lMessage: 'Your message',
    ph: 'What happened, or what would you like? The more specific, the better.',
    allow: 'It is fine to email me at my account address about this.',
    submit: 'Send feedback', sending: 'Sending…',
    tooShort: 'Please write a little more (at least 10 characters).',
    thanksTitle: 'Thank you', thanksText: 'Your message has been received. We read every one.',
    home: 'Back to Divine Astro', again: 'Send another message',
    gate: 'Please sign in so we know who the feedback is from — it also stops spam.',
    signInWith: 'Continue with', back: '← Divine Astro',
    mineTitle: 'Your earlier feedback', clear: 'clear',
    star: (n) => `${n} star${n > 1 ? 's' : ''}`,
    help: `Cannot sign in, or need a reply urgently? Write to <a href="mailto:${SUPPORT}">${SUPPORT}</a>.`,
    cat: { general: 'General', bug: 'Something is not working', answers: 'An answer or reading',
      payments: 'Payments or an order', idea: 'An idea or request', other: 'Something else' },
    status: { new: 'Received', read: 'Seen', resolved: 'Resolved' },
    lang: 'हिन्दी', failed: 'Could not send. Please try again.',
  },
  hi: {
    title: 'हमें अपनी प्रतिक्रिया भेजें',
    lead: 'कुछ ठीक से काम नहीं कर रहा, कोई उत्तर सही नहीं लगा, या कोई सुझाव है? ' +
      'सीधे लिखें — हर संदेश कोई व्यक्ति स्वयं पढ़ता है।',
    lCategory: 'विषय', lRating: 'अब तक आपका अनुभव कैसा रहा?', optional: 'वैकल्पिक',
    lMessage: 'आपका संदेश',
    ph: 'क्या हुआ, या आप क्या चाहते हैं? जितना स्पष्ट लिखेंगे, उतना अच्छा।',
    allow: 'इस बारे में मेरे खाते के ईमेल पर लिखना ठीक है।',
    submit: 'प्रतिक्रिया भेजें', sending: 'भेजा जा रहा है…',
    tooShort: 'कृपया थोड़ा और लिखें (कम से कम 10 अक्षर)।',
    thanksTitle: 'धन्यवाद', thanksText: 'आपका संदेश हमें मिल गया है। हम हर संदेश पढ़ते हैं।',
    home: 'Divine Astro पर वापस जाएँ', again: 'एक और संदेश भेजें',
    gate: 'कृपया साइन इन करें ताकि हमें पता रहे कि प्रतिक्रिया किसकी है — इससे स्पैम भी रुकता है।',
    signInWith: 'जारी रखें:', back: '← Divine Astro',
    mineTitle: 'आपकी पिछली प्रतिक्रियाएँ', clear: 'हटाएँ',
    star: (n) => `${n} सितारा`,
    help: `साइन इन नहीं हो पा रहा, या तुरंत उत्तर चाहिए? <a href="mailto:${SUPPORT}">${SUPPORT}</a> पर लिखें।`,
    cat: { general: 'सामान्य', bug: 'कुछ ठीक से काम नहीं कर रहा', answers: 'कोई उत्तर या रीडिंग',
      payments: 'भुगतान या ऑर्डर', idea: 'सुझाव या अनुरोध', other: 'कुछ और' },
    status: { new: 'प्राप्त हुआ', read: 'देखा गया', resolved: 'हल हुआ' },
    lang: 'English', failed: 'भेजा नहीं जा सका। कृपया फिर कोशिश करें।',
  },
};

let lang = store.get('astro.lang') === 'hi' ? 'hi' : 'en';
let rating = null;
const t = () => T[lang];

/* ---------------------------------------------------------------- theme --- */
(function initTheme() {
  const saved = store.get('astro.theme');
  const light = saved ? saved === 'light'
    : (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches);
  if (light) document.documentElement.setAttribute('data-theme', 'light');
})();

async function api(path, opts = {}) {
  const res = await fetch(path, {
    credentials: 'same-origin',
    headers: opts.body ? { 'Content-Type': 'application/json' } : {},
    ...opts,
  });
  let body = null;
  try { body = await res.json(); } catch { /* empty */ }
  if (!res.ok) {
    const err = new Error((body && body.detail) || `HTTP ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return body;
}

/* ---------------------------------------------------------------- render --- */
function paintStars() {
  const box = $('#stars');
  box.innerHTML = [1, 2, 3, 4, 5].map((n) => `
    <label><input type="radio" name="rating" value="${n}" aria-label="${esc(t().star(n))}"
      ${rating === n ? 'checked' : ''}><span class="star${rating && n <= rating ? ' on' : ''}"
      aria-hidden="true">&#9733;</span></label>`).join('') +
    `<button type="button" class="clear" id="clear-rating" ${rating ? '' : 'hidden'}>${esc(t().clear)}</button>`;
  box.querySelectorAll('input').forEach((i) => {
    i.onchange = () => { rating = Number(i.value); paintStars(); };
  });
  $('#clear-rating').onclick = () => { rating = null; paintStars(); };
}

function applyLang() {
  const s = t();
  document.documentElement.lang = lang;
  $('#back').textContent = s.back;
  $('#title').textContent = s.title;
  $('#lead').textContent = s.lead;
  $('#l-category').textContent = s.lCategory;
  $('#l-rating').textContent = s.lRating;
  $('#l-optional').textContent = s.optional;
  $('#l-message').textContent = s.lMessage;
  $('#message').placeholder = s.ph;
  $('#l-allow').textContent = s.allow;
  $('#l-submit').textContent = s.submit;
  $('#lang-toggle').textContent = s.lang;
  $('#t-title').textContent = s.thanksTitle;
  $('#t-text').textContent = s.thanksText;
  $('#t-home').textContent = s.home;
  $('#again').textContent = s.again;
  $('#mine-title').textContent = s.mineTitle;
  $('#help').innerHTML = s.help;
  $('#gate-msg').textContent = s.gate;
  const sel = $('#category');
  const cur = sel.value || 'general';
  sel.innerHTML = Object.entries(s.cat)
    .map(([k, v]) => `<option value="${k}">${esc(v)}</option>`).join('');
  sel.value = cur;
  paintStars();
  if (signedIn) loadMine();
  loadGateButtons();
}

let signedIn = false;
let providers = null;

async function loadGateButtons() {
  const box = $('#gate-actions');
  try {
    if (!providers) providers = (await api('/api/auth/providers')).providers || [];
    box.innerHTML = providers.map((p) =>
      `<a class="primary" href="/api/auth/${esc(p.key)}/start?next=/feedback">` +
      `${esc(t().signInWith)} ${esc(p.label)}</a>`).join('');
  } catch { box.innerHTML = ''; }
}

async function loadMine() {
  try {
    const { feedback } = await api('/api/feedback/mine');
    $('#mine-wrap').hidden = !feedback.length;
    $('#mine').innerHTML = feedback.map((f) => `
      <li><div class="meta"><span>${esc(t().cat[f.category] || f.category)}</span>
        ${f.rating ? `<span>${'★'.repeat(f.rating)}</span>` : ''}
        <span>${esc(f.at)}</span>
        <span class="pill ${esc(f.status)}">${esc(t().status[f.status] || f.status)}</span></div>
        ${esc(f.message)}${f.message.length >= 160 ? '…' : ''}</li>`).join('');
  } catch { $('#mine-wrap').hidden = true; }
}

function show(which) {
  $('#gate').hidden = which !== 'gate';
  $('#form-card').hidden = which !== 'form';
  $('#thanks').hidden = which !== 'thanks';
}

function fromPage() {
  const q = new URLSearchParams(location.search).get('from');
  if (q) return q.slice(0, 120);
  try {
    const r = new URL(document.referrer);
    return r.origin === location.origin ? (r.pathname + r.search).slice(0, 120) : '';
  } catch { return ''; }
}

/* ------------------------------------------------------------------ boot --- */
async function boot() {
  let me = null;
  try { me = await api('/api/me'); } catch { /* signed out */ }
  signedIn = Boolean(me && me.user);
  applyLang();
  show(signedIn ? 'form' : 'gate');
  if (signedIn) loadMine();

  $('#lang-toggle').onclick = () => {
    lang = lang === 'hi' ? 'en' : 'hi';
    store.set('astro.lang', lang);
    applyLang();
  };

  const message = $('#message'), count = $('#count');
  message.oninput = () => {
    const n = message.value.trim().length;
    count.textContent = `${message.value.length} / 2000`;
    count.classList.toggle('bad', n > 0 && n < 10);
  };

  $('#again').onclick = () => {
    message.value = ''; message.oninput();
    rating = null; paintStars();
    show('form'); message.focus();
  };

  $('#form').onsubmit = async (ev) => {
    ev.preventDefault();
    const err = $('#error'), btn = $('#submit');
    err.hidden = true;
    const text = message.value.trim();
    if (text.length < 10) { err.textContent = t().tooShort; err.hidden = false; message.focus(); return; }

    btn.disabled = true;
    $('#l-submit').textContent = t().sending;
    try {
      await api('/api/feedback', {
        method: 'POST',
        body: JSON.stringify({
          category: $('#category').value, rating, message: text,
          page: fromPage(), allow_contact: $('#allow').checked,
        }),
      });
      show('thanks');
      loadMine();
    } catch (e) {
      if (e.status === 401) { signedIn = false; show('gate'); return; }
      err.textContent = e.message || t().failed;
      err.hidden = false;
    } finally {
      btn.disabled = false;
      $('#l-submit').textContent = t().submit;
    }
  };
}

boot();
