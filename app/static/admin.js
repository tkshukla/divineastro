/* Admin panel.
 *
 * Every endpoint it touches is already gated server-side by the `admin`
 * dependency, so this file is convenience, not security.
 */
'use strict';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

const esc = (s) => String(s ?? '').replace(/[&<>"']/g,
  (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

const rupees = (n) => `₹${Number(n).toLocaleString('en-IN')}`;

async function api(path, opts = {}) {
  const res = await fetch(path, {
    credentials: 'same-origin',
    headers: opts.body ? { 'Content-Type': 'application/json' } : {},
    ...opts,
  });
  let body = null;
  try { body = await res.json(); } catch { /* empty or non-JSON */ }
  if (!res.ok) {
    const err = new Error((body && body.detail) || `HTTP ${res.status}`);
    err.status = res.status;
    throw err;
  }
  return body;
}

function initTheme() {
  const saved = localStorage.getItem('astro.theme');
  const prefersLight = window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches;
  const theme = saved || (prefersLight ? 'light' : 'dark');
  applyTheme(theme);

  $$('.theme-toggle, #theme-toggle').forEach((btn) => {
    btn.onclick = () => {
      const current = document.documentElement.getAttribute('data-theme') === 'light' ? 'light' : 'dark';
      const next = current === 'light' ? 'dark' : 'light';
      applyTheme(next);
      localStorage.setItem('astro.theme', next);
    };
  });
}

function applyTheme(theme) {
  if (theme === 'light') {
    document.documentElement.setAttribute('data-theme', 'light');
    document.body.classList.add('theme-light');
    $$('.theme-icon').forEach((el) => { el.textContent = '🌙'; });
  } else {
    document.documentElement.removeAttribute('data-theme');
    document.body.classList.remove('theme-light');
    $$('.theme-icon').forEach((el) => { el.textContent = '☀️'; });
  }
}
initTheme();

/* ---------------------------------------------------------------- gate --- */

async function boot() {
  let me = null;
  try {
    me = await api('/api/me');
  } catch (e) {
    if (e.status !== 401) throw e;
  }

  const user = me && me.user;
  if (!user) return showGate('Sign in required',
    'Sign in with the Google account registered as an administrator.', true);

  if (!user.is_admin) {
    return showGate('Not an administrator',
      `You are signed in as ${user.email || 'this account'}, which does not have ` +
      'administrator rights. Sign in with the registered administrator account, or ' +
      'add this address to ASTRO_ADMIN_EMAILS on the server and sign in again.', false);
  }

  $('#who').textContent = user.email || user.name || 'admin';
  $('#panel').hidden = false;
  wireTabs();
  wireCoupons();
  wireManual();
  wireUsers();
  wireFeedback();
  wireTraffic();
  wireQuestions();

  // Load active tab initially and prefetch background queues
  await Promise.all([
    loadMetrics(),
    loadCoupons(),
    loadUpi(),
    loadManual(),
    loadFeedback(),
    loadTraffic(),
    loadKundalis(),
    loadHealth(),
  ]);
}

function showGate(title, msg, offerSignIn) {
  $('#gate').hidden = false;
  $('#gate-title').textContent = title;
  $('#gate-msg').textContent = msg;
  if (!offerSignIn) return;

  const box = $('#gate-actions');
  api('/api/auth/providers').then(({ providers, dev_login }) => {
    (providers || []).forEach((p) => {
      const a = document.createElement('a');
      a.className = 'primary as-button';
      a.href = `/api/auth/${p.key}/start?next=/admin`;
      a.textContent = `Continue with ${p.label}`;
      box.appendChild(a);
    });
    if (dev_login) {
      const b = document.createElement('button');
      b.className = 'ghost';
      b.textContent = 'Dev sign-in';
      b.onclick = async () => {
        const email = prompt('Email for dev sign-in:');
        if (!email) return;
        await api('/api/auth/dev', { method: 'POST', body: JSON.stringify({ email }) });
        location.reload();
      };
      box.appendChild(b);
    }
  }).catch((e) => {
    const p = document.createElement('p');
    p.className = 'error';
    p.textContent = `Could not load sign-in options: ${e.message}`;
    box.appendChild(p);
  });
}

function wireTabs() {
  $$('.atab').forEach((b) => {
    b.onclick = () => {
      $$('.atab').forEach((x) => x.classList.toggle('active', x === b));
      $$('.apane').forEach((p) => p.classList.toggle('active', p.id === `pane-${b.dataset.tab}`));
      
      const tab = b.dataset.tab;
      if (tab === 'metrics') loadMetrics();
      else if (tab === 'coupons') loadCoupons();
      else if (tab === 'users') loadUsers();
      else if (tab === 'feedback') loadFeedback();
      else if (tab === 'traffic') loadTraffic();
      else if (tab === 'questions') loadQuestions();
      else if (tab === 'health') loadHealth();
      else if (tab === 'upi') loadUpi();
      else if (tab === 'manual') loadManual();
      else if (tab === 'kundali') loadKundalis();
    };
  });
}

function setCount(id, n) {
  const el = $(id);
  if (!el) return;
  el.textContent = n ? String(n) : '';
  el.classList.toggle('has', !!n);
}

/* ------------------------------------------------------------- metrics --- */

async function loadMetrics() {
  try {
    const data = await api('/api/admin/metrics');
    $('#m-rev-all').textContent = rupees(data.revenue_all_rupees);
    $('#m-rev-month').textContent = rupees(data.revenue_month_rupees);
    $('#m-rev-today').textContent = rupees(data.revenue_today_rupees);
    $('#m-users').textContent = Number(data.total_users).toLocaleString('en-IN');
    $('#m-orders').textContent = Number(data.total_paid_orders).toLocaleString('en-IN');
    $('#m-questions').textContent = Number(data.total_questions).toLocaleString('en-IN');

    // Product sales table
    const pBox = $('#product-sales-list');
    if (data.products && data.products.length) {
      pBox.innerHTML = `
        <table class="admin-table">
          <thead>
            <tr><th>Product</th><th>Orders</th><th>Revenue</th></tr>
          </thead>
          <tbody>
            ${data.products.map((p) => `
              <tr>
                <td><b>${esc(p.title)}</b><br><span class="muted">${esc(p.sku)}</span></td>
                <td>${p.count}</td>
                <td>${rupees(p.revenue_paise / 100)}</td>
              </tr>`).join('')}
          </tbody>
        </table>`;
    } else {
      pBox.innerHTML = '<p class="empty">No product sales yet.</p>';
    }

    // Recent transactions table
    const oBox = $('#recent-orders-list');
    if (data.recent_orders && data.recent_orders.length) {
      oBox.innerHTML = `
        <table class="admin-table">
          <thead>
            <tr><th>Customer</th><th>Product</th><th>Amount</th><th>Status</th><th>Time</th></tr>
          </thead>
          <tbody>
            ${data.recent_orders.map((o) => `
              <tr>
                <td>${esc(o.buyer_name || '—')}<br><span class="muted">${esc(o.buyer_email)}</span></td>
                <td>${esc(o.title)}</td>
                <td><b>${rupees(o.amount_paise / 100)}</b></td>
                <td><span class="pill ${esc(o.status)}">${esc(o.status)}</span></td>
                <td><span class="muted">${esc(o.paid_at || o.created_at)}</span></td>
              </tr>`).join('')}
          </tbody>
        </table>`;
    } else {
      oBox.innerHTML = '<p class="empty">No recent orders.</p>';
    }
  } catch (e) {
    console.error('Failed to load metrics:', e);
  }
}

/* ------------------------------------------------------------- coupons --- */

let allCoupons = [];
let couponFilter = 'current';   // which chip is selected
let editingCoupon = null;       // the coupon open in the form, or null when creating

// The server holds every amount in paise, including a flat coupon's discount;
// everything typed into this form is rupees.
const toPaise = (rupeesValue) => Math.round(Number(rupeesValue) * 100);
const fromPaise = (paise) => (paise ? paise / 100 : '');

const fmtDate = (iso) => (iso
  ? new Date(iso).toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
  : '');

const STATUS_LABEL = {
  live: 'live', paused: 'paused', expired: 'expired', scheduled: 'scheduled',
  used_up: 'used up', deleted: 'deleted',
};

// [key, chip label, predicate]. "Current" is the default: everything that has
// not been deleted, so deleted coupons are out of the way but one click from view.
const COUPON_FILTERS = [
  ['current', 'Current', (c) => c.status !== 'deleted'],
  ['live', 'Live', (c) => c.status === 'live'],
  ['paused', 'Paused', (c) => c.status === 'paused'],
  ['ended', 'Expired / used up', (c) => c.status === 'expired' || c.status === 'used_up'],
  ['deleted', 'Deleted', (c) => c.status === 'deleted'],
  ['all', 'Everything', () => true],
];

function wireCoupons() {
  const form = $('#coupon-form');
  const btnToggle = $('#btn-toggle-coupon-form');
  const btnCancel = $('#btn-cancel-coupon-form');
  const search = $('#coupon-search');
  const kind = $('#c-kind');
  const err = $('#coupon-error');

  const syncKind = () => {
    $('#c-value-label').textContent = {
      percent: 'Value (%)', flat: 'Value (₹ off)', extra_credits: 'Extra questions',
    }[kind.value];
    $('#c-maxoff-field').hidden = kind.value !== 'percent';
  };
  kind.onchange = syncKind;

  // One form serves both jobs. With a coupon it edits that coupon (the code is
  // its identity, so it is read-only); with none it creates a new one.
  window.openCouponForm = (coupon) => {
    editingCoupon = coupon || null;
    form.reset();
    err.hidden = true;
    $('#c-form-title').textContent = coupon ? `Edit coupon ${coupon.code}` : 'Create Promotion Code';
    $('#c-submit-label').textContent = coupon ? 'Save changes' : 'Save & Activate Coupon';
    $('#c-code').disabled = Boolean(coupon);
    $('#c-code-note').textContent = coupon ? 'cannot be changed' : '';

    const skuSelect = $('#c-skus');
    const targets = coupon
      ? String(coupon.applies_to || 'all').toLowerCase().split(',').map((t) => t.trim()).filter(Boolean)
      : [];
    // A target that is no longer in the catalogue must survive a save, not be
    // silently dropped because it has no option to be selected.
    const known = new Set($$('option', skuSelect).map((o) => o.value));
    targets.filter((t) => t !== 'all' && t !== '*' && !known.has(t)).forEach((t) => {
      const o = document.createElement('option');
      o.value = t; o.textContent = `${t} (not in the current catalogue)`;
      skuSelect.appendChild(o);
    });
    $$('option', skuSelect).forEach((o) => { o.selected = targets.includes(o.value); });

    if (coupon) {
      $('#c-code').value = coupon.code;
      kind.value = coupon.kind;
      $('#c-value').value = coupon.kind === 'flat' ? coupon.value / 100 : coupon.value;
      $('#c-max').value = coupon.max_redemptions ?? '';
      $('#c-per').value = coupon.max_per_user;
      $('#c-until').value = coupon.expires_at ? coupon.expires_at.slice(0, 10) : '';
      $('#c-min').value = fromPaise(coupon.min_amount_paise);
      $('#c-maxoff').value = fromPaise(coupon.max_discount_paise);
      $('#c-desc').value = coupon.description || '';
    }
    syncKind();
    form.hidden = false;
    form.scrollIntoView({ behavior: 'smooth', block: 'start' });
  };

  btnToggle.onclick = () => {
    if (!form.hidden && !editingCoupon) { form.hidden = true; return; }
    window.openCouponForm(null);
  };
  btnCancel.onclick = () => { form.hidden = true; editingCoupon = null; };
  search.oninput = () => renderCouponsList();

  const skuSelect = $('#c-skus');
  api('/api/products').then(({ products }) => {
    skuSelect.innerHTML =
      '<option value="questions">All question packs</option>' +
      '<option value="kundali">All hand-written kundalis</option>' +
      (products || []).map((p) =>
        `<option value="${esc(p.sku)}">${esc(p.title)} — ${rupees(p.rupees)}</option>`).join('');
  }).catch(() => {});

  form.onsubmit = async (ev) => {
    ev.preventDefault();
    err.hidden = true;
    const btn = $('button[type=submit]', form);

    const k = kind.value;
    const raw = Number($('#c-value').value);
    const skus = $$('#c-skus option:checked').map((o) => o.value);
    const until = $('#c-until').value;
    const body = {
      kind: k,
      value: k === 'flat' ? toPaise(raw) : raw,     // flat: rupees typed -> paise stored
      applies_to: skus.length ? skus.join(',') : 'all',
      max_redemptions: $('#c-max').value ? Number($('#c-max').value) : null,
      max_per_user: Number($('#c-per').value || 1),
      min_amount_paise: $('#c-min').value ? toPaise($('#c-min').value) : 0,
      max_discount_paise: k === 'percent' && $('#c-maxoff').value ? toPaise($('#c-maxoff').value) : null,
      description: $('#c-desc').value.trim(),
    };

    btn.disabled = true;
    try {
      if (editingCoupon) {
        // Only re-send the expiry if the date was actually changed, so a coupon
        // whose expiry carries a time is not rewritten to 23:59:59 by a save.
        const was = editingCoupon.expires_at ? editingCoupon.expires_at.slice(0, 10) : '';
        if (until !== was) body.expires_at = until ? `${until}T23:59:59` : null;
        await api(`/api/admin/coupons/${editingCoupon.id}`,
          { method: 'PATCH', body: JSON.stringify(body) });
      } else {
        body.code = $('#c-code').value;
        body.expires_at = until ? `${until}T23:59:59` : null;
        await api('/api/admin/coupons', { method: 'POST', body: JSON.stringify(body) });
        couponFilter = 'current';
      }
      form.hidden = true;
      editingCoupon = null;
      await loadCoupons();
    } catch (e) {
      err.textContent = e.message;
      err.hidden = false;
    } finally {
      btn.disabled = false;
    }
  };
}

function describe(c) {
  if (c.kind === 'percent') {
    return `${c.value}% off` + (c.max_discount_paise ? ` (max ${rupees(c.max_discount_paise / 100)})` : '');
  }
  if (c.kind === 'flat') return `${rupees(c.value / 100)} off`;
  return `+${c.value} free questions`;
}

async function loadCoupons() {
  try {
    const { coupons } = await api('/api/admin/coupons');
    allCoupons = coupons || [];
    // The sidebar count is what a customer could use right now.
    setCount('#c-coupons', allCoupons.filter((c) => c.status === 'live').length);
    renderCouponsList();
  } catch (e) {
    console.error('Failed to load coupons:', e);
  }
}

function renderCouponChips() {
  const box = $('#coupon-chips');
  box.innerHTML = COUPON_FILTERS.map(([key, label, test]) => {
    const n = allCoupons.filter(test).length;
    return `<button type="button" class="chip${key === couponFilter ? ' on' : ''}" data-f="${key}"
      aria-pressed="${key === couponFilter}">${esc(label)} <span class="n">${n}</span></button>`;
  }).join('');
  $$('button', box).forEach((b) => {
    b.onclick = () => { couponFilter = b.dataset.f; renderCouponsList(); };
  });
}

function couponUsesTable(rows) {
  if (!rows.length) return '<p class="empty" style="margin:8px 0 0;">Not used yet.</p>';
  return `<table class="admin-table" style="margin-top:8px;">
    <thead><tr><th>Customer</th><th>Order</th><th>Discount</th><th>Order status</th><th>When</th></tr></thead>
    <tbody>${rows.map((r) => `<tr>
      <td>${esc(r.email || '—')}</td><td>#${r.order_id} <span class="muted">${esc(r.sku)}</span></td>
      <td>${rupees(r.discount_paise / 100)}</td>
      <td><span class="pill ${esc(r.order_status)}">${esc(r.order_status.replace('_', ' '))}</span></td>
      <td><span class="muted">${esc(r.at)}</span></td></tr>`).join('')}</tbody></table>`;
}

function renderCouponsList() {
  renderCouponChips();
  const box = $('#coupon-list');
  const query = ($('#coupon-search')?.value || '').trim().toLowerCase();
  const test = (COUPON_FILTERS.find(([k]) => k === couponFilter) || COUPON_FILTERS[0])[2];

  const filtered = allCoupons.filter((c) => test(c) && (!query
    || c.code.toLowerCase().includes(query)
    || (c.applies_to && c.applies_to.toLowerCase().includes(query))
    || (c.description && c.description.toLowerCase().includes(query))));

  if (!filtered.length) {
    box.innerHTML = query
      ? '<p class="empty">No coupons match your filter.</p>'
      : couponFilter === 'deleted'
        ? '<p class="empty">Nothing has been deleted.</p>'
        : allCoupons.length
          ? '<p class="empty">No coupons in this view.</p>'
          : '<p class="empty">No coupons created yet. Click "+ Create New Coupon" above.</p>';
    return;
  }

  box.innerHTML = filtered.map((c) => {
    const deleted = c.status === 'deleted';
    const bits = [
      `Target: <code>${esc(c.applies_to === 'all' ? 'All Products' : c.applies_to)}</code>`,
      `Uses: <b>${c.redemptions}${c.max_redemptions ? ` / ${c.max_redemptions}` : ' (unlimited)'}</b>`,
      `Per customer: ${c.max_per_user || '∞'}`,
      c.min_amount_paise ? `Min order: ${rupees(c.min_amount_paise / 100)}` : '',
      c.starts_at ? `Starts: <b>${esc(fmtDate(c.starts_at))}</b>` : '',
      c.expires_at ? `Expires: <b>${esc(fmtDate(c.expires_at))}</b>` : 'No expiry',
    ].filter(Boolean).join(' &middot; ');
    const trail = [
      `Created ${esc(fmtDate(c.created_at))}`,
      deleted ? `<span class="warn">Deleted ${esc(fmtDate(c.deleted_at))}</span>` : '',
      c.description ? `Note: ${esc(c.description)}` : '',
      c.total_discount_paise ? `Customer savings given: ${rupees(c.total_discount_paise / 100)}` : '',
    ].filter(Boolean).join(' &middot; ');

    return `
    <div class="row${deleted ? ' is-deleted' : ''}" data-id="${c.id}">
      <div class="row-main">
        <div class="row-title">
          <code class="code">${esc(c.code)}</code>
          <button class="ghost sm btn-copy" data-code="${esc(c.code)}" title="Copy code" style="padding:2px 7px;font-size:0.75rem;margin-left:6px;">&#128203; Copy</button>
          <span class="pill st-${esc(c.status)}" style="margin-left:6px;">${esc(STATUS_LABEL[c.status] || c.status)}</span>
          &middot; <b>${esc(describe(c))}</b>
        </div>
        <div class="row-sub">${bits}<br /><span class="muted">${trail}</span></div>
        <div class="uses" hidden></div>
      </div>
      <div class="row-act">
        ${deleted
          ? '<button class="primary sm" data-act="restore">Restore</button>'
          : `<button class="ghost sm" data-act="edit">Edit</button>
             <button class="ghost sm" data-act="toggle">${c.active ? 'Pause' : 'Resume'}</button>
             <button class="danger sm" data-act="delete">Delete</button>`}
        <button class="ghost sm" data-act="uses">Uses (${c.redemptions})</button>
      </div>
    </div>`;
  }).join('');

  $$('#coupon-list .row').forEach((row) => {
    const id = Number(row.dataset.id);
    const c = allCoupons.find((x) => x.id === id);
    const fail = (e) => alert(e.message);

    row.querySelector('.btn-copy').onclick = (ev) => {
      const btn = ev.currentTarget;
      navigator.clipboard.writeText(btn.dataset.code).then(() => {
        btn.textContent = 'Copied!';
        setTimeout(() => { btn.textContent = '📋 Copy'; }, 1500);
      });
    };

    const on = (act, fn) => {
      const b = row.querySelector(`[data-act="${act}"]`);
      if (b) b.onclick = async () => { b.disabled = true; try { await fn(b); } catch (e) { fail(e); } b.disabled = false; };
    };

    on('edit', async () => window.openCouponForm(c));
    on('toggle', async () => {
      await api(`/api/admin/coupons/${id}`, { method: 'PATCH', body: JSON.stringify({ active: !c.active }) });
      await loadCoupons();
    });
    on('delete', async () => {
      if (!confirm(`Delete coupon ${c.code}?\n\nCustomers will no longer be able to use it. ` +
        'It stays in the Deleted list, and you can restore it later.')) return;
      await api(`/api/admin/coupons/${id}`, { method: 'DELETE' });
      await loadCoupons();
    });
    on('restore', async () => {
      await api(`/api/admin/coupons/${id}/restore`, { method: 'POST' });
      couponFilter = 'paused';      // it comes back paused — show where it went
      await loadCoupons();
    });
    on('uses', async () => {
      const panel = row.querySelector('.uses');
      if (!panel.hidden) { panel.hidden = true; return; }
      const { redemptions } = await api(`/api/admin/coupons/${id}/redemptions`);
      panel.innerHTML = couponUsesTable(redemptions);
      panel.hidden = false;
    });
  });
}

/* --------------------------------------------------------------- users --- */

let umProducts = null;      // catalogue for the "give a product" picker
let umLastFocus = null;     // what to re-focus when the panel closes
let umFlash = '';           // one-shot confirmation shown after an action re-renders the panel

function wireUsers() {
  const search = $('#user-search');
  if (search) search.oninput = debounce(() => loadUsers(), 300);

  const back = $('#user-modal');
  $('#um-close').onclick = closeUserModal;
  back.onclick = (ev) => { if (ev.target === back) closeUserModal(); };
  document.addEventListener('keydown', (ev) => {
    if (ev.key === 'Escape' && !back.hidden) closeUserModal();
  });
}

async function loadUsers() {
  const box = $('#users-list');
  const q = ($('#user-search')?.value || '').trim();
  try {
    const { users } = await api(`/api/admin/users?q=${encodeURIComponent(q)}`);
    if (!users || !users.length) {
      box.innerHTML = '<p class="empty">No users found.</p>';
      return;
    }

    box.innerHTML = `
      <table class="admin-table">
        <thead>
          <tr>
            <th>User / Email</th>
            <th>Credits</th>
            <th>Questions</th>
            <th>Paid Orders</th>
            <th>Total Spend</th>
            <th>Joined</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          ${users.map((u) => `
            <tr data-id="${u.id}">
              <td>
                <b>${esc(u.name || '—')}</b><br>
                <span class="muted">${esc(u.email || u.provider)}</span>
                ${u.blocked ? '<span class="pill st-deleted" style="margin-left:4px;">blocked</span>' : ''}
                ${u.is_admin ? '<span class="pill delivered" style="margin-left:4px;">admin</span>' : ''}
                ${u.blocked && u.blocked_reason ? `<div class="muted" style="font-size:0.78rem;">Reason: ${esc(u.blocked_reason)}</div>` : ''}
              </td>
              <td><b>${u.balance}</b></td>
              <td>${u.questions_count}</td>
              <td>${u.orders_count}</td>
              <td><b>${rupees(u.spent_rupees)}</b></td>
              <td><span class="muted">${esc(u.created_at)}</span></td>
              <td><button class="ghost sm btn-manage" type="button">Manage</button></td>
            </tr>`).join('')}
        </tbody>
      </table>`;

    $$('#users-list tr[data-id]').forEach((row) => {
      row.querySelector('.btn-manage').onclick = () => openUserModal(Number(row.dataset.id));
    });
  } catch (e) {
    box.innerHTML = `<p class="error">${esc(e.message)}</p>`;
  }
}

/* ---- the user detail panel ---- */

function closeUserModal() {
  $('#user-modal').hidden = true;
  document.body.classList.remove('modal-open');
  if (umLastFocus && umLastFocus.focus) umLastFocus.focus();
}

async function openUserModal(id) {
  umLastFocus = document.activeElement;
  $('#user-modal').hidden = false;
  document.body.classList.add('modal-open');
  $('#um-body').innerHTML = '<p class="empty">Loading…</p>';
  $('#user-modal .amodal').focus();
  await refreshUserModal(id);
}

async function refreshUserModal(id) {
  try {
    const d = await api(`/api/admin/users/${id}`);
    if (!umProducts) umProducts = (await api('/api/products')).products || [];
    renderUserModal(d);
  } catch (e) {
    $('#um-body').innerHTML = `<p class="error">${esc(e.message)}</p>`;
  }
}

const LEDGER_KIND = {
  signup_bonus: 'sign-up gift', purchase: 'purchase', question: 'question asked',
  refund: 'refund', admin_adjust: 'admin',
};

function renderUserModal(d) {
  const u = d.user;
  const flash = umFlash; umFlash = '';

  const grantSection = `
    <section class="um-sec">
      <h4>Give something</h4>
      <div class="crow">
        <div class="field">
          <label for="um-action">What</label>
          <select id="um-action">
            <option value="credits">Give question credits</option>
            <option value="product">Give a product free (complimentary)</option>
            <option value="deduct">Remove credits (correct a mistake)</option>
          </select>
        </div>
        <div class="field" id="um-credits-row">
          <label for="um-amount">How many</label>
          <input id="um-amount" type="number" min="1" max="1000" value="5" inputmode="numeric" />
        </div>
        <div class="field" id="um-product-row" hidden>
          <label for="um-sku">Product</label>
          <select id="um-sku">${(umProducts || []).map((p) =>
            `<option value="${esc(p.sku)}">${esc(p.title)}</option>`).join('')}</select>
        </div>
      </div>
      <div class="field">
        <label for="um-note">Why <span class="opt">required &mdash; kept on the record</span></label>
        <input id="um-note" maxlength="200" placeholder="e.g. Compensation for the frozen chat on 19 Sep" />
      </div>
      <button type="button" class="primary sm" id="um-grant">Apply</button>
      <p class="pane-help" id="um-grant-hint" style="margin:8px 0 0;">
        A free product is recorded as a paid ₹0 order, so a kundali goes into the Kundali Queue and a report unlocks &mdash;
        but it is never counted as a sale.</p>
      <p class="error" id="um-grant-err" hidden></p>
    </section>`;

  const blockSection = u.is_admin
    ? '<section class="um-sec"><h4>Block</h4><p class="pane-help">Administrators cannot be blocked. Remove their admin access first.</p></section>'
    : u.blocked
      ? `<section class="um-sec"><h4>Blocked</h4>
          <p class="um-blocked">Blocked ${esc(u.blocked_at)}${u.blocked_by ? ` by ${esc(u.blocked_by)}` : ''}.<br>
            <b>Reason:</b> ${esc(u.blocked_reason || '—')}</p>
          <button type="button" class="primary sm" id="um-unblock">Unblock this account</button>
          <p class="error" id="um-block-err" hidden></p></section>`
      : `<section class="um-sec"><h4>Block</h4>
          <div class="field">
            <label for="um-reason">Reason <span class="opt">required &mdash; kept on the account</span></label>
            <input id="um-reason" maxlength="200" placeholder="e.g. Abusive messages to support" />
          </div>
          <button type="button" class="danger sm" id="um-block">Block this account</button>
          <p class="pane-help" style="margin:8px 0 0;">They are signed out and cannot sign in, ask questions or buy until you unblock them.
            Their purchases and saved charts are kept.</p>
          <p class="error" id="um-block-err" hidden></p></section>`;

  const ledger = d.ledger.length
    ? `<table class="admin-table"><thead><tr><th>When</th><th>Change</th><th>Type</th><th>Note</th></tr></thead><tbody>${
      d.ledger.map((e) => `<tr><td><span class="muted">${esc(e.at)}</span></td>
        <td><b style="color:${e.delta < 0 ? '#f0708c' : '#7ddba0'}">${e.delta > 0 ? '+' : ''}${e.delta}</b></td>
        <td>${esc(LEDGER_KIND[e.kind] || e.kind)}</td><td>${esc(e.note)}</td></tr>`).join('')}</tbody></table>`
    : '<p class="empty">No credit history.</p>';

  const orders = d.orders.length
    ? `<table class="admin-table"><thead><tr><th>#</th><th>Item</th><th>Paid</th><th>Status</th><th>When</th></tr></thead><tbody>${
      d.orders.map((o) => `<tr><td>${o.id}</td><td>${esc(o.title)}
        ${o.provider === 'comp' ? ' <span class="pill st-scheduled">complimentary</span>'
          : o.provider === 'manual' ? ' <span class="pill off">manual</span>' : ''}</td>
        <td>${rupees(o.amount)}</td><td><span class="pill ${esc(o.status)}">${esc(o.status.replace('_', ' '))}</span></td>
        <td><span class="muted">${esc(o.at)}</span></td></tr>`).join('')}</tbody></table>`
    : '<p class="empty">No orders.</p>';

  const fb = d.feedback.length
    ? d.feedback.map((f) => `<div class="um-fb"><span class="muted">${esc(f.at)} &middot; ${esc(f.category)}
        ${f.rating ? ` &middot; ${'★'.repeat(f.rating)}` : ''} &middot; ${esc(f.status)}</span><br>${esc(f.message)}</div>`).join('')
    : '<p class="empty">No feedback sent.</p>';

  $('#um-body').innerHTML = `
    <h3 id="um-title" style="margin:0 0 4px;">${esc(u.name || u.email || 'User')}
      ${u.blocked ? '<span class="pill st-deleted">blocked</span>' : ''}
      ${u.is_admin ? '<span class="pill delivered">admin</span>' : ''}</h3>
    <p class="pane-help" style="margin:0 0 14px;">${esc(u.email || '—')}${u.phone ? ` &middot; ${esc(u.phone)}` : ''}
      &middot; ${esc(u.provider || '—')} &middot; joined ${esc(u.created_at)} &middot; last seen ${esc(u.last_seen_at)}</p>
    ${flash ? `<p class="um-flash" role="status">${esc(flash)}</p>` : ''}
    <div class="um-stats">
      <div><b>${d.balance}</b><span>credits</span></div>
      <div><b>${d.questions_count}</b><span>questions asked</span></div>
      <div><b>${d.births_count}</b><span>charts saved</span></div>
      <div><b>${d.orders.length}</b><span>orders</span></div>
    </div>
    ${grantSection}
    ${blockSection}
    <section class="um-sec"><h4>Credit history</h4><div class="table-wrap">${ledger}</div></section>
    <section class="um-sec"><h4>Orders</h4><div class="table-wrap">${orders}</div></section>
    <section class="um-sec"><h4>Feedback sent</h4>${fb}</section>`;

  /* ---- give / remove ---- */
  const action = $('#um-action');
  action.onchange = () => {
    const isProduct = action.value === 'product';
    $('#um-credits-row').hidden = isProduct;
    $('#um-product-row').hidden = !isProduct;
    $('#um-grant').textContent = action.value === 'deduct' ? 'Remove credits' : 'Apply';
  };
  $('#um-grant').onclick = async (ev) => {
    const btn = ev.currentTarget, err = $('#um-grant-err');
    err.hidden = true;
    const note = $('#um-note').value.trim();
    const fail = (m) => { err.textContent = m; err.hidden = false; };
    if (note.length < 3) return fail('Add a short note saying why — it is kept on the record.');

    const who = u.email || u.name || `user ${u.id}`;
    let label, path, payload;
    if (action.value === 'product') {
      const p = (umProducts || []).find((x) => x.sku === $('#um-sku').value);
      label = `Give "${p ? p.title : $('#um-sku').value}" free to ${who}?`;
      path = `/api/admin/users/${u.id}/grant`;
      payload = { kind: 'product', sku: $('#um-sku').value, note };
    } else {
      const n = Math.abs(parseInt($('#um-amount').value, 10));
      if (!n) return fail('Enter how many credits.');
      if (action.value === 'credits') {
        label = `Give ${n} question credit${n > 1 ? 's' : ''} to ${who}?`;
        path = `/api/admin/users/${u.id}/grant`;
        payload = { kind: 'credits', credits: n, note };
      } else {
        label = `Remove ${n} credit${n > 1 ? 's' : ''} from ${who}?`;
        path = `/api/admin/users/${u.id}/credits`;
        payload = { delta: -n, note };
      }
    }
    if (!confirm(label)) return;

    btn.disabled = true;
    try {
      const res = await api(path, { method: 'POST', body: JSON.stringify(payload) });
      umFlash = action.value === 'product'
        ? `Done — order #${res.order.id} created. Balance is now ${res.new_balance}.`
        : `Done — balance is now ${res.new_balance}.`;
      await refreshUserModal(u.id);
      loadUsers();
      if (action.value === 'product') loadKundalis();
    } catch (e) {
      fail(e.message);
      btn.disabled = false;
    }
  };

  /* ---- block / unblock ---- */
  const setBlocked = async (blocked, reason) => {
    const err = $('#um-block-err');
    err.hidden = true;
    try {
      await api(`/api/admin/users/${u.id}/block`, {
        method: 'POST', body: JSON.stringify({ blocked, reason }),
      });
      umFlash = blocked ? 'Account blocked.' : 'Account unblocked.';
      await refreshUserModal(u.id);
      loadUsers();
    } catch (e) { err.textContent = e.message; err.hidden = false; }
  };
  const blockBtn = $('#um-block');
  if (blockBtn) blockBtn.onclick = () => {
    const reason = $('#um-reason').value.trim();
    const err = $('#um-block-err');
    if (reason.length < 3) { err.textContent = 'Give a reason — it is kept on the account.'; err.hidden = false; return; }
    if (confirm(`Block ${u.email || u.name}? They will be signed out and unable to use the site.`)) setBlocked(true, reason);
  };
  const unblockBtn = $('#um-unblock');
  if (unblockBtn) unblockBtn.onclick = () => {
    if (confirm(`Unblock ${u.email || u.name}?`)) setBlocked(false, '');
  };
}

/* ------------------------------------------------------------ feedback --- */

const FB_FILTERS = [['new', 'New'], ['read', 'Seen'], ['resolved', 'Resolved'], ['all', 'All']];
let fbFilter = 'new';
const FB_CATEGORY = {
  general: 'General', bug: 'Something not working', answers: 'An answer / reading',
  payments: 'Payments / order', idea: 'Idea / request', other: 'Something else',
};

function wireFeedback() {
  const search = $('#fb-search');
  if (search) search.oninput = debounce(() => loadFeedback(), 300);
}

async function loadFeedback() {
  const q = ($('#fb-search')?.value || '').trim();
  try {
    const { items, counts } = await api(
      `/api/admin/feedback?status=${encodeURIComponent(fbFilter)}&q=${encodeURIComponent(q)}`);
    setCount('#c-feedback', counts.new);
    renderFeedbackChips(counts);
    renderFeedbackList(items, q);
  } catch (e) {
    $('#fb-list').innerHTML = `<p class="error">${esc(e.message)}</p>`;
  }
}

function renderFeedbackChips(counts) {
  const box = $('#fb-chips');
  box.innerHTML = FB_FILTERS.map(([key, label]) =>
    `<button type="button" class="chip${key === fbFilter ? ' on' : ''}" data-f="${key}"
      aria-pressed="${key === fbFilter}">${esc(label)} <span class="n">${counts[key] ?? 0}</span></button>`).join('');
  $$('button', box).forEach((b) => { b.onclick = () => { fbFilter = b.dataset.f; loadFeedback(); }; });
}

function renderFeedbackList(items, q) {
  const box = $('#fb-list');
  if (!items.length) {
    box.innerHTML = q ? '<p class="empty">No feedback matches your search.</p>'
      : fbFilter === 'new' ? '<p class="empty">Nothing new. You are all caught up.</p>'
        : '<p class="empty">Nothing here.</p>';
    return;
  }

  box.innerHTML = items.map((f) => `
    <div class="row" data-id="${f.id}">
      <div class="row-main">
        <div class="row-title">
          ${f.rating ? `<span class="fb-stars" title="${f.rating} of 5">${'★'.repeat(f.rating)}${'☆'.repeat(5 - f.rating)}</span>` : ''}
          <span class="pill off">${esc(FB_CATEGORY[f.category] || f.category)}</span>
          <span class="pill ${f.status === 'new' ? 'st-scheduled' : f.status === 'resolved' ? 'st-live' : 'st-paused'}">${esc(f.status === 'read' ? 'seen' : f.status)}</span>
        </div>
        <div class="fb-msg">${esc(f.message)}</div>
        <div class="row-sub">
          ${esc(f.name || '—')} ${f.email ? `&lt;${esc(f.email)}&gt;` : ''} &middot; ${esc(f.at)}
          ${f.page ? `&middot; from <code>${esc(f.page)}</code>` : ''}
          ${f.allow_contact ? '' : '&middot; <span class="warn">asked not to be contacted</span>'}
          ${f.handled_at ? `<br><span class="muted">handled ${esc(f.handled_at)}</span>` : ''}
        </div>
        <div class="fb-note">
          <input class="note" placeholder="Private note (only you see this)" value="${esc(f.admin_note)}" maxlength="2000" />
          <button type="button" class="ghost sm" data-act="note">Save note</button>
          <span class="muted fb-saved" hidden>saved</span>
        </div>
      </div>
      <div class="row-act">
        ${f.status === 'new' ? '<button class="ghost sm" data-act="read" type="button">Mark seen</button>' : ''}
        ${f.status !== 'resolved' ? '<button class="primary sm" data-act="resolved" type="button">Resolve</button>'
          : '<button class="ghost sm" data-act="new" type="button">Reopen</button>'}
        ${f.email && f.allow_contact
          ? `<a class="ghost sm as-link" href="mailto:${esc(f.email)}?subject=${encodeURIComponent('Your Divine Astro feedback')}">Reply</a>` : ''}
        <button class="ghost sm" data-act="user" type="button">User</button>
      </div>
    </div>`).join('');

  $$('#fb-list .row').forEach((row) => {
    const id = Number(row.dataset.id);
    const f = items.find((x) => x.id === id);
    const patch = (body) => api(`/api/admin/feedback/${id}`, { method: 'PATCH', body: JSON.stringify(body) });
    const on = (act, fn) => {
      const b = row.querySelector(`[data-act="${act}"]`);
      if (b) b.onclick = async () => {
        b.disabled = true;
        try { await fn(); } catch (e) { alert(e.message); }
        b.disabled = false;
      };
    };
    for (const s of ['read', 'resolved', 'new']) {
      on(s, async () => { await patch({ status: s }); await loadFeedback(); });
    }
    on('note', async () => {
      await patch({ admin_note: row.querySelector('.note').value });
      const ok = row.querySelector('.fb-saved');
      ok.hidden = false;
      setTimeout(() => { ok.hidden = true; }, 1500);
    });
    on('user', async () => openUserModal(f.user_id));
  });
}

/* ----------------------------------------------------------- questions --- */

function wireQuestions() {
  const search = $('#question-search');
  if (search) search.oninput = debounce(() => loadQuestions(), 300);
}

async function loadQuestions() {
  const box = $('#questions-list');
  const q = ($('#question-search')?.value || '').trim();
  try {
    const { questions } = await api(`/api/admin/questions?q=${encodeURIComponent(q)}`);
    if (!questions || !questions.length) {
      box.innerHTML = '<p class="empty">No questions logged yet.</p>';
      return;
    }

    box.innerHTML = questions.map((item) => `
      <div class="row">
        <div class="row-main">
          <div class="row-title">
            <b>${esc(item.question)}</b>
            ${item.verdict ? `<span class="pill delivered" style="margin-left:6px;">${esc(item.verdict)}</span>` : ''}
            <span class="pill off" style="margin-left:4px;">${esc(item.language.toUpperCase())}</span>
          </div>
          <div class="row-sub">
            <span class="muted">${esc(item.user_email)} &middot; ${esc(item.asked_at)} &middot; Topic: ${esc(item.topic || 'general')}</span>
            <p style="margin:6px 0 0;font-size:0.84rem;color:rgba(255,255,255,0.85);">${esc(item.answer_preview)}</p>
          </div>
        </div>
      </div>`).join('');
  } catch (e) {
    box.innerHTML = `<p class="error">${esc(e.message)}</p>`;
  }
}

/* -------------------------------------------------------------- health --- */

async function loadHealth() {
  const box = $('#health-grid');
  try {
    const health = await api('/api/admin/system-health');
    box.innerHTML = `
      <div class="health-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <b>Database</b>
          <span class="health-status-badge ${health.database.ok ? 'ok' : 'err'}">${health.database.ok ? 'Online' : 'Error'}</span>
        </div>
        <div class="muted" style="font-size:0.82rem;">Engine: ${esc(health.database.driver)}</div>
      </div>
      <div class="health-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <b>Vedic Ephemeris</b>
          <span class="health-status-badge ${health.ephemeris.ok ? 'ok' : 'err'}">${health.ephemeris.ok ? 'Active' : 'Offline'}</span>
        </div>
        <div class="muted" style="font-size:0.82rem;">${esc(health.ephemeris.engine)}</div>
      </div>
      <div class="health-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <b>LLM Intelligence</b>
          <span class="health-status-badge ${health.llm.ok ? 'ok' : 'warn'}">${health.llm.ok ? 'Configured' : 'Missing Key'}</span>
        </div>
        <div class="muted" style="font-size:0.82rem;">Provider: ${esc(health.llm.provider)}</div>
      </div>
      <div class="health-card">
        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
          <b>Payment Gateway</b>
          <span class="health-status-badge ${health.gateways.live ? 'ok' : 'warn'}">${esc(health.gateways.provider)} (${health.gateways.mode})</span>
        </div>
        <div class="muted" style="font-size:0.82rem;">Currencies: INR / UPI</div>
      </div>`;
  } catch (e) {
    box.innerHTML = `<p class="error">${esc(e.message)}</p>`;
  }
}

/* --------------------------------------------------------- UPI queue ----- */

async function loadUpi() {
  const box = $('#upi-list');
  const { pending } = await api('/api/admin/upi/pending');
  setCount('#c-upi', pending.length);

  if (!pending.length) {
    box.innerHTML = '<p class="empty">Nothing waiting. Claimed payments appear here.</p>';
    return;
  }

  box.innerHTML = pending.map((o) => `
    <div class="row" data-id="${o.id}">
      <div class="row-main">
        <div class="row-title">${esc(o.title)} &middot; <b>${rupees(o.expected_amount)}</b></div>
        <div class="row-sub">
          ${esc(o.buyer_name || '')} &lt;${esc(o.buyer_email)}&gt;<br />
          Reference <code>${esc(o.reference || '—')}</code> &middot;
          UTR ends in <code class="utr">${esc(o.utr_last5 || '—')}</code><br />
          <span class="muted">submitted ${esc(o.submitted_at || '—')}</span>
          ${o.utr_ambiguous ? `<br /><span class="warn">⚠ another pending order ends in the same 5 characters — check the amount and buyer against the bank statement before approving.</span>` : ''}
        </div>
      </div>
      <div class="row-act">
        <input class="note" placeholder="note (optional)" />
        <button class="primary sm" data-act="approve">Approve &amp; grant</button>
        <button class="danger sm" data-act="reject">Reject</button>
      </div>
    </div>`).join('');

  $$('#upi-list .row').forEach((row) => {
    row.querySelectorAll('button[data-act]').forEach((btn) => {
      btn.onclick = async () => {
        const id = Number(row.dataset.id);
        const approve = btn.dataset.act === 'approve';
        const note = row.querySelector('.note').value;
        const o = pending.find((x) => x.id === id);
        // Approving is what grants the credits, so make it a deliberate click.
        if (approve && o && !confirm(
          `Approve ${rupees(o.expected_amount)} from ${o.buyer_email || 'this buyer'} ` +
          `(UTR ends in ${o.utr_last5 || '—'})?\n\nOnly do this if that exact amount is in ` +
          'your bank / UPI app. It grants the credits straight away.')) return;
        btn.disabled = true;
        try {
          // One endpoint decides both ways: /verify takes approve true|false.
          // (This used to POST to /upi/approve and /upi/reject, which do not exist.)
          const res = await api('/api/admin/upi/verify', {
            method: 'POST',
            body: JSON.stringify({ order_id: id, approve, note }),
          });
          if (approve && res && res.granted === false) {
            alert(res.message || 'This order was already approved earlier; nothing more was granted.');
          }
          await loadUpi();
          await loadMetrics();
        } catch (e) {
          alert(e.message);
          btn.disabled = false;
        }
      };
    });
  });
}

/* ------------------------------------------------------------- traffic --- */

// Everything below builds DOM with textContent / setAttribute — never innerHTML.
// Source names, hosts and campaign tags arrive from outside (referrers, UTM
// parameters), so they are untrusted text.

const SVG_NS = 'http://www.w3.org/2000/svg';
let trDays = 30;
let trData = null;

const fmt = (n) => Number(n || 0).toLocaleString('en-IN');
// A share can't exceed 100%. A sign-up rate can (more sign-ups than TRACKED visitors, e.g. visitors
// on Do-Not-Track) — say so plainly instead of printing a meaningless 575%.
const pct = (x) => (x == null ? '—' : x > 1 ? '>100%' : `${(x * 100).toFixed(1)}%`);

const SOURCE_NAMES = {
  direct: 'Direct / unknown', unknown: 'Unknown / before tracking', google: 'Google', bing: 'Bing',
  duckduckgo: 'DuckDuckGo', yahoo: 'Yahoo', yandex: 'Yandex', ecosia: 'Ecosia', facebook: 'Facebook',
  instagram: 'Instagram', x: 'X (Twitter)', youtube: 'YouTube', whatsapp: 'WhatsApp',
  telegram: 'Telegram', linkedin: 'LinkedIn', reddit: 'Reddit', pinterest: 'Pinterest', quora: 'Quora',
  chatgpt: 'ChatGPT', perplexity: 'Perplexity', gemini: 'Gemini', email: 'Email', other: 'Other',
  dev: 'Dev sign-in', microsoft: 'Microsoft', apple: 'Apple', mobile: 'Mobile', tablet: 'Tablet',
  desktop: 'Desktop',
};
const niceLabel = (k) => SOURCE_NAMES[k] || k;

function svgEl(tag, attrs = {}, text) {
  const e = document.createElementNS(SVG_NS, tag);
  Object.entries(attrs).forEach(([k, v]) => e.setAttribute(k, v));
  if (text != null) e.textContent = text;
  return e;
}

function el(tag, cls, text) {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text != null) e.textContent = text;
  return e;
}

/* ---- stat tiles: one headline number each, not a chart ---- */

function tile(label, value, sub, dot) {
  const t = el('div', 'tile');
  const l = el('div', 't-label');
  if (dot) { const d = el('span', `dot dot-${dot}`); d.setAttribute('aria-hidden', 'true'); l.appendChild(d); }
  l.appendChild(document.createTextNode(label));
  t.append(l, el('div', 't-value', value), el('div', 't-sub', sub));
  return t;
}

/* ---- daily columns (one measure per chart, one axis) ---- */

function drawColumns(host, days, o) {
  host.textContent = '';
  const W = Math.max(280, host.clientWidth || 560), H = 232;
  const m = { l: 44, r: 10, t: 24, b: 30 };
  const pw = W - m.l - m.r, ph = H - m.t - m.b;
  const vals = days.map((d) => d[o.key]);
  const peak = Math.max(0, ...vals);

  // Round the top of the axis to a clean number, in whole steps (these are counts).
  const raw = Math.max(1, Math.ceil(peak / 4));
  const mag = 10 ** Math.floor(Math.log10(raw));
  const step = [1, 2, 5, 10].map((k) => k * mag).find((v) => v >= raw);
  const top = step * 4;
  const y = (v) => m.t + ph - (v / top) * ph;

  const svg = svgEl('svg', {
    viewBox: `0 0 ${W} ${H}`, width: W, height: H, role: 'img',
    'aria-label': `${o.title}, last ${days.length} days. Peak ${peak}. A table of the numbers is below.`,
  });
  for (let i = 0; i <= 4; i++) {
    const yy = y(step * i);
    svg.appendChild(svgEl('line', { x1: m.l, x2: W - m.r, y1: yy, y2: yy, class: i === 0 ? 'viz-axis' : 'viz-grid' }));
    svg.appendChild(svgEl('text', { x: m.l - 8, y: yy + 4, 'text-anchor': 'end' }, fmt(step * i)));
  }

  const slot = pw / days.length;
  // <= 24px thick with 2px of air between; when 90 days are squeezed into a small card the
  // gap drops to 1px so the bars stay a legible width instead of hairlines.
  const gap = slot >= 8 ? 2 : 1;
  const bw = Math.max(2, Math.min(24, slot - gap));
  const every = Math.max(1, Math.ceil(64 / slot));           // date labels no closer than ~64px
  const tip = el('div', 'viz-tip');
  tip.hidden = true;
  let peakLabelled = false;
  const hits = [];
  const showers = [], hiders = [];

  days.forEach((d, i) => {
    const v = d[o.key], cx = m.l + slot * i + slot / 2, h = (v / top) * ph;
    let bar = null;
    if (v > 0) {
      const x = cx - bw / 2, r = Math.min(4, bw / 2, h), yy = m.t + ph - h;
      // 4px-rounded data end, square where it meets the baseline.
      bar = svgEl('path', {
        d: `M${x},${m.t + ph} V${yy + r} Q${x},${yy} ${x + r},${yy} H${x + bw - r} Q${x + bw},${yy} ${x + bw},${yy + r} V${m.t + ph} Z`,
        class: `viz-bar ${o.color}`,
      });
      svg.appendChild(bar);
      if (!peakLabelled && v === peak) {                     // label only the peak, nothing else
        peakLabelled = true;
        svg.appendChild(svgEl('text', { x: cx, y: yy - 7, 'text-anchor': 'middle', class: 'viz-peak' }, fmt(v)));
      }
    }
    if ((days.length - 1 - i) % every === 0) {
      svg.appendChild(svgEl('text', { x: cx, y: H - 9, 'text-anchor': 'middle' }, d.label));
    }

    const noun = v === 1 ? o.one : o.many;
    // The hit target is the whole day's column, far bigger than the bar itself.
    const hit = svgEl('rect', {
      x: m.l + slot * i, y: m.t, width: slot, height: ph, class: 'viz-hit', tabindex: '0',
      'aria-label': `${d.label}: ${fmt(v)} ${noun}. ${o.detail(d)}`,
    });
    const show = () => {
      tip.textContent = '';
      tip.append(el('b', null, `${fmt(v)} ${noun}`), el('span', null, `${d.label} · ${o.detail(d)}`));
      tip.hidden = false;
      tip.style.left = `${Math.min(Math.max(cx, 70), W - 70)}px`;
      tip.style.top = `${Math.max(y(v), m.t + 6)}px`;
      if (bar) bar.classList.add('hot');
    };
    const hide = () => { tip.hidden = true; if (bar) bar.classList.remove('hot'); };
    // Keyboard: each day's column is focusable and shows the same tooltip as a pointer.
    hit.addEventListener('focus', show);
    hit.addEventListener('blur', hide);
    hits.push(hit);
    showers.push(show);
    hiders.push(hide);
  });
  hits.forEach((h) => svg.appendChild(h));                   // above every bar

  // Pointer/touch: ONE overlay that snaps to the nearest day, so the reader aims at
  // a date rather than at a column that may be only a few pixels wide on a phone.
  const cover = svgEl('rect', { x: m.l, y: m.t, width: pw, height: ph, class: 'viz-cover' });
  let cur = -1;
  const track = (ev) => {
    const box = svg.getBoundingClientRect();
    const x = (ev.clientX - box.left) * (W / box.width) - m.l;
    const i = Math.max(0, Math.min(days.length - 1, Math.floor(x / slot)));
    if (i !== cur) { if (cur >= 0) hiders[cur](); cur = i; showers[i](); }
  };
  ['pointerenter', 'pointermove', 'pointerdown'].forEach((ev) => cover.addEventListener(ev, track));
  cover.addEventListener('pointerleave', () => { if (cur >= 0) hiders[cur](); cur = -1; });
  svg.appendChild(cover);

  if (peak === 0) {
    svg.appendChild(svgEl('text', { x: m.l + pw / 2, y: m.t + ph / 2, 'text-anchor': 'middle', class: 'viz-empty' },
      'No data in this period yet'));
  }
  host.append(svg, tip);
}

/* ---- ranked horizontal bars for sources, pages, devices ---- */

function barList(host, rows, o = {}) {
  host.textContent = '';
  if (!rows || !rows.length) { host.appendChild(el('p', 'empty', 'Nothing recorded yet.')); return; }
  const max = Math.max(...rows.map((r) => r.count), 1);
  const ul = el('ul', `bl${o.color === 'orange' ? ' orange' : ''}`);
  rows.forEach((r) => {
    const li = el('li');
    const top = el('div', 'bl-top');
    top.append(
      el('span', o.mono ? 'bl-label mono' : 'bl-label', o.raw ? r.label : niceLabel(r.label)),
      el('span', 'bl-val', o.value ? o.value(r) : `${fmt(r.count)} · ${pct(r.share)}`));
    const track = el('div', 'bl-track');
    const fill = el('div', 'bl-fill');
    fill.style.width = `${Math.max(2, (r.count / max) * 100).toFixed(1)}%`;
    track.appendChild(fill);
    li.append(top, track);
    ul.appendChild(li);
  });
  host.appendChild(ul);
}

function renderDailyTable(days) {
  const box = $('#tr-table');
  box.textContent = '';
  const t = el('table', 'admin-table');
  const head = el('tr');
  ['Date', 'Visitors', 'Page views', 'New users'].forEach((h) => head.appendChild(el('th', null, h)));
  t.appendChild(el('thead')).appendChild(head);
  const body = el('tbody');
  [...days].reverse().forEach((d) => {
    const tr = el('tr');
    tr.append(el('td', null, d.date), el('td', null, fmt(d.visitors)),
      el('td', null, fmt(d.pageviews)), el('td', null, fmt(d.new_users)));
    body.appendChild(tr);
  });
  t.appendChild(body);
  box.appendChild(t);
}

function renderTraffic(d) {
  const tot = d.totals, w = d.windows;
  const tiles = $('#tr-tiles');
  tiles.textContent = '';
  tiles.append(
    tile('Visitors', fmt(tot.visitors), `today ${fmt(w.today.visitors)}`, 'blue'),
    tile('Page views', fmt(tot.pageviews),
      tot.visitors ? `${(tot.pageviews / tot.visitors).toFixed(1)} per visitor` : 'no visits yet'),
    tile('New users', fmt(tot.new_users), `today ${fmt(w.today.new_users)} · ${fmt(d.users_total)} in all`, 'orange'),
    tile('Sign-up rate', pct(tot.signup_rate),
      d.tracking_since && d.tracking_since > d.range.from
        ? `new users ÷ visitors, since ${d.tracking_since}` : 'new users ÷ visitors'),
    tile('On the site now', fmt(d.live_now), 'in the last 5 minutes'));

  const since = d.tracking_since
    ? `Visit tracking began on ${d.tracking_since}; earlier visits were not recorded (new-user counts go back further, since they come from sign-up dates). `
    : 'No visits have been recorded yet. Load the public site in a private window to see the first one — your own signed-in visits are never counted. ';
  $('#tr-note').textContent = `${since}A visitor is counted once per day, so a multi-day total is a sum of daily visitors. ` +
    'Bots, Do-Not-Track requests and your own visits are excluded; no IP address or browser string is stored. ' +
    'Only full page loads are counted, not clicks inside the app.';

  const days = d.daily;
  const visitorsDetail = (x) => `${fmt(x.pageviews)} page views · ${fmt(x.new_users)} new users`;
  const newDetail = (x) => `${fmt(x.visitors)} visitors`;
  const draw = () => {
    drawColumns($('#chart-visitors'), days,
      { key: 'visitors', color: 'blue', title: 'Visitors per day', one: 'visitor', many: 'visitors', detail: visitorsDetail });
    drawColumns($('#chart-new'), days,
      { key: 'new_users', color: 'orange', title: 'New users per day', one: 'new user', many: 'new users', detail: newDetail });
  };
  draw();
  ['#chart-visitors', '#chart-new'].forEach((s) => { $(s)._redraw = draw; });

  barList($('#bl-sources'), d.sources.filter((r) => r.label !== 'internal'));
  barList($('#bl-signup'), d.signup_sources, { color: 'orange' });
  barList($('#bl-pages'), d.pages, {
    raw: true, mono: true,
    value: (r) => `${fmt(r.count)} views · ${fmt(r.visitors)} visitors`,
  });
  barList($('#bl-devices'), d.devices);
  barList($('#bl-providers'), d.providers, { color: 'orange' });
  barList($('#bl-campaigns'), d.campaigns, { raw: true });
  renderDailyTable(days);
}

function fillOverviewCounters(d) {
  $('#m-vis-today').textContent = fmt(d.windows.today.visitors);
  $('#m-new-today').textContent = fmt(d.windows.today.new_users);
  $('#m-live').textContent = fmt(d.live_now);
}

async function loadTraffic() {
  const root = $('#traffic-root');
  root.classList.add('is-loading');               // hold the frame while refetching — no layout jump
  try {
    trData = await api(`/api/admin/traffic?days=${trDays}`);
    renderTraffic(trData);
    fillOverviewCounters(trData);
  } catch (e) {
    console.error('Failed to load traffic:', e);
    $('#tr-note').textContent = `Could not load traffic: ${e.message}`;
  } finally {
    root.classList.remove('is-loading');
  }
}

function wireTraffic() {
  $$('#tr-range .chip').forEach((b) => {
    b.onclick = () => {
      trDays = Number(b.dataset.days);
      $$('#tr-range .chip').forEach((x) => {
        x.classList.toggle('on', x === b);
        x.setAttribute('aria-pressed', String(x === b));
      });
      loadTraffic();
    };
  });
  // Charts are drawn at their real pixel width, so redraw when the width changes
  // (window resize, or the tab becoming visible for the first time).
  if ('ResizeObserver' in window) {
    let raf = 0;
    const ro = new ResizeObserver(() => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        ['#chart-visitors', '#chart-new'].forEach((s) => { const h = $(s); if (h && h._redraw) h._redraw(); });
      });
    });
    ['#chart-visitors', '#chart-new'].forEach((s) => ro.observe($(s)));
  }
}

