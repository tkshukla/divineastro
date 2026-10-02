/* Counts one page load for the admin Traffic panel (see app/analytics.py).
 *
 * Visits used to be counted when the server sent the HTML, which also counted
 * every headless scanner that fetched the page; those never run scripts, so
 * counting from here leaves them out. Loaded by every public page, once.
 *
 * The page's own referrer and query string are sent because the server cannot
 * see them: this request's Referer is our own site. Nothing else is sent, and
 * the server stores no IP address or browser string. */
(() => {
  'use strict';
  // Honour Do-Not-Track / Global Privacy Control here too, so nothing is even sent.
  // (The server checks the same headers, for browsers that set only those.)
  if (navigator.doNotTrack === '1' || window.doNotTrack === '1' || navigator.globalPrivacyControl) return;

  // Read now, before account.js strips ?welcome from the address bar.
  const body = JSON.stringify({
    path: location.pathname,
    ref: document.referrer || '',
    q: location.search || '',
  });

  const send = () => {
    try {
      // A plain string goes as text/plain, a "simple" request that needs no preflight.
      if (navigator.sendBeacon && navigator.sendBeacon('/api/visit', body)) return;
    } catch { /* fall through to fetch */ }
    fetch('/api/visit', {
      method: 'POST', body, keepalive: true, credentials: 'same-origin',
      headers: { 'Content-Type': 'text/plain;charset=UTF-8' },
    }).catch(() => { /* analytics must never surface an error */ });
  };

  // A prerendered page runs scripts before anyone sees it, and maybe never is.
  // Count it only once it is actually shown.
  if (document.prerendering) {
    document.addEventListener('prerenderingchange', send, { once: true });
  } else {
    send();
  }
})();
