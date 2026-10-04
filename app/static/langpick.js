/* The language picker (DIVASTRO-121), shared by the app header and every
 * server-rendered page.
 *
 * The picker itself is plain HTML that works without this file:
 *   <details class="lang-picker"><summary class="lp-btn">🌐 ಕನ್ನಡ ▾</summary>
 *     <div class="lp-menu"><ul><li><a data-lang="kn" href="/kn/panchang">…</a></li>…</ul></div>
 *   </details>
 * (app/i18n.py `picker()` writes it for server pages; index.html has the app's.)
 *
 * This adds what HTML alone cannot:
 *  - Escape closes the menu and returns focus to the button; a click/tap
 *    outside closes it; arrow keys move between the languages.
 *  - The choice is remembered (localStorage "astro.lang", the app's own key), so
 *    the app opens in the language the reader picked on a Panchang page.
 *  - In the app, choosing does not navigate: app.js sets window.daSetLang and
 *    the page re-renders in place.
 *  - A one-time first-visit hint: when the browser's languages include one of
 *    ours and the reader has never chosen, a small banner in THAT language's
 *    script offers to switch ("ಈ ಸೈಟ್ ಅನ್ನು ಕನ್ನಡದಲ್ಲಿ ನೋಡಬೇಕೆ?"). Dismissing it
 *    is remembered ("astro.langHint").
 */
(() => {
  'use strict';
  const LANG_KEY = 'astro.lang';
  const HINT_KEY = 'astro.langHint';
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch { /* private mode */ } },
  };

  function close(det, focus) {
    if (!det.open) return;
    det.open = false;
    if (focus) det.querySelector('summary')?.focus();
  }

  function choose(code, href, ev) {
    store.set(LANG_KEY, code);
    store.set(HINT_KEY, '1');
    if (typeof window.daTrack === 'function') window.daTrack('lang', code);
    if (typeof window.daSetLang === 'function') {
      if (ev) ev.preventDefault();
      window.daSetLang(code);
      return true;
    }
    if (!ev && href) location.href = href;
    return false;
  }

  function wire(det) {
    if (det.dataset.wired) return;
    det.dataset.wired = '1';
    const links = () => Array.from(det.querySelectorAll('.lp-menu a[data-lang]'));
    det.addEventListener('toggle', () => {
      if (det.open) (det.querySelector('a[aria-current]') || links()[0])?.focus();
    });
    det.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') { close(det, true); e.preventDefault(); return; }
      if (!det.open || !['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(e.key)) return;
      const all = links();
      let i = all.indexOf(document.activeElement);
      if (e.key === 'ArrowDown') i = (i + 1) % all.length;
      else if (e.key === 'ArrowUp') i = (i - 1 + all.length) % all.length;
      else if (e.key === 'Home') i = 0;
      else i = all.length - 1;
      all[i].focus();
      e.preventDefault();
    });
    det.addEventListener('click', (e) => {
      const a = e.target.closest('a[data-lang]');
      if (!a) return;
      choose(a.dataset.lang, a.href, e);
      close(det, false);
    });
  }

  document.addEventListener('click', (e) => {
    document.querySelectorAll('details.lang-picker[open]').forEach((det) => {
      if (!det.contains(e.target)) close(det, false);
    });
  });

  function wireAll() { document.querySelectorAll('details.lang-picker').forEach(wire); }

  /* ---------------------------------------------------------- first-visit hint */
  function browserMatch(current, offered) {
    const prefs = (navigator.languages && navigator.languages.length)
      ? navigator.languages : [navigator.language || ''];
    for (const tag of prefs) {
      const code = String(tag || '').toLowerCase().split('-')[0];
      if (!code) continue;
      if (code === 'en') return null;          // an English browser needs no offer
      if (code === current) return null;       // already reading in it
      if (offered[code]) return offered[code];
    }
    return null;
  }

  function showHint() {
    // HINT_KEY, not LANG_KEY: the app writes astro.lang on every load (its
    // current language, "en" by default), so that key cannot tell "never chose"
    // apart from "chose English". Any choice through the picker or the hint
    // sets HINT_KEY, as does dismissing the hint.
    if (store.get(HINT_KEY)) return;
    if (new URLSearchParams(location.search).get('lang')) return;
    const det = document.querySelector('details.lang-picker');
    if (!det) return;
    const offered = {};
    det.querySelectorAll('.lp-menu a[data-lang]').forEach((a) => { offered[a.dataset.lang] = a; });
    const current = (typeof window.daGetLang === 'function' && window.daGetLang())
      || det.dataset.current || 'en';
    const a = browserMatch(current, offered);
    if (!a || !a.dataset.hint) return;
    const box = document.createElement('div');
    box.className = 'lp-hint';
    box.setAttribute('role', 'dialog');
    box.setAttribute('aria-live', 'polite');
    box.setAttribute('lang', a.getAttribute('lang') || a.dataset.lang);
    box.setAttribute('aria-label', a.dataset.hint);
    const p = document.createElement('p');
    p.textContent = a.dataset.hint;
    const yes = document.createElement('a');
    yes.href = a.href;
    yes.className = 'lp-hint-yes';
    yes.textContent = a.dataset.yes || a.textContent;
    const no = document.createElement('button');
    no.type = 'button';
    no.className = 'lp-hint-no';
    no.textContent = a.dataset.notnow || '×';
    const done = () => { store.set(HINT_KEY, '1'); box.remove(); };
    yes.addEventListener('click', (e) => { done(); choose(a.dataset.lang, a.href, e); });
    no.addEventListener('click', done);
    box.addEventListener('keydown', (e) => { if (e.key === 'Escape') done(); });
    box.append(p, yes, no);
    document.body.appendChild(box);
  }

  function init() { wireAll(); showHint(); }
  window.daLangPicker = { wireAll };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init);
  else init();
})();
