/* Divine Astro service worker (DIVASTRO-112): the daily vrat / Rahu Kaal push.
 *
 * Served at /sw.js (scope /) by app/push.py. Deliberately tiny: it shows the
 * notification the server sent and opens its link when tapped. No offline
 * caching and no fetch handler, so it never sits between the page and the
 * network.
 */
'use strict';

self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (event) => event.waitUntil(self.clients.claim()));

self.addEventListener('push', (event) => {
  let data = {};
  try { data = event.data ? event.data.json() : {}; } catch (_) {
    data = { body: event.data ? event.data.text() : '' };
  }
  event.waitUntil(self.registration.showNotification(data.title || 'Divine Astro', {
    body: data.body || '',
    icon: data.icon || '/static/icon-512.png',
    badge: data.badge || '/static/icon-512.png',
    tag: data.tag || 'daily',
    lang: data.lang || 'en',
    data: { url: data.url || '/' },
  }));
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  // Only ever open a page on this site, whatever the payload says.
  let target = self.location.origin + '/';
  try {
    const u = new URL((event.notification.data && event.notification.data.url) || '/', self.location.origin);
    if (u.origin === self.location.origin) target = u.href;
  } catch (_) { /* the home page */ }
  event.waitUntil((async () => {
    const wins = await self.clients.matchAll({ type: 'window', includeUncontrolled: true });
    const open = wins.find((w) => w.url === target && 'focus' in w);
    return open ? open.focus() : self.clients.openWindow(target);
  })());
});