/* ------------------------------------------------------ manual order ----- */

const MO_BIRTH_KINDS = new Set(['kundali', 'kundali_book', 'single_question', 'custom']);
let moProducts = {};          // sku -> product, from /api/products
let moPlace = null;           // the city picked from the search list

const moKind = () => ($('#mo-sku').value === 'custom' ? 'custom'
  : (moProducts[$('#mo-sku').value] || {}).kind);

function moSyncProduct(resetAmount) {
  const sku = $('#mo-sku').value;
  const kind = moKind();
  $('#mo-custom').hidden = sku !== 'custom';
  $('#mo-birth').hidden = !MO_BIRTH_KINDS.has(kind);
  $('#mo-birth-opt').textContent =
    kind === 'kundali' || kind === 'kundali_book' ? 'needed for the astrologer' : 'optional';
  // Default the amount to the list price, but never overwrite one typed by hand.
  if (resetAmount) {
    const p = moProducts[sku];
    $('#mo-amount').value = p ? p.rupees : '';
  }
}

function moPickPlace(p) {
  moPlace = p;
  $('#mo-place').value = p.label;
  $('#mo-place-results').hidden = true;
  const picked = $('#mo-place-picked');
  picked.textContent = `✓ ${p.label} · ${p.latitude.toFixed(2)}, ${p.longitude.toFixed(2)} · ${p.timezone}`;
  picked.hidden = false;
}

