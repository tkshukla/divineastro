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
  const isHi = () => typeof state !== 'undefined' && state.lang === 'hi';
  const curLang = () => (typeof state !== 'undefined' && state.lang) ? state.lang : 'en';

  // A place as a Hindi reader names it: an SEO city's Hindi name ("नई दिल्ली") when
  // we have one (share.js holds that list), else the label exactly as picked.
  function placeLabel(place) {
    const label = (place && place.label) || '';
    const S = window.DAShare;
    const c = isHi() && S && S.cityFor ? S.cityFor(place) : null;
    return c && c.name_hi ? c.name_hi : label;
  }
  // 'YYYY-MM-DD' as '3 अक्टूबर 2026' in Hindi; unchanged in English.
  function showDate(iso) {
    if (!isHi() || !/^\d{4}-\d{2}-\d{2}$/.test(String(iso || ''))) return iso || '';
    try {
      return new Intl.DateTimeFormat('hi-IN', { day: 'numeric', month: 'long', year: 'numeric',
        timeZone: 'UTC', numberingSystem: 'latn' }).format(new Date(`${iso}T00:00:00Z`));
    } catch { return iso; }
  }
  // The server's own error detail is English; a Hindi reader gets the tool's
  // Hindi message instead.
  const failText = (detail, key, fallback) => (isHi() ? tr(key, fallback) : (detail || fallback));

  // DIVASTRO-103: "today" is the calendar date at the chosen place (India by
  // default), not the UTC date — toISOString() showed yesterday 00:00-05:30 IST.
  // A function declaration (hoisted), so every tool below can use it.
  function todayIn(tz) {
    try {
      return new Intl.DateTimeFormat('en-CA', { timeZone: tz || 'Asia/Kolkata' }).format(new Date());
    } catch (_) {
      return new Intl.DateTimeFormat('en-CA', { timeZone: 'Asia/Kolkata' }).format(new Date());
    }
  }
  // 'YYYY-MM-DD' plus n days, in pure calendar arithmetic (no timezone involved).
  function addDaysIso(iso, n) {
    const d = new Date(`${iso}T00:00:00Z`);
    d.setUTCDate(d.getUTCDate() + n);
    return d.toISOString().slice(0, 10);
  }

  // Read a response as JSON WITHOUT surfacing the browser's own parse error. When the
  // server fails with a plain-text "Internal Server Error", `await res.json()` used to
  // throw `Unexpected token 'I', "Internal S"... is not valid JSON` straight into the
  // page. A failed request now yields a readable message instead; a *successful*
  // response that isn't JSON is a genuine fault and throws.
  async function readJson(res) {
    const text = await res.text();
    try { return text ? JSON.parse(text) : {}; } catch { /* not JSON */ }
    if (res.ok) throw new Error(tr('replyUnreadable', 'The server sent a reply this page could not read. Please try again.'));
    return { detail: tr('serverProblem', 'The server ran into a problem (error {n}). Please try again in a moment.')
      .replace('{n}', res.status) };
  }

  // The server labels an unnamed person "—", which is truthy, so `name || 'Groom'`
  // never fell back and the Mangal section read "—: Not Manglik".
  const named = (n) => (n && n.trim() && n.trim() !== '—' ? n.trim() : '');

  /* ---------------------------------------------------------- place picker */
  // IANA zone ids are English; for India (the zone nearly every visitor picks) a
  // Hindi reader is better off without one.
  const tzNote = (tz) => (isHi() && tz === 'Asia/Kolkata' ? '' : (tz || ''));
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
          `<li data-i="${i}">${esc(p.label)}<span>${esc(tzNote(p.timezone))}</span></li>`).join('');
        list.hidden = false;
        qa('li', list).forEach((li) => {
          li.onclick = () => {
            chosen = places[Number(li.dataset.i)];
            input.value = chosen.label;
            if (chosenEl) {
              const tz = tzNote(chosen.timezone);
              chosenEl.textContent = `${chosen.latitude.toFixed(4)}, ` +
                `${chosen.longitude.toFixed(4)}${tz ? ` · ${tz}` : ''}`;
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
      const data = await readJson(res);
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

      ${shareSlot('milan-share')}

      <table class="koota-table"><tbody>${rows}</tbody></table>

      <div class="card milan-extra">
        <h3>${esc(tr('mangalTitle', 'Mangal Dosha Analysis'))}</h3>
        <ul style="line-height: 1.6; font-size: 13.5px; padding-left: 18px; margin: 10px 0;">
          ${manglik(named(ak.groom.name) || 'Groom (वर)', d.mangal.groom)}
          ${manglik(named(ak.bride.name) || 'Bride (कन्या)', d.mangal.bride)}
        </ul>
        ${d.mangal.pair?.note ? `<p style="margin-top: 10px; color: var(--gold);">${esc(d.mangal.pair.note)}</p>` : ''}
        ${d.mangal.pair?.tradition_note ? `<p class="muted-line" style="margin-top: 6px; font-size: 12px;">${esc(d.mangal.pair.tradition_note)}</p>` : ''}
      </div>

      ${d.caveat ? `<p class="warn-line">${esc(d.caveat)}</p>` : ''}
      <p class="muted-line">${esc(ak.band_note || '')} ${esc(ak.convention_note || '')}</p>`;
    shareMilan(ak);                        // DIVASTRO-107
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
  let paShown = null;                      // {p, place}: re-rendered when the language changes

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
      const data = await readJson(res);
      if (!res.ok) throw new Error(failText(data.detail, 'paErr', 'Could not compute the panchang.'));
      paSharePlace = place;                // DIVASTRO-107: the share link's city
      paShown = { p: data, place };
      renderPanchang(data, place);
    } catch (ex) {
      err.textContent = ex.message || tr('paErr', 'Could not compute the panchang.'); err.hidden = false;
    }
  }

  const hhmm = (iso) => (iso ? String(iso).slice(11, 16) : '—');
  const span = (w) => (w ? `${hhmm(w.start)} – ${hhmm(w.end)}` : '—');

  function renderPanchang(p, place) {
    const hi = isHi();
    // /api/panchang sends every name in both languages (app/astro/names_hi.py).
    const name = (r) => (hi ? r.label_hi || r.name_hi : '') || r.label || r.name;
    const until = (iso) => (hi ? `${hhmm(iso)} ${tr('until', 'तक')}` : `${tr('until', 'until')} ${hhmm(iso)}`);
    const limb = (rows) => (rows || []).map((r) =>
      `<div class="limb-line"><b>${esc(name(r))}</b> ` +
      `<span>${esc(until(r.ends))}</span></div>`).join('') || '—';
    const vara = (hi && p.vara && p.vara.name_hi) || p.summary.vara;
    const notes = (hi ? p.notes_hi : p.notes) || [];
    const reckoned = p.reckoned_from === 'sunrise' ? ''
      : `(${esc(hi ? tr('reckonedMidnight', 'reckoned from midnight') : p.reckoned_from)})`;

    q('#panchang-result').innerHTML = `
      <div class="card pa-card">
        <div class="pa-head">
          <div>
            <h2>${esc(vara)} · ${esc(showDate(p.date))}</h2>
            <p class="muted-line">${esc(placeLabel(place))} ${reckoned}</p>
          </div>
          <div class="pa-sun">
            <div title="${esc(tr('sunL', 'Sunrise – sunset'))}">☀ ${hhmm(p.sun.rise)} – ${hhmm(p.sun.set)}</div>
            <div title="${esc(tr('moonL', 'Moonrise – moonset'))}">☾ ${hhmm(p.moon.rise)} – ${hhmm(p.moon.set)}</div>
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
          <div class="bad"><span>${esc(tr('rahuKaalL', 'Rahu Kaal'))}</span><b>${span(p.muhurta.rahu_kaal)}</b></div>
          <div class="bad"><span>${esc(tr('yamagandaL', 'Yamaganda'))}</span><b>${span(p.muhurta.yamaganda)}</b></div>
          <div class="bad"><span>${esc(tr('gulikaL', 'Gulika Kaal'))}</span><b>${span(p.muhurta.gulika_kaal)}</b></div>
          <div class="good"><span>${esc(tr('abhijitL', 'Abhijit Muhurta'))}</span><b>${
            p.muhurta.abhijit ? span(p.muhurta.abhijit) : esc(tr('none', 'none today'))}</b></div>
        </div>
      </div>

      ${notes.length
        ? `<p class="muted-line">${esc(notes.join(' '))}</p>` : ''}
      ${shareSlot('panchang-share')}`;
    sharePanchang(p);                      // DIVASTRO-107
    q('#panchang-result').hidden = false;
  }

  /* ------------------------------------------------- home: the Today strip */
  // DIVASTRO-101. Of ~23 real visitors in a week, ~21 left the home screen without
  // tapping anything: nothing on it was worth having by itself. Today's tithi,
  // nakshatra and Rahu Kaal are what people check daily, cost no LLM tokens, and
  // come from the same /api/panchang the Panchang tool above already calls, so
  // there is no second computation to keep in step with this one.
  //
  // It lives here rather than in app.js because it reuses this file's place picker
  // and opens the Panchang tool with the same city already chosen.
  const TODAY_KEY = 'astro.todayCity';
  const DELHI = { latitude: 28.6139, longitude: 77.2090, timezone: 'Asia/Kolkata', label: 'New Delhi, India' };
  const todayStrip = q('#today-strip');
  let todayPlace = DELHI;
  let todayData = null;
  let todaySeq = 0;                       // a slow reply for an old city must not overwrite a newer one
  let todayVrat = null;                   // DIVASTRO-111: today's vrat/festival names, or null

  // Anything in storage was written by an older page (or by hand): use it only if it
  // still looks like a place, else quietly fall back to Delhi.
  try {
    const saved = JSON.parse(localStorage.getItem(TODAY_KEY) || 'null');
    if (saved && Number.isFinite(saved.latitude) && Number.isFinite(saved.longitude)
        && typeof saved.label === 'string') todayPlace = saved;
  } catch { /* private mode or bad JSON: Delhi */ }

  // The panchang lists every tithi/nakshatra that touches the day; "today's" is the
  // one running now, not the one at sunrise (they differ for much of the day).
  const current = (rows) => {
    const now = Date.now();
    return (rows || []).find((r) => Date.parse(r.starts) <= now && now < Date.parse(r.ends))
      || (rows || [])[0] || null;
  };

  function renderTodayStrip() {
    if (!todayStrip) return;
    const hi = typeof state !== 'undefined' && state.lang === 'hi';
    const set = (sel, text) => { const el = q(sel); if (el) el.textContent = text; };
    set('#today-title', tr('todayTitle', 'Today'));
    set('#today-tithi-l', tr('todayTithi', 'Tithi'));
    set('#today-nak-l', tr('todayNak', 'Nakshatra'));
    set('#today-rahu-l', tr('todayRahu', 'Rahu Kaal'));
    set('#today-city-name', String(placeLabel(todayPlace)).split(',')[0]);
    q('#today-city')?.setAttribute('aria-label', `${tr('todayChange', 'Change city')}: ${todayPlace.label}`);
    q('#today-place')?.setAttribute('placeholder', tr('todayCityPh', 'Start typing a city…'));
    const shareEl = q('#today-share');     // DIVASTRO-107: hidden until there is something to share
    if (shareEl) shareEl.hidden = !todayData;
    renderVratLine(hi);
    if (!todayData) return;               // still loading: the skeleton stays

    const ti = current(todayData.tithi);
    const nk = current(todayData.nakshatra);
    const rk = todayData.muhurta && todayData.muhurta.rahu_kaal;
    // /api/panchang sends the Hindi names beside the English (app/astro/names_hi.py).
    const tithi = ti ? ((hi && ti.label_hi) || ti.label || ti.name) : '—';
    const nak = nk ? ((hi && nk.name_hi) || nk.name) : '—';
    const now = Date.now();
    const inRahu = !!(rk && Date.parse(rk.start) <= now && now < Date.parse(rk.end));
    const rahu = rk ? `${hhmm(rk.start)}–${hhmm(rk.end)}` : '—';
    set('#today-tithi', tithi);
    set('#today-nak', nak);
    set('#today-rahu', inRahu ? `${rahu} · ${tr('todayNow', 'now')}` : rahu);
    q('#today-rahu')?.parentElement.classList.toggle('now', inRahu);
    shareToday(tithi, rahu);               // DIVASTRO-107
    q('#today-open')?.setAttribute('aria-label',
      `${tr('todayOpen', "Open today's full panchang")}. ${tr('todayTithi', 'Tithi')}: ${tithi}. ` +
      `${tr('todayNak', 'Nakshatra')}: ${nak}. ${tr('todayRahu', 'Rahu Kaal')}: ${rahu}.`);
  }
  // app.js calls this from applyLanguage, so the strip follows the EN / हिं switch.
  window.renderTodayStrip = renderTodayStrip;

  // DIVASTRO-111: one short line under the strip when today is a vrat or festival
  // ("Today: Papankusha Ekadashi"), linking to the vrat-tyohar page. Nothing at all
  // on an ordinary day or if the lookup fails.
  function renderVratLine(hi) {
    const el = q('#today-vrat');
    if (!el) return;
    const items = (todayVrat && Array.isArray(todayVrat.items)) ? todayVrat.items : [];
    if (!todayData || !items.length) { el.hidden = true; return; }
    const names = items.slice(0, 2).map((v) => (hi ? v.name_hi : v.name_en)).join(', ');
    el.textContent = `${hi ? 'आज' : 'Today'}: ${names}`;
    el.setAttribute('href', hi ? '/hi/vrat-tyohar' : '/vrat-tyohar');
    el.hidden = false;
  }

  async function loadVrat(seq) {
    try {
      const params = new URLSearchParams({
        lat: todayPlace.latitude, lon: todayPlace.longitude, tz: todayPlace.timezone || '',
      });
      const res = await fetch(`/api/vrat/today?${params}`);
      if (!res.ok) return;
      const data = await res.json();
      if (seq !== todaySeq) return;
      todayVrat = data;
      renderTodayStrip();
    } catch { /* silent: the line simply does not appear */ }
  }

  async function loadToday() {
    if (!todayStrip) return;
    const seq = ++todaySeq;
    todayData = null;
    todayVrat = null;
    todayStrip.classList.add('loading');
    renderTodayStrip();
    const params = new URLSearchParams({
      latitude: todayPlace.latitude, longitude: todayPlace.longitude, timezone: todayPlace.timezone || '',
    });
    try {
      const res = await fetch(`/api/panchang?${params}`);
      if (!res.ok) throw new Error(String(res.status));
      const data = await res.json();
      if (seq !== todaySeq) return;
      todayData = data;
      todayStrip.classList.remove('loading');
      renderTodayStrip();
      loadVrat(seq);                      // DIVASTRO-111, after the strip: never delays it
    } catch {
      // A home screen that shows a broken box is worse than one without it.
      if (seq === todaySeq) todayStrip.hidden = true;
    }
  }

  if (todayStrip) {
    const picker = q('#today-picker');
    const cityBtn = q('#today-city');
    placePicker(q('#today-place'), q('#today-results'), null);
    const closePicker = () => { picker.hidden = true; cityBtn.setAttribute('aria-expanded', 'false'); };
    cityBtn.addEventListener('click', () => {
      picker.hidden = !picker.hidden;
      cityBtn.setAttribute('aria-expanded', String(!picker.hidden));
      if (!picker.hidden) { q('#today-place').value = ''; q('#today-place').focus(); }
    });
    q('#today-place').addEventListener('keydown', (e) => { if (e.key === 'Escape') closePicker(); });
    q('#today-place').addEventListener('place:chosen', (e) => {
      const p = e.detail;
      todayPlace = { latitude: p.latitude, longitude: p.longitude, timezone: p.timezone, label: p.label };
      try { localStorage.setItem(TODAY_KEY, JSON.stringify(todayPlace)); } catch { /* private mode */ }
      closePicker();
      loadToday();
    });
    // The strip is the way in to the full Panchang, for the same city.
    q('#today-open').addEventListener('click', () => {
      showStage('stage-panchang');
      paPlace = todayPlace;
      q('#pa-place').value = todayPlace.label;
      q('#pa-chosen').hidden = true;
      q('#pa-date').value = '';            // the strip is about today
      loadPanchang();
    });
    loadToday();
  }

  /* ---------------------------------------------------------------- muhurat */
  const muPick = placePicker(q('#mu-place'), q('#mu-results'), q('#mu-chosen'));
  let muPlace = null;

  function initMuhuratDates() {
    const today = todayIn((muPlace || muPick())?.timezone);
    if (!q('#mu-from').value) q('#mu-from').value = today;
    if (!q('#mu-to').value) q('#mu-to').value = addDaysIso(today, 30);
  }

  q('#mu-place')?.addEventListener('place:chosen', (e) => {
    muPlace = e.detail;
  });

  let muShown = false;                     // a result is on screen: refetched on a language switch
  q('#muhurat-go')?.addEventListener('click', () => findMuhurat(true));

  async function findMuhurat(scroll) {
    const btn = q('#muhurat-go');
    const err = q('#muhurat-error');
    err.hidden = true;

    const event = q('#mu-event').value;
    const fromDate = q('#mu-from').value;
    const toDate = q('#mu-to').value;
    if (!fromDate || !toDate) {
      err.textContent = tr('muNeedDates', 'Please choose both from and to dates.');
      err.hidden = false;
      return;
    }

    const place = muPlace || muPick() ||
      { latitude: 28.6139, longitude: 77.2090, timezone: 'Asia/Kolkata', label: 'New Delhi, India' };

    const lang = curLang();
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
      const data = await readJson(res);
      if (!res.ok) throw new Error(failText(data.detail, 'muErr', 'Could not calculate muhurat.'));
      renderMuhurat(data, place, scroll);
      muShown = true;
    } catch (ex) {
      err.textContent = ex.message || tr('muErr', 'Could not calculate muhurat.'); err.hidden = false;
    } finally {
      btn.disabled = false; btn.classList.remove('busy');
    }
  }

  function renderMuhurat(data, place, scroll) {
    const days = data.days || [];
    if (!days.length) {
      q('#muhurat-result').innerHTML = `<div class="card"><p>${esc(tr('muNone', 'No dates found for this range.'))}</p></div>`;
      q('#muhurat-result').hidden = false;
      return;
    }

    const rows = days.map((d) => `
      <tr style="border-bottom: 1px solid rgba(255,255,255,0.04);">
        <td style="padding: 10px 8px; white-space: nowrap;">
          <b>${esc(showDate(d.date))}</b><br/>
          <span style="font-size: 12px; color: var(--ink-dim);">${esc(d.vara)}</span>
        </td>
        <td style="padding: 10px 8px;">
          <span class="badge ${esc(d.badge)}" style="font-size: 12px;">${esc(d.verdict)}</span>
        </td>
        <td style="padding: 10px 8px; font-size: 12.5px;">
          <b>${esc(d.tithi)}</b> · ${esc(d.nakshatra)}<br/>
          <span style="font-size: 12px; color: var(--ink-dim);">${esc(d.yoga)}</span>
        </td>
        <td style="padding: 10px 8px; font-size: 12px; color: var(--gold);">
          ${d.abhijit ? `${esc(tr('abhijitShort', 'Abhijit'))}: ${esc(d.abhijit)}` : '—'}
        </td>
        <td style="padding: 10px 8px; font-size: 12px;">
          ${(d.reasons || []).map(r => `<span style="display:block;">• ${esc(r)}</span>`).join('') || '—'}
        </td>
      </tr>
    `).join('');

    q('#muhurat-result').innerHTML = `
      <div class="card" style="margin-top: 20px; overflow-x: auto;">
        <h3 style="margin-bottom: 12px; color: var(--gold);">
          ${esc(tr('muhuratResultsTitle', 'Auspicious Dates Summary'))} — ${esc(placeLabel(place))}
        </h3>
        <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 13px;">
          <thead>
            <tr style="border-bottom: 1px solid var(--line); color: var(--ink-dim);">
              <th style="padding: 8px;">${esc(tr('muColDate', 'Date / Day'))}</th>
              <th style="padding: 8px;">${esc(tr('muColVerdict', 'Verdict'))}</th>
              <th style="padding: 8px;">${esc(tr('muColLimbs', 'Tithi & Nakshatra'))}</th>
              <th style="padding: 8px;">${esc(tr('muColAbhijit', 'Abhijit'))}</th>
              <th style="padding: 8px;">${esc(tr('muColReasons', 'Evaluation / Reasons'))}</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    `;
    q('#muhurat-result').hidden = false;
    if (scroll) q('#muhurat-result').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  // --------------------------------------------------------------------------
  // Choghadiya
  // --------------------------------------------------------------------------

  const choPlaceInput = q('#cho-place');
  const choResults = q('#cho-results');
  const choChosen = q('#cho-chosen');

  // These three lines used to call show(), suggest() and window.APP_STATE, none of
  // which exist: the home-page card did nothing (ReferenceError), typing a place
  // threw on every keystroke, and Hindi users always got English. Found by the
  // browser audit in tests/e2e/test_mobile_screens.py.
  const getChoPlace = choPlaceInput ? placePicker(choPlaceInput, choResults, choChosen) : () => null;

  q('#open-choghadiya')?.addEventListener('click', () => {
    showStage('stage-choghadiya');
    if (!q('#cho-date').value) {
      q('#cho-date').value = todayIn(getChoPlace()?.timezone);
    }
  });

  let choShown = false;                    // a result is on screen: refetched on a language switch
  q('#choghadiya-go')?.addEventListener('click', () => loadChoghadiya(true));

  async function loadChoghadiya(scroll) {
    const err = q('#choghadiya-error');
    err.hidden = true; err.textContent = '';
    const btn = q('#choghadiya-go');
    const place = getChoPlace() || {
      label: 'New Delhi, India',
      latitude: 28.6139,
      longitude: 77.2090,
      timezone: 'Asia/Kolkata',
    };
    const targetDate = q('#cho-date').value || todayIn(place.timezone);
    const lang = curLang();

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
      const data = await readJson(res);
      if (!res.ok) throw new Error(failText(data.detail, 'choErr', 'Could not calculate Choghadiya.'));
      renderChoghadiya(data, place, lang, scroll);
      choShown = true;
    } catch (ex) {
      err.textContent = ex.message || tr('choErr', 'Could not calculate Choghadiya.'); err.hidden = false;
    } finally {
      btn.disabled = false; btn.classList.remove('busy');
    }
  }

  function renderChoghadiya(data, place, lang, scroll) {
    const isHi = lang === 'hi';
    const act = data.active_slot;
    const badgeColor = {
      auspicious: 'var(--green)',
      neutral: 'var(--gold)',
      inauspicious: 'var(--rose)',
    };

    function renderSlots(slots) {
      return slots.map(s => {
        const bg = s.is_current ? 'background: rgba(212, 175, 55, 0.15); border-left: 3px solid var(--gold);' : '';
        const dotColor = badgeColor[s.quality] || '#999';
        return `
          <tr style="border-bottom: 1px solid rgba(255,255,255,0.04); ${bg}">
            <td style="padding: 10px 8px; font-weight: bold;">
              ${esc(s.start)} – ${esc(s.end)}
              ${s.is_current ? `<span style="margin-left: 6px; font-size: 12px; color: var(--gold); border: 1px solid var(--gold); border-radius: 4px; padding: 1px 4px;">${isHi ? 'वर्तमान' : 'NOW'}</span>` : ''}
            </td>
            <td style="padding: 10px 8px;">
              <b>${esc(s.name_label)}</b><br/>
              <span style="font-size: 12px; color: var(--ink-dim);">${isHi ? 'स्वामी: ' : 'Lord: '}${esc(s.ruler_label)}</span>
            </td>
            <td style="padding: 10px 8px;">
              <span style="display: inline-flex; align-items: center; gap: 5px; font-size: 12px; font-weight: 600; color: ${dotColor};">
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
              ${isHi ? 'दैनिक चौघड़िया चक्र' : 'Choghadiya Muhurta Schedule'} — ${esc(placeLabel(place))}
            </h3>
            <p style="margin: 4px 0 0 0; font-size: 12.5px; color: var(--ink-dim);">
              ${esc(isHi ? data.weekday_hi : data.weekday)} · ${esc(showDate(data.date))} · ${isHi ? 'सूर्योदय' : 'Sunrise'}: ${esc(data.sunrise)} · ${isHi ? 'सूर्यास्त' : 'Sunset'}: ${esc(data.sunset)}
            </p>
          </div>
          ${act ? `
            <div style="padding: 8px 14px; border-radius: 8px; background: rgba(212, 175, 55, 0.1); border: 1px solid var(--gold); text-align: right;">
              <span style="font-size: 12px; color: var(--gold); text-transform: uppercase;">${isHi ? 'वर्तमान सक्रिय मुहूर्त' : 'Active Muhurta Now'}</span>
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
    if (scroll) q('#choghadiya-result').scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  /* ---------------------------------------- WhatsApp share (DIVASTRO-107) */
  // Builders and the wa.me / navigator.share plumbing live in share.js. Only a
  // score, today's public almanac values and a city ever go into a share text —
  // never a name, birth date, time or place (the Milan form has all four).
  let paSharePlace = null;
  const SHARE = () => window.DAShare || null;
  const shareLabel = () => tr('shareWa', 'Share on WhatsApp');
  const shareSlot = (id) => (SHARE() ? `<div class="share-row">${SHARE().button(id, shareLabel())}</div>` : '');

  function shareMilan(ak) {
    const S = SHARE();
    if (!S) return;
    S.wire(q('#milan-share'), S.milanText(ak.total, ak.maximum), S.url('/kundali-milan', 'milan'));
  }

  function sharePanchang(p) {
    const S = SHARE();
    if (!S) return;
    const hi = typeof state !== 'undefined' && state.lang === 'hi';
    const today = !q('#pa-date').value;
    const ti = today ? current(p.tithi) : (p.tithi || [])[0];
    const nk = today ? current(p.nakshatra) : (p.nakshatra || [])[0];
    const place = paSharePlace || DELHI;
    const text = S.panchangText({
      city: S.cityName(place),
      date: p.date,
      tithi: ti ? ((hi && ti.label_hi) || ti.label || ti.name) : '—',
      nak: nk ? ((hi && nk.name_hi) || nk.name) : '—',
      rahu: (p.muhurta && p.muhurta.rahu_kaal) ? span(p.muhurta.rahu_kaal) : '—',
    });
    S.wire(q('#panchang-share'), text, S.url(S.cityPath('panchang', place, '/?open=panchang'), 'panchang'));
  }

  function shareToday(tithi, rahu) {
    const S = SHARE();
    const el = q('#today-share');
    if (!S || !el) return;
    q('#today-share-l').textContent = tr('shareShort', 'Share');
    el.setAttribute('aria-label', shareLabel());
    S.wire(el, S.todayText({ city: S.cityName(todayPlace), rahu, tithi }),
      S.url(S.cityPath('rahu-kaal', todayPlace, '/?open=panchang'), 'rahukaal'));
  }
  // The SEO city list may arrive after today's panchang: relink once it does.
  if (SHARE()) SHARE().ready.then(() => { if (todayData) renderTodayStrip(); });

  /* ------------------------------------------------- EN / हिं switch (tools) */
  // The tool pages' static labels, and any result already on screen: a Panchang
  // re-renders from the bilingual data it holds; Muhurat and Choghadiya come back
  // from the server already in one language, so they are asked again.
  const MU_EVENTS = { marriage: 'evMarriage', griha_pravesh: 'evGrihaPravesh', mundan: 'evMundan',
                      namkaran: 'evNamkaran', general: 'evGeneral' };
  function applyToolsLanguage() {
    const set = (sel, text) => { const el = q(sel); if (el) el.textContent = text; };
    set('#panchang-title', tr('panchangTitle', 'Panchang'));
    set('#panchang-sub', tr('panchangSub', 'The five limbs of the day, with Rahu Kaal and the auspicious windows.'));
    set('#lbl-pa-date', tr('lblDate', 'Date'));
    set('#lbl-pa-place', tr('lblPlace', 'Place'));
    qa('#pa-place, #mu-place, #cho-place').forEach((el) => {
      el.placeholder = tr('todayCityPh', 'Start typing a city…');
    });
    qa('#mu-event option').forEach((o) => {
      if (MU_EVENTS[o.value]) o.textContent = tr(MU_EVENTS[o.value], o.textContent);
    });
    if (paShown) renderPanchang(paShown.p, paShown.place);
    if (muShown && !q('#muhurat-result').hidden) findMuhurat(false);
    if (choShown && !q('#choghadiya-result').hidden) loadChoghadiya(false);
  }
  window.applyToolsLanguage = applyToolsLanguage;
  applyToolsLanguage();
  // The SEO city list (Hindi city names) may arrive after the first render.
  if (SHARE()) SHARE().ready.then(() => { if (paShown) renderPanchang(paShown.p, paShown.place); });

  /* ------------------------------------------------------------- deep links */
  // The server-rendered /panchang, /rahu-kaal, /choghadiya and /kundali-milan
  // pages (app/seo_pages.py) link here as /?open=<tool>. Clicking the home card
  // reuses exactly what a visitor's own tap would do, then the parameter is
  // dropped so a reload or a shared link of the address bar starts clean.
  const DEEP_LINKS = {
    panchang: '#open-panchang', 'rahu-kaal': '#open-panchang',
    choghadiya: '#open-choghadiya', muhurat: '#open-muhurat',
    milan: '#open-milan', 'kundali-milan': '#open-milan',
    kundali: '#home-cta',     // birth form: /free-kundali and rashifal CTAs, like the home CTA
  };
  const deepParams = new URLSearchParams(location.search);
  const deepTarget = DEEP_LINKS[deepParams.get('open')];
  if (deepTarget) {
    q(deepTarget)?.click();
    deepParams.delete('open');
    history.replaceState({}, '', location.pathname +
      (deepParams.toString() ? `?${deepParams}` : ''));
  }
})();
