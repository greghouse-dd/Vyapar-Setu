/* =========================================================
   VYAPAR SETU — Main Application Controller
   v2.0 — Backend API Integration Layer
   ========================================================= */

// ── API Configuration ─────────────────────────────────────────────────────────
window.API_BASE = 'http://localhost:8001';
window.BACKEND_ONLINE = false;

// ── API Client Helper ─────────────────────────────────────────────────────────
window.ApiClient = (function() {
  async function request(method, path, body = null, opts = {}) {
    const url = `${window.API_BASE}${path}`;
    const fetchOpts = {
      method,
      headers: { 'Content-Type': 'application/json', ...(opts.headers || {}) },
      signal: AbortSignal.timeout(30_000),
    };
    if (body && method !== 'GET') {
      fetchOpts.body = JSON.stringify(body);
    }
    const resp = await fetch(url, fetchOpts);
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: resp.statusText }));
      throw new Error(err.detail || `HTTP ${resp.status}`);
    }
    return resp.json();
  }

  // Convenience methods
  const get  = (path, opts)       => request('GET',  path, null, opts);
  const post = (path, body, opts) => request('POST', path, body, opts);

  // Download binary file (docx / zip)
  async function download(path, body, filename) {
    const resp = await fetch(`${window.API_BASE}${path}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    if (!resp.ok) throw new Error(`Download failed: ${resp.statusText}`);
    const blob = await resp.blob();
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename || 'download';
    a.click();
    URL.revokeObjectURL(a.href);
  }

  return { get, post, download };
})();

// ── Backend Status Checker ────────────────────────────────────────────────────
async function checkBackendStatus() {
  const indicator = document.getElementById('backend-status');
  try {
    await window.ApiClient.get('/health');
    window.BACKEND_ONLINE = true;
    if (indicator) {
      indicator.textContent = '● Backend Online';
      indicator.style.color = '#4ade80';
      indicator.title = `Connected to ${window.API_BASE}`;
    }
  } catch (_) {
    window.BACKEND_ONLINE = false;
    if (indicator) {
      indicator.textContent = '● Demo Mode';
      indicator.style.color = '#fbbf24';
      indicator.title = `Backend offline — start with: cd website/backend && uvicorn main:app --port 8001 --reload`;
    }
  }
}

// ── Main App Controller ───────────────────────────────────────────────────────
window.AppController = (function() {
  const data = window.VYAPAR_DATA;
  let currentTab = 'ledger-view';

  function updateHeaderStats() {
    const totalBudget = data.CONTRACTS.reduce((sum, c) => sum + c.maxBudget, 0);
    const totalCommitted = data.CONTRACTS.reduce((sum, c) => sum + c.committedSpend, 0);
    const ratio = ((totalCommitted / totalBudget) * 100).toFixed(0);

    const container = document.getElementById('headstats');
    if (container) {
      container.innerHTML = `
        <span><b>${data.CONTRACTS.length}</b><span class="lbl">Active Contracts</span></span>
        <span><b>₹${(totalBudget / 1e7).toFixed(1)} Cr</b><span class="lbl">Total Budget</span></span>
        <span><b>${ratio}%</b><span class="lbl">Committed</span></span>
      `;
    }
  }

  function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <span>${type === 'success' ? '✓' : type === 'danger' ? '✕' : 'ℹ'}</span>
      <div>${message}</div>
    `;

    container.appendChild(toast);
    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transition = 'opacity 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }

  function switchTab(tabId) {
    currentTab = tabId;

    document.querySelectorAll('.tab-btn').forEach(btn => {
      if (btn.dataset.tab === tabId) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    document.querySelectorAll('.tab-view').forEach(view => {
      if (view.id === tabId) {
        view.classList.add('active');
        initializeView(tabId, view);
      } else {
        view.classList.remove('active');
      }
    });
  }

  function initializeView(tabId, wrapper) {
    if (wrapper.dataset.initialized === 'true' && tabId === 'ledger-view') {
      window.LedgerModule?.init(wrapper);
      return;
    }

    wrapper.dataset.initialized = 'true';

    switch (tabId) {
      case 'ledger-view':     window.LedgerModule?.init(wrapper);       break;
      case 'forecast-view':   window.ForecastModule?.init(wrapper);     break;
      case 'optimizer-view':  window.OptimizerModule?.init(wrapper);    break;
      case 'pooling-view':    window.PoolingModule?.init(wrapper);      break;
      case 'idle-view':       window.IdleAdvisorModule?.init(wrapper);  break;
      case 'vernacular-view': window.VernacularModule?.init(wrapper);   break;
      case 'tender-view':     window.TenderModule?.init(wrapper);       break;
      case 'backtest-view':   window.BacktestModule?.init(wrapper);     break;
    }
  }

  function bindEvents() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    document.getElementById('btn-new-contract')?.addEventListener('click', () => {
      switchTab('ledger-view');
      window.LedgerModule?.openModal(null);
    });

    document.getElementById('btn-voice-qa-head')?.addEventListener('click', () => {
      switchTab('vernacular-view');
    });

    document.getElementById('btn-tender-head')?.addEventListener('click', () => {
      switchTab('tender-view');
    });

    // Backend status refresh on click
    document.getElementById('backend-status')?.addEventListener('click', async () => {
      await checkBackendStatus();
      showToast(
        window.BACKEND_ONLINE
          ? `✅ Backend connected at ${window.API_BASE}`
          : `⚠️ Backend offline — run: uvicorn main:app --port 8001 --reload`,
        window.BACKEND_ONLINE ? 'success' : 'info'
      );
    });
  }

  function init() {
    updateHeaderStats();
    bindEvents();
    switchTab('ledger-view');
    // Check backend status after a short delay
    setTimeout(checkBackendStatus, 800);
  }

  return { init, switchTab, showToast, updateHeaderStats };
})();

document.addEventListener('DOMContentLoaded', () => {
  window.AppController.init();
});