function wireManual() {
  const form = $('#mo-form');
  let amountTouched = false;

  api('/api/products').then(({ products }) => {
    moProducts = Object.fromEntries((products || []).map((p) => [p.sku, p]));
    $('#mo-sku').innerHTML = (products || [])
      .map((p) => `<option value="${esc(p.sku)}">${esc(p.title)} — ${rupees(p.rupees)}</option>`)
      .join('') + '<option value="custom">Custom / other…</option>';
    moSyncProduct(true);
  }).catch(() => {});

  $('#mo-sku').onchange = () => moSyncProduct(!amountTouched);
  $('#mo-amount').oninput = () => { amountTouched = true; };
  $('#mo-email').oninput = () => { $('#mo-force-wrap').hidden = true; };

  let timer = null;
  $('#mo-place').oninput = () => {
    moPlace = null;
    $('#mo-place-picked').hidden = true;
    const q = $('#mo-place').value.trim();
    clearTimeout(timer);
    const box = $('#mo-place-results');
    if (q.length < 2) { box.hidden = true; return; }
    timer = setTimeout(async () => {
      try {
        const { results } = await api(`/api/places?q=${encodeURIComponent(q)}&limit=8`);
        box.innerHTML = results.length
          ? results.map((p, i) => `<button type="button" data-i="${i}">${esc(p.label)}</button>`).join('')
          : '<span class="muted">No matching city.</span>';
        box.hidden = false;
        $$('button', box).forEach((b) => { b.onclick = () => moPickPlace(results[Number(b.dataset.i)]); });
      } catch { box.hidden = true; }
    }, 250);
  };

  form.onreset = () => {
    // reset fires before the fields clear; defer so the defaults are re-derived
    setTimeout(() => {
      amountTouched = false; moPlace = null;
      $('#mo-place-results').hidden = true;
      $('#mo-place-picked').hidden = true;
      $('#mo-force-wrap').hidden = true;
      $('#mo-error').hidden = true;
      moSyncProduct(true);
    }, 0);
  };

  form.onsubmit = async (ev) => {
    ev.preventDefault();
    const err = $('#mo-error'), ok = $('#mo-ok'), btn = $('button[type=submit]', form);
    err.hidden = ok.hidden = true;

    const email = $('#mo-email').value.trim();
    const phone = $('#mo-phone').value.trim();
    if (!email && !phone) return showErr('Enter the customer’s email or phone number.');
    const amount = Math.round(parseFloat($('#mo-amount').value) * 100);
    if (!Number.isFinite(amount) || amount < 0) return showErr('Enter the amount received.');

    const sku = $('#mo-sku').value;
    const body = {
      email, phone, name: $('#mo-name').value.trim(), sku, amount_paise: amount,
      method: $('#mo-method').value, reference: $('#mo-ref').value.trim(),
      note: $('#mo-note').value.trim(), force: $('#mo-force').checked,
    };
    if (sku === 'custom') {
      body.title = $('#mo-title').value.trim();
      body.credits = Number($('#mo-credits').value || 0);
      if (!body.title) return showErr('Say what was sold.');
    }

    // Birth details ride along only when the section is shown and filled in.
    const date = $('#mo-bdate').value, time = $('#mo-btime').value;
    if (!$('#mo-birth').hidden && (date || time || $('#mo-place').value.trim())) {
      if (!date) return showErr('Enter the date of birth, or clear the birth section.');
      if (!moPlace) return showErr('Pick the birth place from the list so it has coordinates.');
      body.birth = {
        name: $('#mo-bname').value.trim() || body.name, date,
        time: time || '12:00', time_known: Boolean(time),
        gender: $('#mo-bgender').value, place: moPlace.label,
        latitude: moPlace.latitude, longitude: moPlace.longitude,
        timezone: moPlace.timezone,
      };
    }

    btn.disabled = true;               // a double-click must not record twice
    try {
      const r = await api('/api/admin/orders/manual', { method: 'POST', body: JSON.stringify(body) });
      const c = r.customer;
      ok.innerHTML =
        `✓ Order <b>#${r.order.id}</b> recorded &mdash; ${esc(r.order.title)}, ` +
        `${rupees(r.order.amount)}. ${c.created ? 'New account created for' : 'Added to'} ` +
        `<b>${esc(c.email || c.name || 'the customer')}</b>; balance now ${c.credits} question(s).` +
        (r.warnings.length ? `<br /><span class="warn">⚠ ${r.warnings.map(esc).join(' ')}</span>` : '');
      ok.hidden = false;
      form.reset();
      await Promise.all([loadManual(), loadMetrics(), loadKundalis()]);
    } catch (e) {
      showErr(e.message);
      // A refused duplicate is the one error the admin can knowingly override.
      if (e.status === 409 && /identical manual order/.test(e.message)) $('#mo-force-wrap').hidden = false;
    } finally {
      btn.disabled = false;
    }

    function showErr(msg) { err.textContent = msg; err.hidden = false; }
  };
}

