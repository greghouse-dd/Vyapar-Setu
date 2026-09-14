/* =========================================================
   VYAPAR SETU — Main Application Controller
   ========================================================= */

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

    // Update Tab Buttons
    document.querySelectorAll('.tab-btn').forEach(btn => {
      if (btn.dataset.tab === tabId) {
        btn.classList.add('active');
      } else {
        btn.classList.remove('active');
      }
    });

    // Update Views
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
      // Re-render ledger list/detail to reflect additions
      window.LedgerModule?.init(wrapper);
      return;
    }

    wrapper.dataset.initialized = 'true';

    switch (tabId) {
      case 'ledger-view':
        window.LedgerModule?.init(wrapper);
        break;
      case 'forecast-view':
        window.ForecastModule?.init(wrapper);
        break;
      case 'optimizer-view':
        window.OptimizerModule?.init(wrapper);
        break;
      case 'pooling-view':
        window.PoolingModule?.init(wrapper);
        break;
      case 'idle-view':
        window.IdleAdvisorModule?.init(wrapper);
        break;
      case 'vernacular-view':
        window.VernacularModule?.init(wrapper);
        break;
      case 'tender-view':
        window.TenderModule?.init(wrapper);
        break;
      case 'backtest-view':
        window.BacktestModule?.init(wrapper);
        break;
    }
  }

  function bindEvents() {
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        switchTab(btn.dataset.tab);
      });
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
  }

  function init() {
    updateHeaderStats();
    bindEvents();
    switchTab('ledger-view');
  }

  return { init, switchTab, showToast, updateHeaderStats };
})();

document.addEventListener('DOMContentLoaded', () => {
  window.AppController.init();
});
