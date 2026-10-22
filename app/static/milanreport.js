/* DIVASTRO-156: the ₹51 Kundali Milan report card on the public matching pages
 * (app/milan_card.py). Reports milan_report_shown once the card is on screen and
 * milan_report_click when its button is tapped, with the card's detail ("page" on
 * /kundali-milan, "naam" under a naam-milan result). Nothing the visitor typed is sent.
 * daTrack comes from visit.js and is a no-op under Do-Not-Track. Sample taps are
 * reported as sample_view, like the other sample links. */
(() => {
  'use strict';
  const card = document.querySelector('[data-milan-report]');
  if (!card) return;
  const detail = card.dataset.milanReport || 'page';
  const track = (name, d) => { try { window.daTrack?.(name, d); } catch { /* never surfaces */ } };

  let seen = false;
  const shown = () => { if (!seen) { seen = true; track('milan_report_shown', detail); } };
  if ('IntersectionObserver' in window) {
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { shown(); io.disconnect(); }
    });
    io.observe(card);
  } else {
    shown();
  }

  card.addEventListener('click', (e) => {
    if (e.target.closest('[data-milan-report-go]')) track('milan_report_click', detail);
    const sample = e.target.closest('a[data-sample]');
    if (sample) track('sample_view', sample.dataset.sample);
  });
})();