async function loadManual() {
  const box = $('#mo-list');
  const { orders } = await api('/api/admin/orders/manual?limit=30');
  if (!orders.length) {
    box.innerHTML = '<p class="empty">No manual orders yet.</p>';
    return;
  }
  box.innerHTML = orders.map((o) => `
    <div class="row">
      <div class="row-main">
        <div class="row-title">#${o.id} &middot; ${esc(o.title)} &middot; <b>${rupees(o.amount)}</b></div>
        <div class="row-sub">
          ${esc(o.customer_name || '')} ${o.customer_email ? `&lt;${esc(o.customer_email)}&gt;` : ''}
          ${o.customer_phone ? `&middot; ${esc(o.customer_phone)}` : ''}<br />
          <span class="muted">${esc(o.note)} &middot; ${esc(o.paid_at || o.created_at)}
          ${o.recorded_by ? `&middot; by ${esc(o.recorded_by)}` : ''}</span>
        </div>
      </div>
      <div class="row-act">
        ${o.fulfilment !== 'not_applicable'
          ? `<span class="pill ${esc(o.fulfilment)}">${esc(o.fulfilment.replace('_', ' '))}</span>` : ''}
        ${o.credits ? `<span class="pill off">+${o.credits} questions</span>` : ''}
      </div>
    </div>`).join('');
}

