/* "Stay in touch" strip on the server-rendered content pages (DIVASTRO-135).
 *
 * - Counts taps on its three actions (strip_push / strip_channel / strip_share)
 *   through window.daTrack from visit.js (a no-op when Do Not Track is on).
 * - Loads push.js lazily, and only when this browser can do web push; push.js
 *   then reveals #strip-push (unless already subscribed or push is off on the
 *   server) and runs the same subscribe flow as the home screen.
 * Without JS the strip is just the channel and share links.
 */
'use strict';

(() => {
  const strip = document.getElementById('stay-strip');
  if (!strip) return;

  strip.addEventListener('click', (e) => {
    const el = e.target.closest('[data-strip]');
    if (el && typeof window.daTrack === 'function') window.daTrack(el.dataset.strip);
  });

  const btn = document.getElementById('strip-push');
  if (!btn) return;
  if (!('serviceWorker' in navigator) || !('PushManager' in window) || !('Notification' in window)) return;
  if (Notification.permission === 'denied') return;

  let loaded = false;
  const load = () => {
    if (loaded) return;
    loaded = true;
    if (document.querySelector('script[src^="/static/push.js"]')) return;   // /vrat-tyohar already has it
    const s = document.createElement('script');
    s.src = '/static/push.js';
    s.async = true;
    document.head.appendChild(s);
  };
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      if (entries.some((x) => x.isIntersecting)) { io.disconnect(); load(); }
    }, { rootMargin: '300px' });
    io.observe(strip);
  } else {
    load();
  }
})();
