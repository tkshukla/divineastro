/* Free Vedic tools: Kundali Milan, Panchang, and Muhurat Finder.
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
    if (!q('#panchang-result').innerHTML) loadPanchang();
  });
  q('#open-muhurat')?.addEventListener('click', () => {
    showStage('stage-muhurat');
    initMuhuratDates();
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
      const currentLang = (typeof state !== 'undefined' && state.lang) ? state.lang : 'en';
      payload = { groom: readSide('groom'), bride: readSide('bride'), lang: currentLang };
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
      if (!m) return '';
      const refs = (m.references || []).filter(r => r.afflicted).map(r => r.reference);
      const isAff = m.manglik;
      return `<li><b>${esc(who)}:</b> ${
        isAff
          ? `Manglik (${esc(m.severity || 'mild')})`
          : 'Not Manglik'}${m.summary ? ` — ${esc(m.summary)}` : ''}</li>`;
    };

    const cancellations = (ak.cancellations_applied || []).map(c => typeof c === 'object' ? `${c.koota}: ${c.reason}` : c).join('; ');

    q('#milan-result').innerHTML = `
      <div class="milan-score ${tone}">
        <div class="ms-num">${ak.total}<span>/ ${ak.maximum}</span></div>
        <div class="ms-meta">
          <div class="ms-verdict">${esc(ak.verdict || '')}</div>
          <div class="ms-bar"><i style="width:${pct}%"></i></div>
          ${cancellations
            ? `<div class="ms-note">${esc(ak.total_before_cancellation)} ${tr('beforeCancellation', 'before cancellation')} — ${esc(cancellations)}</div>` : ''}
        </div>
      </div>

      <table class="koota-table"><tbody>${rows}</tbody></table>

      <div class="card milan-extra">
        <h3>${esc(tr('mangalTitle', 'Mangal Dosha Analysis'))}</h3>
        <ul style="line-height: 1.6; font-size: 13.5px; padding-left: 18px; margin: 10px 0;">
          ${manglik(ak.groom.name || 'Groom (वर)', d.mangal.groom)}
          ${manglik(ak.bride.name || 'Bride (कन्या)', d.mangal.bride)}
        </ul>
        ${d.mangal.pair?.note ? `<p style="margin-top: 10px; color: var(--gold);">${esc(d.mangal.pair.note)}</p>` : ''}
        ${d.mangal.pair?.tradition_note ? `<p class="muted-line" style="margin-top: 6px; font-size: 12px;">${esc(d.mangal.pair.tradition_note)}</p>` : ''}
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

  /* ---------------------------------------------------------------- muhurat */
  const muPick = placePicker(q('#mu-place'), q('#mu-results'), q('#mu-chosen'));
  let muPlace = null;

  function initMuhuratDates() {
    const today = new Date();
    const future = new Date();
    future.setDate(today.getDate() + 30);
    const toIso = (d) => d.toISOString().slice(0, 10);
    if (!q('#mu-from').value) q('#mu-from').value = toIso(today);
    if (!q('#mu-to').value) q('#mu-to').value = toIso(future);
  }

  q('#mu-place')?.addEventListener('place:chosen', (e) => {
    muPlace = e.detail;
  });

  q('#muhurat-go')?.addEventListener('click', async () => {
    const btn = q('#muhurat-go');
    const err = q('#muhurat-error');
    err.hidden = true;

    const event = q('#mu-event').value;
    const fromDate = q('#mu-from').value;
    const toDate = q('#mu-to').value;
    if (!fromDate || !toDate) {
      err.textContent = 'Please choose both from and to dates.';
      err.hidden = false;
      return;
    }

    const place = muPlace || muPick() ||
      { latitude: 28.6139, longitude: 77.2090, timezone: 'Asia/Kolkata', label: 'New Delhi, India' };

    const lang = (typeof state !== 'undefined' && state.lang) ? state.lang : 'en';
    const params = new URLSearchParams({
      event,
      from_date: fromDate,
      to_date: toDate,
      latitude: place.latitude,
      longitude: place.longitude,
      timezone: place.timezone || '',
      language: lang,
    });

    btn.disabled = true; btn.classList.add('busy');
    try {
      const res = await fetch(`/api/muhurat?${params}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Could not calculate muhurat.');
      renderMuhurat(data, place.label);
    } catch (ex) {
      err.textContent = ex.message; err.hidden = false;
    } finally {
      btn.disabled = false; btn.classList.remove('busy');
    }
  });

  function renderMuhurat(data, placeLabel) {
    const days = data.days || [];
    if (!days.length) {
      q('#muhurat-result').innerHTML = '<div class="card"><p>No dates found for this range.</p></div>';
      q('#muhurat-result').hidden = false;
      return;
    }

    const rows = days.map((d) => `
      <tr style="border-bottom: 1px solid rgba(255,255,255,0.04);">
        <td style="padding: 10px 8px; white-space: nowrap;">
          <b>${esc(d.date)}</b><br/>
          <span style="font-size: 11.5px; color: var(--ink-dim);">${esc(d.vara)}</span>
        </td>
        <td style="padding: 10px 8px;">
          <span class="badge ${esc(d.badge)}" style="font-size: 11px;">${esc(d.verdict)}</span>
        </td>
        <td style="padding: 10px 8px; font-size: 12.5px;">
          <b>${esc(d.tithi)}</b> · ${esc(d.nakshatra)}<br/>
          <span style="font-size: 11.5px; color: var(--ink-dim);">${esc(d.yoga)}</span>
        </td>
        <td style="padding: 10px 8px; font-size: 11.5px; color: var(--gold);">
          ${d.abhijit ? `Abhijit: ${esc(d.abhijit)}` : '—'}
        </td>
        <td style="padding: 10px 8px; font-size: 12px;">
          ${(d.reasons || []).map(r => `<span style="display:block;">• ${esc(r)}</span>`).join('') || '—'}
        </td>
      </tr>
    `).join('');

    q('#muhurat-result').innerHTML = `
      <div class="card" style="margin-top: 20px; overflow-x: auto;">
        <h3 style="margin-bottom: 12px; color: var(--gold);">
          ${esc(tr('muhuratResultsTitle', 'Auspicious Dates Summary'))} — ${esc(placeLabel)}
        </h3>
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
          <thead>
            <tr style="border-bottom: 1px solid var(--line); color: var(--ink-dim);">
              <th style="padding: 8px;">Date / Day</th>
              <th style="padding: 8px;">Verdict</th>
              <th style="padding: 8px;">Tithi &amp; Nakshatra</th>
              <th style="padding: 8px;">Abhijit</th>
              <th style="padding: 8px;">Evaluation / Reasons</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    `;
    q('#muhurat-result').hidden = false;
    q('#muhurat-result').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // --------------------------------------------------------------------------
  // Choghadiya
  // --------------------------------------------------------------------------

  let choPlace = null;
  const choPlaceInput = q('#cho-place');
  const choResults = q('#cho-results');
  const choChosen = q('#cho-chosen');

  q('#open-choghadiya')?.addEventListener('click', () => {
    show('stage-choghadiya');
    if (!q('#cho-date').value) {
      q('#cho-date').value = new Date().toISOString().slice(0, 10);
    }
  });

  if (choPlaceInput) {
    choPlaceInput.addEventListener('input', () => {
      suggest(choPlaceInput.value, choResults, (p) => {
        choPlace = p;
        choPlaceInput.value = p.label;
        choChosen.textContent = p.label;
        choChosen.hidden = false;
        choResults.hidden = true;
      });
    });
  }

  q('#choghadiya-go')?.addEventListener('click', async () => {
    const err = q('#choghadiya-error');
    err.hidden = true; err.textContent = '';
    const btn = q('#choghadiya-go');
    const targetDate = q('#cho-date').value || new Date().toISOString().slice(0, 10);
    const place = choPlace || {
      label: 'New Delhi, India',
      latitude: 28.6139,
      longitude: 77.2090,
      timezone: 'Asia/Kolkata',
    };
    const lang = (window.APP_STATE && window.APP_STATE.lang) || 'en';

    const params = new URLSearchParams({
      date: targetDate,
      latitude: place.latitude,
      longitude: place.longitude,
      timezone: place.timezone || '',
      language: lang,
    });

    btn.disabled = true; btn.classList.add('busy');
    try {
      const res = await fetch(`/api/choghadiya?${params}`);
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Could not calculate Choghadiya.');
      renderChoghadiya(data, place.label, lang);
    } catch (ex) {
      err.textContent = ex.message; err.hidden = false;
    } finally {
      btn.disabled = false; btn.classList.remove('busy');
    }
  });

  function renderChoghadiya(data, placeLabel, lang) {
    const isHi = lang === 'hi';
    const act = data.active_slot;
    const badgeColor = {
      auspicious: '#22c55e',
      neutral: '#eab308',
      inauspicious: '#ef4444',
    };

    function renderSlots(slots) {
      return slots.map(s => {
        const bg = s.is_current ? 'background: rgba(212, 175, 55, 0.15); border-left: 3px solid var(--gold);' : '';
        const dotColor = badgeColor[s.quality] || '#999';
        return `
          <tr style="border-bottom: 1px solid rgba(255,255,255,0.04); ${bg}">
            <td style="padding: 10px 8px; font-weight: bold;">
              ${esc(s.start)} – ${esc(s.end)}
              ${s.is_current ? `<span style="margin-left: 6px; font-size: 10px; color: var(--gold); border: 1px solid var(--gold); border-radius: 4px; padding: 1px 4px;">${isHi ? 'वर्तमान' : 'NOW'}</span>` : ''}
            </td>
            <td style="padding: 10px 8px;">
              <b>${esc(s.name_label)}</b><br/>
              <span style="font-size: 11px; color: var(--ink-dim);">${isHi ? 'स्वामी: ' : 'Lord: '}${esc(s.ruler_label)}</span>
            </td>
            <td style="padding: 10px 8px;">
              <span style="display: inline-flex; align-items: center; gap: 5px; font-size: 11.5px; font-weight: 600; color: ${dotColor};">
                <span style="width: 8px; height: 8px; border-radius: 50%; background: ${dotColor};"></span>
                ${esc(s.quality_label)}
              </span>
            </td>
            <td style="padding: 10px 8px; font-size: 12px; color: var(--ink-dim);">
              ${esc(s.description)}
            </td>
          </tr>
        `;
      }).join('');
    }

    q('#choghadiya-result').innerHTML = `
      <div class="card" style="margin-top: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; margin-bottom: 16px;">
          <div>
            <h3 style="color: var(--gold); margin: 0;">
              ${isHi ? 'दैनिक चौघड़िया चक्र' : 'Choghadiya Muhurta Schedule'} — ${esc(placeLabel)}
            </h3>
            <p style="margin: 4px 0 0 0; font-size: 12.5px; color: var(--ink-dim);">
              ${esc(isHi ? data.weekday_hi : data.weekday)} · ${esc(data.date)} · ${isHi ? 'सूर्योदय' : 'Sunrise'}: ${esc(data.sunrise)} · ${isHi ? 'सूर्यास्त' : 'Sunset'}: ${esc(data.sunset)}
            </p>
          </div>
          ${act ? `
            <div style="padding: 8px 14px; border-radius: 8px; background: rgba(212, 175, 55, 0.1); border: 1px solid var(--gold); text-align: right;">
              <span style="font-size: 11px; color: var(--gold); text-transform: uppercase;">${isHi ? 'वर्तमान सक्रिय मुहूर्त' : 'Active Muhurta Now'}</span>
              <div style="font-size: 16px; font-weight: bold; color: var(--ink);">
                ${esc(act.name_label)} (${esc(act.start)} – ${esc(act.end)})
              </div>
            </div>
          ` : ''}
        </div>

        <h4 style="margin: 18px 0 8px 0; color: var(--gold); font-size: 14px; border-bottom: 1px solid var(--line); padding-bottom: 4px;">
          ☀️ ${isHi ? 'दिन का चौघड़िया (सूर्योदय से सूर्यास्त)' : 'Day Choghadiya (Sunrise to Sunset)'}
        </h4>
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; margin-bottom: 16px;">
            <thead>
              <tr style="border-bottom: 1px solid var(--line); color: var(--ink-dim);">
                <th style="padding: 6px 8px;">${isHi ? 'समय' : 'Time'}</th>
                <th style="padding: 6px 8px;">${isHi ? 'चौघड़िया / स्वामी' : 'Muhurta / Lord'}</th>
                <th style="padding: 6px 8px;">${isHi ? 'प्रकृति' : 'Nature'}</th>
                <th style="padding: 6px 8px;">${isHi ? 'उपयुक्त कार्य व परामर्श' : 'Recommended Activities'}</th>
              </tr>
            </thead>
            <tbody>
              ${renderSlots(data.day_slots)}
            </tbody>
          </table>
        </div>

        <h4 style="margin: 18px 0 8px 0; color: var(--gold); font-size: 14px; border-bottom: 1px solid var(--line); padding-bottom: 4px;">
          🌙 ${isHi ? 'रात्रि का चौघड़िया (सूर्यास्त से सूर्योदय)' : 'Night Choghadiya (Sunset to Next Sunrise)'}
        </h4>
        <div style="overflow-x: auto;">
          <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
            <thead>
              <tr style="border-bottom: 1px solid var(--line); color: var(--ink-dim);">
                <th style="padding: 6px 8px;">${isHi ? 'समय' : 'Time'}</th>
                <th style="padding: 6px 8px;">${isHi ? 'चौघड़िया / स्वामी' : 'Muhurta / Lord'}</th>
                <th style="padding: 6px 8px;">${isHi ? 'प्रकृति' : 'Nature'}</th>
                <th style="padding: 6px 8px;">${isHi ? 'उपयुक्त कार्य व परामर्श' : 'Recommended Activities'}</th>
              </tr>
            </thead>
            <tbody>
              ${renderSlots(data.night_slots)}
            </tbody>
          </table>
        </div>
      </div>
    `;
    q('#choghadiya-result').hidden = false;
    q('#choghadiya-result').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
})();
