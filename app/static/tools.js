/* Free Vedic tools: Kundali Milan and Panchang.
 *
 * Deliberately self-contained. The birth form in app.js has its own place
 * autocomplete wired to specific element ids; generalising it would have meant
 * editing the one flow that already works and earns money. A small local picker
 * costs a few lines and risks nothing.
 *
 * Depends on app.js only for `showStage`, `t` and `escapeHtml`, all globals.
 */
'use strict';

(() => {
  const q = (s, r = document) => r.querySelector(s);
  const qa = (s, r = document) => Array.from(r.querySelectorAll(s));
  const esc = (s) => (typeof escapeHtml === 'function' ? escapeHtml(s)
    : String(s ?? '').replace(/[&<>"']/g, (c) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c])));
  const tr = (k, fallback) => {
    try { const v = t(k); return v && v !== k ? v : fallback; } catch { return fallback; }
  };

  /* ---------------------------------------------------------- place picker */
  /* Attaches to an input + <ul> pair and reports the chosen place through a
     callback. Returns a getter so the caller never reads the DOM itself. */
  function placePicker(input, list, chosenEl) {
    let chosen = null;
    let timer = null;

    const hide = () => { list.hidden = true; list.innerHTML = ''; };

    input.addEventListener('input', () => {
      chosen = null;
      if (chosenEl) chosenEl.hidden = true;
      clearTimeout(timer);
      const term = input.value.trim();
      if (term.length < 2) { hide(); return; }
      timer = setTimeout(async () => {
        let places = [];
        try {
          const res = await fetch(`/api/places?q=${encodeURIComponent(term)}`);
          // The endpoint returns { results: [...] } — not { places: [...] }.
          places = (await res.json()).results || [];
        } catch { hide(); return; }
        if (!places.length) { hide(); return; }
        list.innerHTML = places.map((p, i) =>
          `<li data-i="${i}">${esc(p.label)}<span>${esc(p.timezone)}</span></li>`).join('');
        list.hidden = false;
        qa('li', list).forEach((li) => {
          li.onclick = () => {
            chosen = places[Number(li.dataset.i)];
            input.value = chosen.label;
            if (chosenEl) {
              chosenEl.textContent = `${chosen.latitude.toFixed(4)}, ` +
                `${chosen.longitude.toFixed(4)} · ${chosen.timezone}`;
              chosenEl.hidden = false;
            }
            hide();
            input.dispatchEvent(new CustomEvent('place:chosen', { detail: chosen }));
          };
        });
      }, 180);
    });

    document.addEventListener('click', (e) => {
      if (e.target !== input && !list.contains(e.target)) hide();
    });

    return () => chosen;
  }

  /* ------------------------------------------------------------- navigation */
  q('#open-milan')?.addEventListener('click', () => showStage('stage-milan'));
  q('#open-panchang')?.addEventListener('click', () => {
    showStage('stage-panchang');
    // Load something immediately rather than showing an empty screen: a
    // panchang with no location is useless, so fall back to Delhi until the
    // visitor picks their own city.
    if (!q('#panchang-result').innerHTML) loadPanchang();
  });

  /* ---------------------------------------------------------- kundali milan */
  const sides = {};
  qa('.milan-card').forEach((form) => {
    const side = form.dataset.side;
    sides[side] = {
      form,
      get: placePicker(q('[data-f="place"]', form), q('[data-f="results"]', form),
                       q('[data-f="chosen"]', form)),
    };
  });

  function readSide(side) {
    const { form, get } = sides[side];
    const val = (f) => q(`[data-f="${f}"]`, form).value;
    const place = get();
    const known = !q('[data-f="unknown"]', form).checked;
    if (!val('date')) throw new Error(tr('milanNeedDate', 'Both dates of birth are needed.'));
    if (!place) throw new Error(tr('milanNeedPlace',
      'Pick both birth places from the suggestions so the coordinates are exact.'));
    return {
      name: val('name').trim(), date: val('date'),
      time: known ? (val('time') || '12:00') : '12:00',
      time_known: known,
      place: place.label, latitude: place.latitude, longitude: place.longitude,
      timezone: place.timezone,
    };
  }

  q('#milan-go')?.addEventListener('click', async () => {
    const btn = q('#milan-go');
    const err = q('#milan-error');
    err.hidden = true;
    let payload;
    try {
      payload = { groom: readSide('groom'), bride: readSide('bride') };
    } catch (ex) { err.textContent = ex.message; err.hidden = false; return; }

    btn.disabled = true; btn.classList.add('busy');
    try {
      const res = await fetch('/api/match', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Could not match those charts.');
      renderMilan(data);
    } catch (ex) {
      err.textContent = ex.message; err.hidden = false;
    } finally {
      btn.disabled = false; btn.classList.remove('busy');
    }
  });

  function renderMilan(d) {
    const ak = d.ashtakoot;
    const pct = Math.round((ak.total / ak.maximum) * 100);
    const tone = ak.total >= 25 ? 'good' : ak.total >= 18 ? 'ok' : 'poor';

    const rows = ak.kootas.map((k) => `
      <tr>
        <td class="kt-name">${esc(k.label)}</td>
        <td class="kt-score ${k.score === 0 ? 'zero' : ''}">${k.score} / ${k.max}</td>
        <td class="kt-note">${esc(k.note || '')}</td>
      </tr>`).join('');

    const manglik = (who, m) => {
      const flags = ['lagna', 'moon', 'venus']
        .filter((ref) => m[ref] && m[ref].afflicted)
        .map((ref) => ref === 'lagna' ? 'ascendant' : ref);
      return `<li><b>${esc(who)}:</b> ${
        flags.length
          ? `Manglik by the ${flags.join(', ')} reading${flags.length > 1 ? 's' : ''}`
          : 'not Manglik'}${m.severity ? ` — ${esc(m.severity)}` : ''}</li>`;
    };

    q('#milan-result').innerHTML = `
      <div class="milan-score ${tone}">
        <div class="ms-num">${ak.total}<span>/ ${ak.maximum}</span></div>
        <div class="ms-meta">
          <div class="ms-verdict">${esc(ak.verdict || '')}</div>
          <div class="ms-bar"><i style="width:${pct}%"></i></div>
          ${ak.cancellations_applied && ak.cancellations_applied.length
            ? `<div class="ms-note">${esc(ak.total_before_cancellation)} before
                 cancellation — ${esc(ak.cancellations_applied.join('; '))}</div>` : ''}
        </div>
      </div>

      <table class="koota-table"><tbody>${rows}</tbody></table>

      <div class="card milan-extra">
        <h3>${esc(tr('mangalTitle', 'Mangal Dosha'))}</h3>
        <ul>${manglik(ak.groom.name || 'Groom', d.mangal.groom)}
            ${manglik(ak.bride.name || 'Bride', d.mangal.bride)}</ul>
        ${d.mangal.compatible === false
          ? `<p class="warn-line">${esc(d.mangal.note || '')}</p>`
          : d.mangal.note ? `<p class="muted-line">${esc(d.mangal.note)}</p>` : ''}
      </div>

      ${d.caveat ? `<p class="warn-line">${esc(d.caveat)}</p>` : ''}
      <p class="muted-line">${esc(ak.band_note || '')} ${esc(ak.convention_note || '')}</p>`;
    q('#milan-result').hidden = false;
    q('#milan-result').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /* ---------------------------------------------------------------- panchang */
  const paPick = placePicker(q('#pa-place'), q('#pa-results'), q('#pa-chosen'));
  let paPlace = null;

  q('#pa-place')?.addEventListener('place:chosen', (e) => {
    paPlace = e.detail;
    loadPanchang();
  });
  q('#pa-date')?.addEventListener('change', () => loadPanchang());

  async function loadPanchang() {
    const err = q('#panchang-error');
    err.hidden = true;
    // New Delhi until the visitor says otherwise — an empty panchang screen
    // would be worse than a defaulted one.
    const place = paPlace || paPick() ||
      { latitude: 28.6139, longitude: 77.2090, timezone: 'Asia/Kolkata', label: 'New Delhi, India' };
    const params = new URLSearchParams({
      latitude: place.latitude, longitude: place.longitude, timezone: place.timezone || '',
    });
    const date = q('#pa-date').value;
    if (date) params.set('date', date);

    try {
      const res = await fetch(`/api/panchang?${params}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Could not compute the panchang.');
      renderPanchang(data, place.label);
    } catch (ex) {
      err.textContent = ex.message; err.hidden = false;
    }
  }

  const hhmm = (iso) => (iso ? String(iso).slice(11, 16) : '—');
  const span = (w) => (w ? `${hhmm(w.start)} – ${hhmm(w.end)}` : '—');

  function renderPanchang(p, label) {
    // tithi/nakshatra/yoga/karana are lists: a vedic day can carry two of each.
    const limb = (rows, key) => (rows || []).map((r) =>
      `<div class="limb-line"><b>${esc(r.label || r.name)}</b> ` +
      `<span>${esc(tr('until', 'until'))} ${hhmm(r.ends)}</span></div>`).join('') || '—';

    q('#panchang-result').innerHTML = `
      <div class="card pa-card">
        <div class="pa-head">
          <div>
            <h2>${esc(p.summary.vara)} · ${esc(p.date)}</h2>
            <p class="muted-line">${esc(label || '')} ${
              p.reckoned_from === 'sunrise' ? '' : `(${esc(p.reckoned_from)})`}</p>
          </div>
          <div class="pa-sun">
            <div>☀ ${hhmm(p.sun.rise)} – ${hhmm(p.sun.set)}</div>
            <div>☾ ${hhmm(p.moon.rise)} – ${hhmm(p.moon.set)}</div>
          </div>
        </div>

        <div class="pa-limbs">
          <div><h4>${esc(tr('tithiL', 'Tithi'))}</h4>${limb(p.tithi)}</div>
          <div><h4>${esc(tr('nakL', 'Nakshatra'))}</h4>${limb(p.nakshatra)}</div>
          <div><h4>${esc(tr('yogaL', 'Yoga'))}</h4>${limb(p.yoga)}</div>
          <div><h4>${esc(tr('karanaL', 'Karana'))}</h4>${limb(p.karana)}</div>
        </div>
      </div>

      <div class="card pa-card">
        <h3>${esc(tr('timingsL', 'Timings'))}</h3>
        <div class="pa-times">
          <div class="bad"><span>Rahu Kaal</span><b>${span(p.muhurta.rahu_kaal)}</b></div>
          <div class="bad"><span>Yamaganda</span><b>${span(p.muhurta.yamaganda)}</b></div>
          <div class="bad"><span>Gulika Kaal</span><b>${span(p.muhurta.gulika_kaal)}</b></div>
          <div class="good"><span>Abhijit Muhurta</span><b>${
            p.muhurta.abhijit ? span(p.muhurta.abhijit) : esc(tr('none', 'none today'))}</b></div>
        </div>
      </div>

      ${(p.notes || []).length
        ? `<p class="muted-line">${esc(p.notes.join(' '))}</p>` : ''}`;
    q('#panchang-result').hidden = false;
  }
})();
