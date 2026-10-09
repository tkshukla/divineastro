/* /pricing: report the page view and taps on "Start free" (DIVASTRO-149).
 *
 * Both go through window.daTrack from visit.js, which is a no-op when Do Not
 * Track / Global Privacy Control is on. A fixed vocabulary of names and labels;
 * nothing the visitor typed. Without JS the page is plain content and links.
 */
'use strict';

(() => {
  const track = (name, detail) => {
    if (typeof window.daTrack === 'function') window.daTrack(name, detail);
  };
  track('pricing_view', 'page');
  document.addEventListener('click', (e) => {
    const el = e.target.closest('[data-plans]');
    if (el) track('plans_click', el.dataset.plans);
    const sample = e.target.closest('a[data-sample]');      // DIVASTRO-151
    if (sample) track('sample_view', sample.dataset.sample);
  });
})();
