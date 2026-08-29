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
  wireUsers();
  wireQuestions();

  // Load active tab initially and prefetch background queues
  await Promise.all([
    loadMetrics(),
    loadCoupons(),
    loadUpi(),
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
      else if (tab === 'questions') loadQuestions();
      else if (tab === 'health') loadHealth();
      else if (tab === 'upi') loadUpi();
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

function wireCoupons() {
  const form = $('#coupon-form');
  const btnToggle = $('#btn-toggle-coupon-form');
  const btnCancel = $('#btn-cancel-coupon-form');
  const search = $('#coupon-search');

  btnToggle.onclick = () => { form.hidden = !form.hidden; };
  btnCancel.onclick = () => { form.hidden = true; };

  search.oninput = () => renderCouponsList();

  const kind = $('#c-kind');
  kind.onchange = () => {
    $('#c-value-label').textContent = {
      percent: 'Value (%)', flat: 'Value (₹ off)', extra_credits: 'Extra questions',
    }[kind.value];
  };

  api('/api/products').then(({ products }) => {
    $('#c-skus').innerHTML = (products || [])
      .map((p) => `<option value="${esc(p.sku)}">${esc(p.title)} — ${rupees(p.rupees)}</option>`)
      .join('');
  }).catch(() => {});

  form.onsubmit = async (ev) => {
    ev.preventDefault();
    const err = $('#coupon-error');
    err.hidden = true;

    const skus = $$('#c-skus option:checked').map((o) => o.value);
    const until = $('#c-until').value;
    const body = {
      code: $('#c-code').value,
      kind: $('#c-kind').value,
      value: Number($('#c-value').value),
      applies_to: skus.length ? skus.join(',') : 'all',
      max_redemptions: $('#c-max').value ? Number($('#c-max').value) : null,
      max_per_user: Number($('#c-per').value || 1),
      expires_at: until ? `${until}T23:59:59` : null,
    };

    try {
      await api('/api/admin/coupons', { method: 'POST', body: JSON.stringify(body) });
      form.reset();
      form.hidden = true;
      kind.onchange();
      await loadCoupons();
    } catch (e) {
      err.textContent = e.message;
      err.hidden = false;
    }
  };
}

function describe(c) {
  if (c.kind === 'percent') return `${c.value}% off`;
  if (c.kind === 'flat') return `${rupees(c.value / 100)} off`;
  return `+${c.value} free questions`;
}

async function loadCoupons() {
  try {
    const { coupons } = await api('/api/admin/coupons');
    allCoupons = coupons || [];
    setCount('#c-coupons', allCoupons.filter((c) => c.active).length);
    renderCouponsList();
  } catch (e) {
    console.error('Failed to load coupons:', e);
  }
}

function renderCouponsList() {
  const box = $('#coupon-list');
  const query = ($('#coupon-search')?.value || '').trim().toLowerCase();

  const filtered = allCoupons.filter((c) => 
    !query || c.code.toLowerCase().includes(query) || (c.applies_to && c.applies_to.toLowerCase().includes(query))
  );

  if (!filtered.length) {
    box.innerHTML = query
      ? '<p class="empty">No coupons match your filter.</p>'
      : '<p class="empty">No coupons created yet. Click "+ Create New Coupon" above.</p>';
    return;
  }

  box.innerHTML = filtered.map((c) => `
    <div class="row" data-id="${c.id}">
      <div class="row-main">
        <div class="row-title">
          <code class="code">${esc(c.code)}</code>
          <button class="ghost sm btn-copy" data-code="${esc(c.code)}" title="Copy code" style="padding:2px 7px;font-size:0.75rem;margin-left:6px;">&#128203; Copy</button>
          <span class="pill ${c.active ? 'delivered' : 'off'}" style="margin-left:6px;">${c.active ? 'live' : 'paused'}</span>
          &middot; <b>${esc(describe(c))}</b>
        </div>
        <div class="row-sub">
          Target: <code>${esc(c.applies_to === 'all' ? 'All Products' : c.applies_to)}</code>
          &middot; Redemptions: <b>${c.redemptions}${c.max_redemptions ? ` / ${c.max_redemptions}` : ' (unlimited)'}</b>
          &middot; Max per user: ${c.max_per_user || '∞'}
          ${c.expires_at ? `&middot; Expires: <b>${esc(c.expires_at.slice(0, 10))}</b>` : '&middot; No expiry'}
          ${c.total_discount_paise ? `<br><span class="muted">Total customer savings given: ${rupees(c.total_discount_paise / 100)}</span>` : ''}
        </div>
      </div>
      <div class="row-act">
        <button class="ghost sm" data-act="toggle">${c.active ? 'Pause' : 'Resume'}</button>
        <button class="danger sm" data-act="delete">Delete</button>
      </div>
    </div>`).join('');

  $$('#coupon-list .row').forEach((row) => {
    const id = Number(row.dataset.id);
    const c = allCoupons.find((x) => x.id === id);

    row.querySelector('.btn-copy').onclick = (ev) => {
      const code = ev.currentTarget.dataset.code;
      navigator.clipboard.writeText(code).then(() => {
        ev.currentTarget.textContent = 'Copied!';
        setTimeout(() => { ev.currentTarget.textContent = '📋 Copy'; }, 1500);
      });
    };

    row.querySelector('[data-act="toggle"]').onclick = async () => {
      await api(`/api/admin/coupons/${id}`, {
        method: 'PATCH', body: JSON.stringify({ active: !c.active }),
      });
      await loadCoupons();
    };

    row.querySelector('[data-act="delete"]').onclick = async () => {
      if (!confirm(`Delete ${c.code}? Coupons that have been used are paused instead, so redemption records survive.`)) return;
      try {
        await api(`/api/admin/coupons/${id}`, { method: 'DELETE' });
      } catch (e) { alert(e.message); }
      await loadCoupons();
    };
  });
}

/* --------------------------------------------------------------- users --- */

function wireUsers() {
  const search = $('#user-search');
  if (search) search.oninput = debounce(() => loadUsers(), 300);
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
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          ${users.map((u) => `
            <tr data-id="${u.id}" data-email="${esc(u.email)}">
              <td>
                <b>${esc(u.name || '—')}</b><br>
                <span class="muted">${esc(u.email || u.provider)}</span>
                ${u.blocked ? '<span class="pill off" style="margin-left:4px;">blocked</span>' : ''}
                ${u.is_admin ? '<span class="pill delivered" style="margin-left:4px;">admin</span>' : ''}
              </td>
              <td><b>${u.balance}</b></td>
              <td>${u.questions_count}</td>
              <td>${u.orders_count}</td>
              <td><b>${rupees(u.spent_rupees)}</b></td>
              <td><span class="muted">${esc(u.created_at)}</span></td>
              <td>
                <div style="display:flex;gap:6px;flex-wrap:wrap;">
                  <button class="ghost sm btn-credit" title="Gift or adjust credits">Adjust Credits</button>
                  ${!u.is_admin ? `<button class="danger sm btn-block">${u.blocked ? 'Unblock' : 'Block'}</button>` : ''}
                </div>
              </td>
            </tr>`).join('')}
        </tbody>
      </table>`;

    $$('#users-list tr[data-id]').forEach((row) => {
      const id = Number(row.dataset.id);
      const email = row.dataset.email;

      row.querySelector('.btn-credit').onclick = async () => {
        const deltaStr = prompt(`Adjust question credits for ${email} (enter positive number to grant, negative to deduct):`, '5');
        if (deltaStr === null) return;
        const delta = parseInt(deltaStr, 10);
        if (isNaN(delta) || delta === 0) return alert('Please enter a valid non-zero number.');
        const note = prompt('Reason / audit note (optional):', 'Customer support grant') || '';
        try {
          const res = await api(`/api/admin/users/${id}/credits`, {
            method: 'POST',
            body: JSON.stringify({ delta, note }),
          });
          alert(`Credits updated! New balance: ${res.new_balance}`);
          await loadUsers();
        } catch (e) { alert(e.message); }
      };

      const blockBtn = row.querySelector('.btn-block');
      if (blockBtn) {
        blockBtn.onclick = async () => {
          const isBlocked = blockBtn.textContent === 'Unblock';
          if (!confirm(`${isBlocked ? 'Unblock' : 'Block'} account for ${email}?`)) return;
          try {
            await api(`/api/admin/users/${id}/block`, {
              method: 'POST',
              body: JSON.stringify({ blocked: !isBlocked }),
            });
            await loadUsers();
          } catch (e) { alert(e.message); }
        };
      }
    });
  } catch (e) {
    box.innerHTML = `<p class="error">${esc(e.message)}</p>`;
  }
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
          claimed UTR <code class="utr">${esc(o.utr)}</code><br />
          <span class="muted">submitted ${esc(o.submitted_at || '—')}</span>
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
        const act = btn.dataset.act;
        const note = row.querySelector('.note').value;
        btn.disabled = true;
        try {
          await api(`/api/admin/upi/${act}`, {
            method: 'POST',
            body: JSON.stringify({ order_id: id, note }),
          });
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

/* ----------------------------------------------------- kundali queue ----- */

const FULFIL = [
  ['pending', 'Pending'],
  ['in_progress', 'In progress'],
  ['delivered', 'Delivered'],
];

async function loadKundalis() {
  const box = $('#kundali-list');
  const all = $('#k-all').checked;
  const { kundalis } = await api(`/api/admin/kundalis?all=${all ? 1 : 0}`);
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