/* ----------------------------------------------------- kundali queue ----- */

const FULFIL = [
  ['pending', 'Pending'],
  ['in_progress', 'In progress'],
  ['delivered', 'Delivered'],
];

async function loadKundalis() {
  const box = $('#kundali-list');
  const all = $('#k-all').checked;
  const { kundalis } = await api(`/api/admin/kundalis?state=${all ? 'all' : 'open'}`);
  setCount('#c-kundali', kundalis.filter((k) => k.fulfilment === 'pending').length);

  if (!kundalis.length) {
    box.innerHTML = '<p class="empty">No hand-written kundalis in the queue.</p>';
    return;
  }

  box.innerHTML = kundalis.map((o) => {
    const b = o.birth;
    const birth = b
      ? `${esc(b.name || '—')} &middot; ${esc(b.date)} ${esc(b.time_known ? b.time : '(time unknown)')}
         &middot; ${esc(b.place)}`
      : '<span class="warn">No birth details on this order — ask the customer.</span>';
    return `
    <div class="row" data-id="${o.id}">
      <div class="row-main">
        <div class="row-title">
          ${esc(o.title)} &middot; <b>${rupees(o.amount)}</b>
          <span class="pill ${esc(o.fulfilment)}">${esc(o.fulfilment.replace('_', ' '))}</span>
        </div>
        <div class="row-sub">
          ${birth}<br />
          ${esc(o.buyer_name || '')} &lt;${esc(o.buyer_email)}&gt;
          ${o.buyer_phone ? '&middot; ' + esc(o.buyer_phone) : ''}
        </div>
      </div>
      <div class="row-act">
        <input class="note" placeholder="note" value="${esc(o.fulfil_note || '')}" />
        <select class="fstat">
          ${FULFIL.map(([v, l]) =>
            `<option value="${v}"${v === o.fulfilment ? ' selected' : ''}>${l}</option>`).join('')}
        </select>
        <button class="primary sm" data-act="save">Save</button>
      </div>
    </div>`;
  }).join('');

  $$('#kundali-list .row').forEach((row) => {
    row.querySelector('button[data-act="save"]').onclick = async (ev) => {
      ev.target.disabled = true;
      try {
        await api('/api/admin/kundalis/fulfil', {
          method: 'POST',
          body: JSON.stringify({
            order_id: Number(row.dataset.id),
            status: row.querySelector('.fstat').value,
            note: row.querySelector('.note').value,
          }),
        });
        await loadKundalis();
      } catch (e) {
        alert(e.message);
        ev.target.disabled = false;
      }
    };
  });
}

function debounce(fn, wait) {
  let timer = null;
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), wait);
  };
}

boot().catch((e) => showGate('Something went wrong', e.message, false));
