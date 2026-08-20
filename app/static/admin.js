/* Admin panel.
 *
 * Every endpoint it touches is already gated server-side by the `admin`
 * dependency, so this file is convenience, not security: hiding a button here
 * protects nobody. The gate below exists only to explain to a signed-out or
 * non-admin visitor what they are looking at.
 */
'use strict';

const $ = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

const esc = (s) => String(s ?? '').replace(/[&<>"']/g,
  (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

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

/* ---------------------------------------------------------------- gate --- */

async function boot() {
  let me = null;
  try {
    me = await api('/api/me');
  } catch (e) {
    if (e.status !== 401) throw e;
  }

  const user = me && me.user;
  // Operator-facing, but still a person: say what to do, not which environment
  // variable to grep for.
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
  await Promise.all([loadUpi(), loadKundalis(), loadCoupons()]);
}

async function showGate(title, msg, offerSignIn) {
  $('#gate').hidden = false;
  $('#gate-title').textContent = title;
  $('#gate-msg').textContent = msg;
  if (!offerSignIn) return;

  const box = $('#gate-actions');
  try {
    const { providers, dev_login } = await api('/api/auth/providers');
    // Each provider is {key, label} — not a bare string.
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
  } catch (e) {
    // Say so rather than rendering an empty box — a silent catch here once hid
    // a bug that left the page with no way to sign in at all.
    const p = document.createElement('p');
    p.className = 'error';
    p.textContent = `Could not load sign-in options: ${e.message}`;
    box.appendChild(p);
  }
}

function wireTabs() {
  $$('.atab').forEach((b) => {
    b.onclick = () => {
      $$('.atab').forEach((x) => x.classList.toggle('active', x === b));
      $$('.apane').forEach((p) => p.classList.toggle('active', p.id === `pane-${b.dataset.tab}`));
    };
  });
}

const rupees = (n) => `₹${Number(n).toLocaleString('en-IN')}`;

function setCount(id, n) {
  const el = $(id);
  el.textContent = n ? String(n) : '';
  el.classList.toggle('has', !!n);
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
        const approve = btn.dataset.act === 'approve';
        const amount = row.querySelector('b').textContent;
        if (!confirm(approve
          ? `Approve ${amount}? Only do this if you can see it in your bank statement. `
            + 'This grants the credits immediately.'
          : 'Reject this claim? No credits will be granted.')) return;

        row.querySelectorAll('button').forEach((b) => (b.disabled = true));
        try {
          await api('/api/admin/upi/verify', {
            method: 'POST',
            body: JSON.stringify({
              order_id: Number(row.dataset.id),
              approve,
              note: row.querySelector('.note').value,
            }),
          });
          await loadUpi();
        } catch (e) {
          alert(e.message);
          row.querySelectorAll('button').forEach((b) => (b.disabled = false));
        }
      };
    });
  });
}

/* ---------------------------------------------------- kundali queue ------ */

const FULFIL = [
  ['pending', 'Not started'],
  ['in_progress', 'In progress'],
  ['delivered', 'Delivered'],
];

async function loadKundalis() {
  const box = $('#kundali-list');
  const state = $('#k-all').checked ? 'all' : 'open';
  const { kundalis } = await api(`/api/admin/kundalis?state=${state}`);
  setCount('#c-kundali', kundalis.filter((k) => k.fulfilment !== 'delivered').length);

  if (!kundalis.length) {
    box.innerHTML = '<p class="empty">No paid kundali orders in this view.</p>';
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

/* ------------------------------------------------------------ coupons --- */

function wireCoupons() {
  $('#k-all').onchange = loadKundalis;

  const kind = $('#c-kind');
  kind.onchange = () => {
    $('#c-value-label').textContent = {
      percent: 'Value (%)', flat: 'Value (₹ off)', extra_credits: 'Extra questions',
    }[kind.value];
  };

  // Populate the product filter from the live catalogue so the codes can never
  // drift from what is actually on sale.
  api('/api/products').then(({ products }) => {
    $('#c-skus').innerHTML = (products || [])
      .map((p) => `<option value="${esc(p.sku)}">${esc(p.title)} — ${rupees(p.rupees)}</option>`)
      .join('');
  }).catch(() => {});

  $('#coupon-form').onsubmit = async (ev) => {
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
      // End of the chosen day, so a coupon marked "expires 31 Dec" works all
      // of 31 December rather than dying at midnight as it begins.
      expires_at: until ? `${until}T23:59:59` : null,
    };

    try {
      await api('/api/admin/coupons', { method: 'POST', body: JSON.stringify(body) });
      $('#coupon-form').reset();
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
  const box = $('#coupon-list');
  const { coupons } = await api('/api/admin/coupons');
  setCount('#c-coupons', coupons.filter((c) => c.active).length);

  if (!coupons.length) {
    box.innerHTML = '<p class="empty">No coupons yet.</p>';
    return;
  }

  box.innerHTML = coupons.map((c) => `
    <div class="row" data-id="${c.id}">
      <div class="row-main">
        <div class="row-title">
          <code class="code">${esc(c.code)}</code>
          <span class="pill ${c.active ? 'delivered' : 'off'}">${c.active ? 'live' : 'paused'}</span>
          &middot; ${esc(describe(c))}
        </div>
        <div class="row-sub">
          ${esc(c.applies_to === 'all' ? 'all products' : c.applies_to)}
          &middot; used ${c.redemptions}${c.max_redemptions ? ` / ${c.max_redemptions}` : ''}
          &middot; ${c.max_per_user} per customer
          ${c.expires_at ? `&middot; expires ${esc(c.expires_at.slice(0, 10))}` : ''}
          ${c.total_discount_paise ? `&middot; <span class="muted">${rupees(c.total_discount_paise / 100)} given away</span>` : ''}
        </div>
      </div>
      <div class="row-act">
        <button class="ghost sm" data-act="toggle">${c.active ? 'Pause' : 'Resume'}</button>
        <button class="danger sm" data-act="delete">Delete</button>
      </div>
    </div>`).join('');

  $$('#coupon-list .row').forEach((row) => {
    const id = Number(row.dataset.id);
    const c = coupons.find((x) => x.id === id);

    row.querySelector('[data-act="toggle"]').onclick = async () => {
      await api(`/api/admin/coupons/${id}`, {
        method: 'PATCH', body: JSON.stringify({ active: !c.active }),
      });
      await loadCoupons();
    };

    row.querySelector('[data-act="delete"]').onclick = async () => {
      if (!confirm(`Delete ${c.code}? Coupons that have been used are paused instead, `
        + 'so the redemption history survives.')) return;
      try {
        await api(`/api/admin/coupons/${id}`, { method: 'DELETE' });
      } catch (e) { alert(e.message); }
      await loadCoupons();
    };
  });
}

boot().catch((e) => showGate('Something went wrong', e.message, false));
